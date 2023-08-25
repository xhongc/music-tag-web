import requests
import base64

from applications.task.services.acoust import AcoustidClient
from applications.task.services.kugou import KugouClient
from applications.task.services.kuwo import KuwoClient
from applications.task.services.qm import QQMusicApi
from applications.task.services.smart_tag_resource import SmartTagClient
from applications.task.utils import timestamp_to_dt
from applications.utils.send import send


class MusicResource:
    def __init__(self, info):
        self.resource = self.get_resource(info)

    def get_resource(self, info):
        if info == "netease":
            return NetEaseMusicClient()
        elif info == "migu":
            return MiGuMusicClient()
        elif info == "qmusic":
            return QmusicClient()
        elif info == "kugou":
            return KugouClient()
        elif info == "kuwo":
            return KuwoClient()
        elif info == "acoustid":
            return AcoustidClient()
        elif info == "smart_tag":
            return SmartTagClient()
        raise Exception("暂不支持该音乐平台")

    def fetch_lyric(self, song_id):
        return self.resource.fetch_lyric(song_id)

    def fetch_id3_by_title(self, title):
        return self.resource.fetch_id3_by_title(title)


class NetEaseMusicClient:
    BASE_URL = "https://music.163.com/"

    def fetch_lyric(self, song_id):
        data = send({"url": self.BASE_URL + "api/song/lyric?lv=-1&kv=-1&tv=-1",
                     "params": {"id": song_id}}, "linuxapi").POST("")
        return data.json().get("lrc", {}).get("lyric")

    def fetch_id3_by_title(self, title):
        data = send({'s': title, 'type': '1', 'limit': '10', 'offset': '0'}).POST("weapi/cloudsearch/get/web")
        songs = data.json().get("result", {}).get("songs", [])
        for song in songs:
            artists = song.get("ar", [])
            album = song.get("al", {})
            if artists:
                artist = ",".join([artist.get("name", "") for artist in artists])
                artist_id = artists[0].get("id", "")
            else:
                artist = ""
                artist_id = ""
            year = song.get("publishTime", "")
            if year:
                year = timestamp_to_dt(year / 1000, "%Y")
            song["artist"] = artist
            song["artist_id"] = artist_id
            song["album"] = album.get("name", "")
            song["album_id"] = album.get("id", "")
            song["album_img"] = album.get("picUrl", {})
            song["year"] = year or ""
        return songs


class MiGuMusicClient:
    BASE_URL = "https://m.music.migu.cn/"
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0',
        'Referer': 'https://m.music.migu.cn/'
    }

    def fetch_lyric(self, song_id):
        url = f'https://music.migu.cn/v3/api/music/audioPlayer/getLyric?copyrightId={song_id}'
        res = requests.get(url, headers=self.header)
        return res.json()["lyric"]

    def fetch_id3_by_title(self, title):
        url = self.BASE_URL + f"migu/remoting/scr_search_tag?rows=10&type=2&keyword={title}&pgc=1"
        res = requests.get(url, headers=self.header)
        songs = res.json()["musics"]
        for song in songs:
            song["id"] = song['copyrightId']
            song["name"] = song['songName']
            song["artist"] = song['singerName']
            song["artist_id"] = song['singerId']
            song["album"] = song['albumName']
            song["album_id"] = song['albumId']
            song["album_img"] = song['cover']
            song["year"] = ""
        return songs


class QmusicClient:
    def fetch_lyric(self, song_id):
        a = QQMusicApi()
        res = a.getQQMusicMediaLyric(song_id)
        decoded_str = base64.b64decode(res.get("lyric", "")).decode("utf-8")
        return decoded_str

    def fetch_id3_by_title(self, title):
        a = QQMusicApi()
        songs = a.getQQMusicMatchSong(title)
        return songs
