from django.contrib import admin

from applications.navidrome.models import Album, MediaFile, Artist, Genre
from component.drf.adminx_expand import MultiDBModelAdmin


class AlbumAdmin(MultiDBModelAdmin):
    list_display = ["id", "name", "artist", "paths"]


class MediaFileAdmin(MultiDBModelAdmin):
    list_display = ["id", "album", "title", "artist", "path"]


class ArtistAdmin(MultiDBModelAdmin):
    list_display = ["id", "name", "song_count"]


class GenreAdmin(MultiDBModelAdmin):
    list_display = ["id", "name"]


admin.site.register(Album, AlbumAdmin)
admin.site.register(MediaFile, MediaFileAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Genre, GenreAdmin)
