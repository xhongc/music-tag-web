from applications.task.utils import match_score, match_artist
from concurrent.futures import ThreadPoolExecutor

from component import music_tag


class SmartTagClient:

    def fetch_lyric(self, song_id):
        pass

    def run(self, resource, title):
        from applications.task.services.music_resource import MusicResource
        songs = MusicResource(resource).fetch_id3_by_title(title)
        for song in songs:
            song["resource"] = resource
        return songs

    def fetch_id3_by_title(self, info):

        title = info["title"]
        full_path = info["full_path"]
        file = music_tag.load_file(full_path)
        artist = file["artist"].value or ""
        album = file["album"].value or ""
        order_songs = []
        max_score = 0
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = pool.map(self.run, ["qmusic", "netease", "migu", "kugou"], [title] * 4)

        for songs in results:
            for song in songs:
                title_score = match_score(title, song["name"])
                artist_score = match_artist(artist if artist else title, song["artist"])
                album_score = match_score(album if album else title, song["album"])
                if artist and artist_score == 0:
                    artist_score = -2
                # 标题包含艺术家信息
                if not artist and artist_score >= 1:
                    if title_score >= 1:
                        title_score = 2
                song["score"] = title_score + artist_score + album_score
                max_score = max(max_score, song["score"])
                if title_score == 0:
                    continue
                order_songs.append(song)
        order_songs.sort(key=lambda x: x["score"], reverse=True)
        return order_songs[:15]
