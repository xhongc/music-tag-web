import random
import requests
import hashlib
from typing import Optional
import datetime

default_headers = {
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    'Referer': 'http://www.kuwo.cn/'
}


def generate_kw_token(length=32):
    charset = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return ''.join(random.choices(charset, k=length))


class KuwoClient:
    def __init__(self):
        self.token = generate_kw_token()
        self.cross = self.sha1_and_md5(self.token)

    def sha1_and_md5(self, token):
        sha1_hash = hashlib.sha1()
        sha1_hash.update(token.encode('utf-8'))
        hash_value = sha1_hash.hexdigest()
        cross = hashlib.md5(hash_value.encode('utf-8')).hexdigest()
        return cross

    def _api_request(self, url, params):
        headers = default_headers.copy()
        headers['Cross'] = self.cross
        headers['Cookie'] = f'Hm_token={self.token}'
        return requests.get(url, params=params, headers=headers, timeout=5.0).json()

    def fetch_lyric(self, song_id):
        url = f'http://kuwo.cn/newh5/singles/songinfoandlrc?musicId={song_id}'
        params = {
            'mid': song_id,
            'type': 'music',
            'httpsStatus': 1,
            'plat': 'web_www'
        }
        resp = self._api_request(url, params)
        lrclist = resp.get("data", {}).get("lrclist", [])
        lyric = ""
        try:
            for line in lrclist:
                seconds = int(float(line.get("time", "0")))
                m, s = divmod(seconds, 60)
                h, m = divmod(m, 60)
                time_format = "%d:%02d:%02d" % (h, m, s)
                content = line.get("lineLyric", "")
                lyric += f"[{time_format}]{content}\n"
        except Exception as e:
            print(e)
        return lyric

    def fetch_id3_by_title(self, title):
        url = 'http://www.kuwo.cn/api/www/search/searchMusicBykeyWord'
        params = {
            'key': title,
            'pn': 1,
            'rn': 10,
            'httpsStatus': 1
        }
        resp = self._api_request(url, params)
        songs = resp.get('data', {}).get('list', None)
        for song in songs:
            song["id"] = song['rid']
            song["name"] = song['name']
            song["artist"] = song['artist']
            song["artist_id"] = song['artistid']
            song["album"] = song['album']
            song["album_id"] = song['albumid']
            song["album_img"] = song['albumpic']
            song["year"] = ""
        return songs


if __name__ == '__main__':
    kw = KuwoClient()
    # print(kw.fetch_id3_by_title("我想"))
    print(kw.fetch_lyric("22822909"))
