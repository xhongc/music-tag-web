import base64
import os

import music_tag
from django.utils.decorators import method_decorator
from django.views.decorators.gzip import gzip_page
from rest_framework.decorators import action

from applications.task.serialziers import FileListSerializer, Id3Serializer, UpdateId3Serializer, \
    FetchId3ByTitleSerializer, FetchLlyricSerializer
from applications.task.services.music_resource import MusicResource
from applications.utils.send import send
from component.drf.viewsets import GenericViewSet
from PIL import Image


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
        return FileListSerializer

    @action(methods=['POST'], detail=False)
    def file_list(self, request, *args, **kwargs):
        validate_data = self.is_validated_data(request.data)
        file_path = validate_data['file_path']
        file_path_list = file_path.split('/')
        try:
            data = os.listdir(file_path)
        except FileNotFoundError:
            return self.failure_response(msg="文件夹不存在")
        children_data = []
        allow_type = ["flac", "mp3", "ape", "wav", "aiff", "wv", "tta", "mp4", "m4a", "ogg", "mpc",
                      "opus", "wma", "dsf", "dff"]
        for index, each in enumerate(data, 1):
            file_type = each.split(".")[-1]
            if os.path.isdir(f"{file_path}/{each}"):
                children_data.append({
                    "id": index,
                    "name": each,
                    "title": each,
                    "icon": "icon-folder",
                    "children": []
                })
                continue
            if file_type not in allow_type:
                continue
            children_data.append({
                "id": index,
                "name": each,
                "title": each,
                "icon": "icon-monitors"
            })
        res_data = [
            {
                "name": file_path_list[-1],
                "title": file_path_list[-1],
                "expanded": True,
                "id": 0,
                "children": children_data
            }
        ]
        return self.success_response(data=res_data)

    @action(methods=['POST'], detail=False)
    def music_id3(self, request, *args, **kwargs):
        validate_data = self.is_validated_data(request.data)
        file_path = validate_data['file_path']
        file_name = validate_data['file_name']
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
        }
        return self.success_response(data=res_data)

    @action(methods=['POST'], detail=False)
    def update_id3(self, request, *args, **kwargs):
        validate_data = self.is_validated_data(request.data)
        music_id3_info = validate_data['music_id3_info']
        for each in music_id3_info:
            f = music_tag.load_file(each["file_full_path"])
            f["title"] = each["title"]
            f["artist"] = each["artist"]
            f["album"] = each["album"]
            f["genre"] = each["genre"]
            f["year"] = each["year"]
            f["lyrics"] = each["lyrics"]
            f["comment"] = each["comment"]
            if each.get("album_img", None):
                img_data = send().GET(each["album_img"])
                if img_data.status_code == 200:
                    f['artwork'] = img_data.content
                    # f['artwork'] = f['artwork'].first.raw_thumbnail([128, 128])
            f.save()
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
