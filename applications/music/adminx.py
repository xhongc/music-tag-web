# -*- coding: utf-8 -*-
import xadmin
from .models import Album, Track, Artist, Genre, Attachment, Playlist, TrackFavorite, Folder


class AlbumAdmin(object):
    list_display = (
        'id',
        'name',
        'artist',
        'all_artist_ids',
        'max_year',
        'song_count',
        'plays_count',
        'duration',
        'genre',
        'created_at',
        'updated_at',
        'accessed_date',
        'full_text',
        'size',
        'comment',
        'paths',
        'description',
        'attachment_cover',
    )
    list_filter = (
        'created_at',
        'updated_at',
        'accessed_date',
        'external_info_updated_at',
    )
    search_fields = ('name',)
    date_hierarchy = 'created_at'
    list_per_page = 10


class TrackAdmin(object):
    list_display = (
        'id',
        'name',
        'path',
        'album',
        'artist',
        'has_cover_art',
        'track_number',
        'disc_number',
        'plays_count',
        'year',
        'size',
        'suffix',
        'mimetype',
        'duration',
        'bit_rate',
        'genre',
        'created_at',
        'updated_at',
        'accessed_date',
        'full_text',
    )
    list_filter = (
        'has_cover_art',
        'created_at',
        'updated_at',
        'accessed_date',
    )
    search_fields = ('name',)
    date_hierarchy = 'created_at'
    list_per_page = 10


class ArtistAdmin(object):
    list_display = (
        'id',
        'name',
        'album_count',
        'full_text',
        'song_count',
        'size',
        'mbz_artist_id',
        'attachment_cover',
        'similar_artists',
        'external_url',
        'external_info_updated_at',
    )
    list_filter = ('attachment_cover', 'external_info_updated_at')
    search_fields = ('name',)

    list_per_page = 10


class GenreAdmin(object):
    list_display = ('id', 'name')
    search_fields = ('name',)


class AttachmentAdmin(object):
    list_display = (
        'id',
        'url',
        'creation_date',
        'last_fetch_date',
        'size',
        'mimetype',
        'file',
    )
    list_filter = ('creation_date', 'last_fetch_date')


class PlaylistAdmin(object):
    list_display = (
        'id',
        'name',
        'user',
        'creation_date',
        'modification_date',
        'privacy_level',
    )
    list_filter = ('user', 'creation_date', 'modification_date')
    search_fields = ('name',)


class TrackFavoriteAdmin(object):
    list_display = ('id', 'creation_date', 'user', 'track')
    list_filter = ('creation_date', 'user', 'track')


class FolderAdmin(object):
    list_display = (
        'id',
        'name',
        'path',
        'created_at',
        'last_scan_time',
        'file_type',
        'uid',
        'parent_id',
    )
    list_filter = ('created_at', 'last_scan_time', "file_type", "state")
    search_fields = ('name',)
    date_hierarchy = 'created_at'
    list_per_page = 10


xadmin.site.register(Album, AlbumAdmin)
xadmin.site.register(Track, TrackAdmin)
xadmin.site.register(Artist, ArtistAdmin)
xadmin.site.register(Genre, GenreAdmin)
xadmin.site.register(Attachment, AttachmentAdmin)
xadmin.site.register(Playlist, PlaylistAdmin)
xadmin.site.register(TrackFavorite, TrackFavoriteAdmin)
xadmin.site.register(Folder, FolderAdmin)
