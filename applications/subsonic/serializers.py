import collections
import time

from django.db.models import Count, functions, Sum
from rest_framework import serializers

from applications.music.models import Track, Artist, Album
from applications.subsonic.utils import get_type_from_ext


class PassSerializers(serializers.Serializer):
    u = serializers.CharField(required=True)
    p = serializers.CharField(required=False)
    s = serializers.CharField(required=False)
    t = serializers.CharField(required=False)


def to_subsonic_date(date):
    """
    Subsonic expects this kind of date format: 2012-04-17T19:55:49.000Z
    """

    if not date:
        return

    return date.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def get_valid_filepart(s):
    """
    Return a string suitable for use in a file path. Escape most non-ASCII
    chars, and truncate the string to a suitable length too.
    """
    max_length = 50
    keepcharacters = " ._()[]-+"
    final = "".join(
        c if c.isalnum() or c in keepcharacters else "_" for c in s
    ).rstrip()
    return final[:max_length]


def get_track_path(track, suffix):
    parts = []
    parts.append(get_valid_filepart(track.artist.name))
    if track.album:
        parts.append(get_valid_filepart(track.album.name))
    track_part = get_valid_filepart(track.name) + "." + suffix
    if track.track_number:
        track_part = f"{track.track_number} - {track_part}"
    parts.append(track_part)
    return "/".join(parts)


def get_artist_data(artist_values):
    return {
        "id": artist_values["id"],
        "name": artist_values["name"],
        "albumCount": artist_values["_albums_count"],
        "coverArt": "ar-{}".format(artist_values["id"]),
    }


def get_folder_data(artist_values):
    return {
        "id": artist_values["uid"],
        "name": artist_values["name"],
        "albumCount": 0,
        "coverArt": "",
    }


def get_folder_child(folder):
    return {
        "id": folder.uid,
        "parent": folder.parent_id,
        "title": folder.name,
        "artist": "",
        "isDir": True if folder.file_type == "folder" else False,
        "coverArt": "",
    }


class GetArtistsSerializer(serializers.Serializer):
    def to_representation(self, queryset):
        payload = {"ignoredArticles": "", "index": []}
        queryset = queryset.order_by(functions.Lower("name"))
        queryset = queryset.annotate(_albums_count=Count("albums"))
        values = queryset.values("id", "_albums_count", "name")

        first_letter_mapping = collections.defaultdict(list)
        for artist in values:
            if artist["name"]:
                first_letter_mapping[artist["name"][0].upper()].append(artist)

        for letter, artists in sorted(first_letter_mapping.items()):
            letter_data = {
                "name": letter,
                "artist": [get_artist_data(v) for v in artists],
            }
            payload["index"].append(letter_data)
        return payload


class GetFolderSerializer(serializers.Serializer):
    def to_representation(self, queryset):
        payload = {"ignoredArticles": "", "index": []}
        queryset = queryset.order_by(functions.Lower("name"))
        values = queryset.values("id", "name", "uid")

        first_letter_mapping = collections.defaultdict(list)
        for artist in values:
            if artist["name"]:
                first_letter_mapping[artist["name"][0].upper()].append(artist)

        for letter, artists in sorted(first_letter_mapping.items()):
            letter_data = {
                "name": letter,
                "artist": [get_folder_data(v) for v in artists],
            }
            payload["index"].append(letter_data)
        return payload


class GetArtistSerializer(serializers.Serializer):
    def to_representation(self, artist):

        albums = Album.objects.filter(artist=artist).prefetch_related("tracks")
        payload = {
            "id": artist.pk,
            "name": artist.name,
            "albumCount": albums.count(),
            "album": [],
        }
        if artist.attachment_cover_id:
            payload["coverArt"] = f"ar-{artist.id}"
        for album in albums:
            album_data = {
                "id": album.id,
                "artistId": artist.id,
                "name": album.name,
                "artist": artist.name,
                "created": to_subsonic_date(album.created_at),
                "songCount": album.tracks.count(),
                "duration": sum([t.duration or 0 for t in album.tracks.all()])
            }
            if album.attachment_cover_id:
                album_data["coverArt"] = f"al-{album.id}"
            if album.max_year:
                album_data["year"] = album.max_year
            payload["album"].append(album_data)
        return payload


def get_track_data(track):
    """
    subsonic expects this kind of data:
    """
    album = track.album
    artist = track.artist
    data = {
        "id": track.pk,
        "isDir": "false",
        "title": track.name,
        "album": album.name if album else "",
        "artist": artist.name,
        "track": track.track_number or 1,
        "discNumber": track.disc_number or 1,
        "contentType": track.mimetype or get_type_from_ext(track.path),
        "suffix": track.suffix or "",
        "path": get_track_path(track, track.suffix or "mp3"),
        "duration": track.duration or 0,
        "created": to_subsonic_date(track.created_at),
        "albumId": album.pk if album else "",
        "artistId": album.artist.pk if album else track.artist.pk,
        "type": "music",
    }
    if album and album.attachment_cover_id:
        data["coverArt"] = f"al-{album.id}"
    if track.bit_rate:
        data["bitrate"] = int(track.bit_rate / 1000)
    if track.size:
        data["size"] = track.size
    if album and album.max_year:
        data["year"] = album.max_year
    else:
        data["year"] = track.created_at.year
    return data


