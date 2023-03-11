import base64
import os

import music_tag
from rest_framework.decorators import action

from applications.task.serialziers import FileListSerializer, Id3Serializer, UpdateId3Serializer, \
    FetchId3ByTitleSerializer, FetchLlyricSerializer
from applications.task.utils import timestamp_to_dt
from applications.utils.send import send
from component.drf.viewsets import GenericViewSet
from django_vue_cli.settings import BASE_URL


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
        data = os.listdir(file_path)
        children_data = []
        allow_type = ["flac", "mp3", "ape", "wav", "aiff", "wv", "tta", "mp4", "m4a", "ogg", "mpc",
                      "opus", "wma", "dsf", "dff"]
        for each in data:
            file_type = each.split(".")[-1]
            if file_type not in allow_type:
                continue
            children_data.append({
                "name": each,
                "title": each
            })
        res_data = [
            {
                "name": file_path_list[-1],
                "title": file_path_list[-1],
                "expanded": True,
                "id": 1,
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
            bs64_img = base64.b64encode(artwork[0].raw).decode()

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
                    f['artwork'].first.raw_thumbnail([64, 64])
            f.save()
        return self.success_response()

    @action(methods=['POST'], detail=False)
    def fetch_lyric(self, request, *args, **kwargs):
        validate_data = self.is_validated_data(request.data)
        song_id = validate_data["song_id"]
        try:
            data = send({"url": BASE_URL + "api/song/lyric?lv=-1&kv=-1&tv=-1",
                         "params": {"id": song_id}}, "linuxapi").POST("")
            lyric = data.json().get("lrc", {}).get("lyric")
        except Exception as e:
            lyric = f"未找到歌词 {e}"
        return self.success_response(data=lyric)

    @action(methods=['POST'], detail=False)
    def fetch_id3_by_title(self, request, *args, **kwargs):
        validate_data = self.is_validated_data(request.data)
        title = validate_data["title"]
        data = send({'s': title, 'type': '1', 'limit': '10', 'offset': '0'}).POST("weapi/cloudsearch/get/web")
        songs = data.json().get("result", {}).get("songs", [])
        formated_songs = []
        for song in songs:
            artists = song.get("ar", [])
            album = song.get("al", {})
            if artists:
                artist = artists[0].get("name", "")
                artist_id = artists[0].get("id", "")
            else:
                artist = ""
                artist_id = ""
            year = song.get("publishTime", 0)
            if year:
                year = timestamp_to_dt(year / 1000, "%Y")
            formated_songs.append({
                "id": song["id"],
                "name": song["name"],
                "artist": artist,
                "artist_id": artist_id,
                "album": album.get("name", ""),
                "album_id": album.get("id", ""),
                "album_img": album.get("picUrl", {}),
                "year": year
            })
        return self.success_response(data=formated_songs)
