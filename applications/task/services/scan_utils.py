from applications.music.models import Folder, Attachment
import music_tag
from django.conf import settings
import time
from applications.music.models import Folder, Track, Album, Artist, Genre
from applications.subsonic.constants import AUDIO_EXTENSIONS_AND_MIMETYPE, COVER_TYPE
from django_vue_cli.celery_app import app
import os
import uuid
from django.core.files.base import ContentFile
import io
from django.core.files import File  # you need this somewhere
from PIL import Image


class MusicInfo:
    def __init__(self, folder):
        if isinstance(folder, Folder):
            self.file = music_tag.load_file(folder.path)
            self.path = folder.path
            self.folder_name = folder.name
            self.file_type = folder.file_type
            self.parent_id = folder.parent_id
        else:
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
        return self.file['#length'].value

    @property
    def size(self):
        return os.path.getsize(self.path)

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
            return self.file['artwork'].value
        except Exception:
            return ""

    def to_dict(self):
        return {
            "year": self.year,
            "comment": self.comment,
            "lyrics": self.lyrics,
            "duration": self.duration,
            "size": self.size,
            "suffix": self.suffix,
            "bit_rate": self.bit_rate,
            "track_number": self.track_number,
            "disc_number": self.disc_number,
            "name": self.title,
        }


class ScanMusic:
    def __init__(self, path):
        self.path = path
        self.artist_map = dict(Artist.objects.values_list("name", "id"))
        self.album_map = dict(Album.objects.values_list("full_text", "id"))
        genre_map = dict(Genre.objects.values_list("name", "id"))
        self.genre_map = {k.upper(): v for k, v in genre_map.items()}

    def get_scan_list(self):
        music_list = Folder.objects.filter(file_type="music", state__in=["none", "updated"]).all()
        return music_list

    def get_or_create_artist(self, music_info):
        artist_name = music_info.artist_name
        if artist_name not in self.artist_map:
            artist = Artist.objects.create(**{
                "name": artist_name,
            })
            self.artist_map[artist_name] = artist.id
        return self.artist_map[artist_name]

    def get_or_create_album(self, music_info):
        album_name = music_info.album_name
        artist_name = music_info.artist_name
        year = music_info.year
        genre = music_info.genre
        comment = music_info.comment
        full_text = f"{album_name}"

        if full_text not in self.album_map:
            artist_id = self.artist_map[artist_name]
            album = Album.objects.create(**{
                "name": album_name,
                "artist_id": artist_id,
                "max_year": year,
                "genre_id": self.genre_map[genre],
                "comment": comment,
                "full_text": full_text
            })
            self.album_map[full_text] = album.id
        else:
            album = Album.objects.filter(id=self.album_map[full_text]).first()
        return album

    def get_or_create_genre(self, music_info):
        genre_name = music_info.genre

        if genre_name not in self.genre_map:
            genre = Genre.objects.create(**{
                "name": genre_name,
            })
            self.genre_map[genre_name] = genre.id
        return self.genre_map[genre_name]

    def get_or_create_attachment(self, music_info, album):
        if album.attachment_cover is None:
            folder = Folder.objects.filter(file_type="image", parent_id=music_info.parent_id,
                                           name__startswith="cover.").first()
            if folder:
                image_path = folder.path
                with open(image_path, "rb") as f:
                    image_data = f.read()
                    at = Attachment.objects.create(**{
                        "size": len(image_data),
                        "mimetype": f"image/{folder.name.split('.')[-1]}",
                    })
                    at.file.save(f"{album.name}.jpg", ContentFile(image_data), True)
                    album.attachment_cover = at
                    album.save()
            else:
                artwork = music_info.artwork
                if artwork:
                    at = Attachment.objects.create(**{
                        "size": len(artwork.raw),
                        "mimetype": artwork.mime,
                    })
                    at.file.save(f"{album.name}.jpg", ContentFile(artwork.raw), True)

                    album.attachment_cover = at
                    album.save()

    def update_or_create_track(self, music_info, album_id, artist_id, genre_id):
        path = music_info.path
        default_data = music_info.to_dict()
        default_data["album_id"] = album_id
        default_data["artist_id"] = artist_id
        default_data["genre_id"] = genre_id
        track, _ = Track.objects.update_or_create(path=path, defaults=default_data)
        return track

    def scan(self):
        folder_list = self.get_scan_list()
        for folder in folder_list:
            try:
                music_info = MusicInfo(folder)
                artist_id = self.get_or_create_artist(music_info)
                genre_id = self.get_or_create_genre(music_info)
                album = self.get_or_create_album(music_info)
                self.get_or_create_attachment(music_info, album)
                self.update_or_create_track(music_info, album_id=album.id, artist_id=artist_id, genre_id=genre_id)
                folder.state = "scanned"
                folder.save()
            except Exception as e:
                print(e)
                continue