def get_album2_data(album):
    """
    subsonic expects this kind of data:
    """
    payload = {
        "id": album.id,
        "artistId": album.artist_id,
        "name": album.name,
        "artist": album.artist.name if album.artist else "",
        "created": to_subsonic_date(album.created_at),
        "duration": album.duration,
        "playCount": album.plays_count,
        "songCount": album.song_count,
    }
    if album.attachment_cover_id:
        payload["coverArt"] = f"al-{album.id}"
    if album.genre:
        payload["genre"] = album.genre.name
    if album.max_year:
        payload["year"] = album.max_year
    return payload


def get_song_list_data(tracks):
    songs = []
    for track in tracks:
        track_data = get_track_data(track)
        songs.append(track_data)
    return songs


class GetAlbumSerializer(serializers.Serializer):
    def to_representation(self, album):
        payload = get_album2_data(album)

        tracks = album.tracks.select_related("album__artist")
        payload["song"] = get_song_list_data(tracks)
        return payload


class GetSongSerializer(serializers.Serializer):
    def to_representation(self, track):
        return get_track_data(track)


def get_starred_data(favorites):
    by_track_id = {}
    by_album_id = {}
    by_artist_id = {}
    song_data = []
    artist_data = []
    album_data = []
    for f in favorites:
        if f.track_id:
            by_track_id[f.track_id] = f
        elif f.album_id:
            by_album_id[f.album_id] = f
        elif f.artist_id:
            by_artist_id[f.artist_id] = f
    if by_track_id:
        tracks = (
            Track.objects.filter(pk__in=by_track_id.keys())
                .select_related("album__artist")
        )
        for t in tracks:
            td = get_track_data(t)
            td["starred"] = to_subsonic_date(by_track_id[t.pk].creation_date)
            song_data.append(td)
    if by_artist_id:
        artists = Artist.objects.filter(pk__in=by_artist_id.keys()).annotate(_albums_count=Count("albums")) \
            .values("id", "name", "_albums_count")
        for a in artists:
            ad = get_artist_data(a)
            ad["starred"] = to_subsonic_date(by_artist_id[a["id"]].creation_date)
            artist_data.append(ad)
    if by_album_id:
        albums = Album.objects.filter(pk__in=by_album_id.keys()).select_related("artist").prefetch_related("tracks")
        for a in albums:
            ad = get_album2_data(a)
            ad["starred"] = to_subsonic_date(by_album_id[a.pk].creation_date)
            album_data.append(ad)
    return {"song": song_data, "album": album_data, "artist": artist_data}


def get_album_list2_data(albums):
    albums = albums.select_related("artist").select_related("genre")
    return [get_album2_data(a) for a in albums]


def get_playlist_data(playlist):
    return {
        "id": playlist.pk,
        "name": playlist.name,
        "owner": playlist.user.username,
        "public": False,
        "songCount": 0,
        "duration": 0,
        "created": to_subsonic_date(playlist.creation_date),
    }


def get_playlist_detail_data(playlist):
    data = get_playlist_data(playlist)
    qs = (
        playlist.playlist_tracks.select_related("track__album__artist")
            .order_by("index")
    )
    data["entry"] = []
    for plt in qs:
        td = get_track_data(plt.track)
        data["entry"].append(td)
    return data


def get_folders(user):
    return [
        # Dummy folder ID to match what is returned in the getMusicFolders endpoint
        # cf https://dev.funkwhale.audio/funkwhale/funkwhale/issues/624
        {"id": 1, "name": "Music"}
    ]


def get_user_detail_data(user):
    return {
        "username": user.username,
        "email": user.email,
        "scrobblingEnabled": "true",
        "adminRole": "false",
        "settingsRole": "false",
        "commentRole": "false",
        "podcastRole": "true",
        "coverArtRole": "false",
        "shareRole": "false",
        "uploadRole": "true",
        "downloadRole": "true",
        "playlistRole": "true",
        "streamRole": "true",
        "jukeboxRole": "true",
        "folder": [f["id"] for f in get_folders(user)],
    }


def get_genre_data(tag, _tracks_count_map):
    return {
        "songCount": _tracks_count_map.get(tag.pk, 0),
        "albumCount": getattr(tag, "_albums_count", 0),
        "value": tag.name,
    }


def get_channel_data(channel, uploads):
    data = {
        "id": str(channel.uuid),
        "url": channel.get_rss_url(),
        "title": channel.artist.name,
        "description": channel.artist.description.as_plain_text
        if channel.artist.description
        else "",
        "coverArt": f"at-{channel.artist.attachment_cover.uuid}"
        if channel.artist.attachment_cover
        else "",
        "originalImageUrl": channel.artist.attachment_cover.url
        if channel.artist.attachment_cover
        else "",
        "status": "completed",
    }
    if uploads:
        data["episode"] = [
            get_channel_episode_data(upload, channel.uuid) for upload in uploads
        ]

    return data


def get_channel_episode_data(upload, channel_id):
    return {
        "id": str(upload.uuid),
        "channelId": str(channel_id),
        "streamId": upload.track.id,
        "title": upload.track.name,
        "description": upload.track.description.as_plain_text
        if upload.track.description
        else "",
        "coverArt": f"at-{upload.track.attachment_cover.uuid}"
        if upload.track.attachment_cover
        else "",
        "isDir": "false",
        "year": upload.track.creation_date.year,
        "publishDate": upload.track.creation_date.isoformat(),
        "created": upload.track.creation_date.isoformat(),
        "genre": "Podcast",
        "size": upload.size if upload.size else "",
        "duration": upload.duration if upload.duration else "",
        "bitrate": upload.bitrate / 1000 if upload.bitrate else "",
        "contentType": upload.mimetype or "audio/mpeg",
        "suffix": upload.extension or "mp3",
        "status": "completed",
    }
