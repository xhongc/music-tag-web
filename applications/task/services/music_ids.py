import base64
import os

import music_tag


class MusicIDS:
    def __init__(self, folder):
        self.file = music_tag.load_file(folder)
        self.path = folder

    @property
    def album_name(self):
        album_name = self.file["album"].value
        album_name = album_name.replace(" ", "")
        if not album_name:
            album_name = "未知专辑"
        return self.file["album"].value

    @property
    def album(self):
        album_name = self.file["album"].value
        album_name = album_name.replace(" ", "")
        if not album_name:
            album_name = "未知专辑"
            return album_name
        return self.file["album"].value

    @property
    def album_type(self):
        try:
            if self.file.tag_format in ["FLAC", "OGG"]:
                return self.file.mfile.tags.get("RELEASETYPE")[0]
            else:
                return self.file.mfile.tags.get("TXXX:MUSICBRAINZALBUMTYPE").text[0]
        except Exception:
            return ""

    @property
    def album_artist(self):
        return self.file["albumartist"].value

    @property
    def artist_name(self):
        return self.file["artist"].value

    @property
    def artist(self):
        return self.file["artist"].value

    @property
    def year(self):
        try:
            year = self.file["year"].value
        except Exception:
            return 0
        try:
            year = int(year)
        except Exception:
            year_list = year.split("-")
            if year_list and year_list[0]:
                try:
                    return int(year_list[0].replace(" ", ""))
                except Exception:
                    return 0
        return year

    @property
    def genre(self):
        genre = self.file["genre"].value
        if genre:
            genre = genre.upper()
        else:
            genre = "未知"
        return genre

    @property
    def comment(self):
        return self.file["comment"].value

    @property
    def lyrics(self):
        return self.file["lyrics"].value

    @property
    def duration(self):
        return round(self.file['#length'].value, 2)

    @property
    def size(self):
        return round(os.path.getsize(self.path) / 1024 / 1024, 2)

    @property
    def suffix(self):
        return self.file['#codec'].value

    @property
    def bit_rate(self):
        return self.file['#bitrate'].value

    @property
    def track_number(self):
        try:
            return self.file['tracknumber'].value
        except Exception:
            return 1

    @property
    def disc_number(self):
        try:
            return self.file['discnumber'].value
        except Exception:
            return 1

    @property
    def title(self):
        return self.file['title'].value

    @property
    def artwork(self):
        try:
            bs64_img = ""
            artwork = self.file['artwork'].values
            if artwork:
                zip_img = artwork[0].raw_thumbnail([128, 128])
                bs64_img = base64.b64encode(zip_img).decode()
            return "data:image/jpeg;base64," + bs64_img
        except Exception:
            return ""

    @property
    def file_name(self):
        return os.path.basename(self.path)

    def to_dict(self):
        return {
            "year": self.year,
            "comment": self.comment,
            "lyrics": self.lyrics,
            "duration": self.duration,
            "size": self.size,
            "bit_rate": self.bit_rate,
            "tracknumber": self.track_number,
            "discnumber": self.disc_number,
            "artwork": self.artwork,
            "title": self.title or self.file_name.split(".")[0],
            "artist": self.artist,
            "album": self.album,
            "album_type": self.album_type,
            "genre": self.genre,
            "filename": self.file_name,
            "albumartist": self.album_artist,
        }
