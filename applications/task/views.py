import base64
import copy
import json
import os
import random

import music_tag
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.gzip import gzip_page
from rest_framework.decorators import action

from applications.music.models import Artist, Track, Album
from applications.task.serialziers import FileListSerializer, Id3Serializer, UpdateId3Serializer, \
    FetchId3ByTitleSerializer, FetchLlyricSerializer, BatchUpdateId3Serializer, MergeArtistSerializer
from applications.task.services.music_resource import MusicResource
from applications.task.services.update_ids import update_music_info
from applications.task.tasks import full_scan_folder, scan_music_id3, scan, clear_music
from component.drf.viewsets import GenericViewSet
from django_vue_cli.celery_app import app as celery_app


@method_decorator(gzip_page, name="dispatch")
class TaskViewSets(GenericViewSet):
    def get_serializer_class(self):
        if self.action == "file_list":
            return FileListSerializer
        elif self.action == "music_id3":
            return Id3Serializer
        elif self.action == "update_id3":
            return UpdateId3Serializer
        elif self.action == "fetch_id3_by_title":
            return FetchId3ByTitleSerializer
        elif self.action == "fetch_lyric":
            return FetchLlyricSerializer
        elif self.action == "batch_update_id3":
            return BatchUpdateId3Serializer
        elif self.action in ["merge_artist", "merge_album"]:
            return MergeArtistSerializer
        return FileListSerializer

    @action(methods=['POST'], detail=False)
    def file_list(self, request, *args, **kwargs):
        """文件列表"""
        validate_data = self.is_validated_data(request.data)
        file_path = validate_data['file_path']
        file_path_list = file_path.split('/')
        try:
            data = os.scandir(file_path)
        except FileNotFoundError:
            return self.failure_response(msg="文件夹不存在")
        children_data = []
        allow_type = ["flac", "mp3", "ape", "wav", "aiff", "wv", "tta", "mp4", "m4a", "ogg", "mpc",
                      "opus", "wma", "dsf", "dff"]
        frc_map = {}
        for index, entry in enumerate(data, 1):
            each = entry.name
            file_type = each.split(".")[-1]
            file_name = ".".join(each.split(".")[:-1])
            if os.path.isdir(f"{file_path}/{each}"):
                children_data.append({
                    "id": index,
                    "name": each,
                    "title": each,
                    "icon": "icon-folder",
                    "children": []
                })
                continue
            if file_type in ["lrc", "txt"]:
                frc_map[file_name] = each
            if file_type not in allow_type:
                continue
            if file_name in frc_map:
                icon = "icon-script-files"
            else:
                icon = "icon-script-file"
            children_data.append({
                "id": index,
                "name": each,
                "title": each,
                "icon": icon
            })
        res_data = [
            {
                "name": file_path_list[-1],
                "title": file_path_list[-1],
                "expanded": True,
                "id": 0,
                "children": children_data,
                "icon": "icon-folder",
            }
        ]
        return self.success_response(data=res_data)

    @action(methods=['POST'], detail=False)
    def music_id3(self, request, *args, **kwargs):
        """获取音乐id3信息"""
        validate_data = self.is_validated_data(request.data)
        file_path = validate_data['file_path']
        file_name = validate_data['file_name']
        file_type = file_name.split(".")[-1]
        if file_type in ["lrc", "txt"]:
            return self.success_response()
        file_path = file_path.rstrip('/')
        sub_path = file_path.split('/')[-1]
        if sub_path == file_name:
            return self.success_response()
        file_title = file_name.split('.')[0]
        f = music_tag.load_file(f"{file_path}/{file_name}")
        artwork = f["artwork"].values
        bs64_img = ""
        if artwork:
            zip_img = artwork[0].raw_thumbnail([128, 128])

            bs64_img = base64.b64encode(zip_img).decode()
        res_data = {
            "title": f["title"].value or file_title,
            "artist": f["artist"].value,
            "album": f["album"].value,
            "genre": f["genre"].value,
            "year": f["year"].value,
            "lyrics": f["lyrics"].value,
            "comment": f["comment"].value,
            "artwork": "data:image/jpeg;base64," + bs64_img,
            "filename": file_name
        }
        return self.success_response(data=res_data)

    @action(methods=['POST'], detail=False)
    def update_id3(self, request, *args, **kwargs):
        """更新音乐id3信息"""
        validate_data = self.is_validated_data(request.data)
        music_id3_info = validate_data['music_id3_info']
        update_music_info(music_id3_info)
        return self.success_response()

    @action(methods=['POST'], detail=False)
    def batch_update_id3(self, request, *args, **kwargs):
        """批量更新音乐id3信息"""
        validate_data = self.is_validated_data(request.data)
        full_path = validate_data['file_full_path']
        select_data = validate_data['select_data']
        music_info = validate_data['music_info']
        music_id3_info = []
        for data in select_data:
            if data.get('icon') == 'icon-folder':
                file_full_path = f"{full_path}/{data.get('name')}"
                data = os.scandir(file_full_path)
                allow_type = ["flac", "mp3", "ape", "wav", "aiff", "wv", "tta", "mp4", "m4a", "ogg", "mpc",
                              "opus", "wma", "dsf", "dff"]
                for index, entry in enumerate(data, 1):
                    each = entry.name
                    file_type = each.split(".")[-1]
                    if file_type not in allow_type:
                        continue
                    music_info.update({
                        "file_full_path": f"{file_full_path}/{each}",
                        "filename": each
                    })
                    music_id3_info.append(copy.deepcopy(music_info))
            else:
                music_info.update({
                    "file_full_path": f"{full_path}/{data.get('name')}",
                    "filename": data.get('name')
                })
                music_id3_info.append(copy.deepcopy(music_info))
        update_music_info(music_id3_info)
        return self.success_response()

    @action(methods=['POST'], detail=False)
    def fetch_lyric(self, request, *args, **kwargs):
        validate_data = self.is_validated_data(request.data)
        resource = validate_data["resource"]
        song_id = validate_data["song_id"]
        try:
            lyric = MusicResource(resource).fetch_lyric(song_id)
        except Exception as e:
            lyric = f"未找到歌词 {e}"
        return self.success_response(data=lyric)

    @action(methods=['POST'], detail=False)
    def fetch_id3_by_title(self, request, *args, **kwargs):
        validate_data = self.is_validated_data(request.data)
        resource = validate_data["resource"]

        title = validate_data["title"]
        songs = MusicResource(resource).fetch_id3_by_title(title)
        return self.success_response(data=songs)

    @action(methods=["get"], detail=False)
    def clear_celery(self, request, *args, **kwargs):
        active_tasks = celery_app.control.inspect().active()
        try:
            active_tasks_data = list(active_tasks.values())[0]
        except Exception:
            return self.success_response()
        for task in active_tasks_data:
            celery_app.control.revoke(task["id"], terminate=True)
        celery_app.control.purge()
        return self.success_response()

    @action(methods=["get"], detail=False)
    def active_queue(self, request, *args, **kwargs):
        active_tasks = celery_app.control.inspect().active()
        try:
            active_tasks_data = list(active_tasks.values())[0]
        except Exception:
            return self.success_response()
        return self.success_response(data=active_tasks_data)

    @action(methods=['GET'], detail=False)
    def task1(self, request, *args, **kwargs):
        scan.delay()
        return self.success_response()

    @action(methods=['GET'], detail=False)
    def task2(self, request, *args, **kwargs):
        clear_music()
        return self.success_response()

    @action(methods=['GET'], detail=False)
    def full_scan_folder(self, request, *args, **kwargs):
        full_scan_folder.delay()
        return self.success_response()

    @action(methods=['POST'], detail=False)
    def merge_artist(self, request, *args, **kwargs):
        validate_data = self.is_validated_data(request.data)
        full_text = validate_data["full_text"]
        artist_list = Artist.objects.filter(full_text=full_text).all()
        first_artist = artist_list[0]
        first_artist.name = full_text
        first_artist.save()
        with transaction.atomic():
            for artist in artist_list[1:]:
                Track.objects.filter(artist=artist).update(artist=first_artist)
                Album.objects.filter(artist=artist).update(artist=first_artist)
                Artist.objects.filter(id=artist.id).delete()
        return self.success_response()

    @action(methods=['POST'], detail=False)
    def merge_album(self, request, *args, **kwargs):
        validate_data = self.is_validated_data(request.data)
        full_text = validate_data["full_text"]
        album_list = Album.objects.filter(full_text=full_text).all()
        first_album = album_list[0]
        first_album.name = full_text
        first_album.save()
        with transaction.atomic():
            for album in album_list[1:]:
                Track.objects.filter(album=album).update(album=first_album)
                Album.objects.filter(id=album.id).delete()
        return self.success_response()

    @action(methods=['GET'], detail=False)
    def import_music(self, request, *args, **kwargs):
        with open("/Users/macbookair/Downloads/艺术家.json","r") as f:
            a = json.load(f)
        for each in a["objects"]:
            Artist.objects.create(**{
                "name": each["name"],
            })
        return self.success_response()

    @action(methods=['GET'], detail=False)
    def import_music2(self, request, *args, **kwargs):
        with open("/Users/macbookair/Downloads/专辑.json", "r") as f:
            a = json.load(f)
        for each in a["objects"]:
            Album.objects.create(**{
                "name": each["专辑名称"],
                "artist_id": random.randint(11, 485)
            })
        return self.success_response()