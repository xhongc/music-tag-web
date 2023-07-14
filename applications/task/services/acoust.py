from component.mz.run import get_acoustid


class AcoustidClient:
    def fetch_id3_by_title(self, title):
        songs = []
        res = get_acoustid(title)
        for each in res:
            songs.append({
                "id": each[1],
                "name": each[2],
                "artist": each[3],
                "artist_id": "",
                "album": each[4],
                "album_id": "",
                "album_img": "",
                "year": "",
            })
        return songs

    def fetch_lyric(self, song_id):
        raise Exception("暂不支持该音乐平台")
