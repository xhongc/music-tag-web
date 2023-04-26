"""
Documentation of Subsonic API can be found at http://www.subsonic.org/pages/api.jsp
"""
import datetime

from django.conf import settings
from django.utils import timezone
from rest_framework import exceptions
from rest_framework import permissions as rest_permissions
from rest_framework import response, viewsets
from rest_framework.decorators import action

from applications.music.models import Artist, Album, Attachment, Track, Playlist, TrackFavorite
from . import authentication, negotiation, serializers
from .filters import AlbumList2FilterSet
from .utils import handle_serve


class SubsonicViewSet(viewsets.GenericViewSet):
    content_negotiation_class = negotiation.SubsonicContentNegociation
    authentication_classes = [authentication.SubsonicAuthentication]
    permission_classes = [rest_permissions.IsAuthenticated]
    throttling_scopes = {"*": {"authenticated": "subsonic", "anonymous": "subsonic"}}

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def handle_exception(self, exc):
        # subsonic API sends 200 status code with custom error
        # codes in the payload
        mapping = {
            exceptions.AuthenticationFailed: (40, "Wrong username or password."),
            exceptions.NotAuthenticated: (10, "Required parameter is missing."),
        }
        payload = {"status": "failed"}
        if exc.__class__ in mapping:
            code, message = mapping[exc.__class__]
        else:
            return super().handle_exception(exc)
        payload["error"] = {"code": code, "message": message}

        return response.Response(payload, status=200)

    @action(detail=False, methods=["get", "post"], permission_classes=[])
    def ping(self, request, *args, **kwargs):
        data = {"status": "ok", "version": "1.16.0"}
        return response.Response(data, status=200)

    @action(
        detail=False,
        methods=["get", "post"],
        url_name="get_license",
        permission_classes=[],
        url_path="getLicense",
    )
    def get_license(self, request, *args, **kwargs):
        now = timezone.now()
        data = {
            "status": "ok",
            "version": "1.16.0",
            "type": "music-tag-web",
            "musicTagVersion": "1.0.1",
            "license": {
                "valid": "true",
                "email": "valid@valid.license",
                "licenseExpires": now + datetime.timedelta(days=365),
            },
        }
        return response.Response(data, status=200)

    @action(
        detail=False,
        methods=["get", "post"],
        url_name="get_artists",
        url_path="getArtists",
    )
    def get_artists(self, request, *args, **kwargs):

        artists = Artist.objects.all()
        data = serializers.GetArtistsSerializer(artists).data
        payload = {"artists": data}

        return response.Response(payload, status=200)

    @action(
        detail=False,
        methods=["get", "post"],
        url_name="get_cover_art",
        url_path="getCoverArt",
    )
    def get_cover_art(self, request, *args, **kwargs):
        """ 返回封面图片"""
        data = request.GET or request.POST
        the_id = data.get("id", "")
        if not the_id:
            return response.Response(
                {"error": {"code": 10, "message": "cover art ID must be specified."}}
            )

        if the_id.startswith("al-"):
            try:
                album_id = int(the_id.replace("al-", ""))
                album = Album.objects.get(pk=album_id)
            except (TypeError, ValueError, Album.DoesNotExist):
                return response.Response(
                    {"error": {"code": 70, "message": "cover art not found."}}
                )
            attachment = album.attachment_cover
        elif the_id.startswith("ar-"):
            try:
                artist_id = int(the_id.replace("ar-", ""))
                artist = Artist.objects.get(pk=artist_id)
            except (TypeError, ValueError, Album.DoesNotExist):
                return response.Response(
                    {"error": {"code": 70, "message": "cover art not found."}}
                )
            attachment = artist.attachment_cover
        elif the_id.startswith("at-"):
            try:
                attachment_id = the_id.replace("at-", "")
                attachment = Attachment.objects.get(id=attachment_id)
            except (TypeError, ValueError, Album.DoesNotExist):
                return response.Response(
                    {"error": {"code": 70, "message": "cover art not found."}}
                )
        else:
            return response.Response(
                {"error": {"code": 70, "message": "cover art not found."}}
            )
        if not attachment:
            return response.Response(
                {"error": {"code": 70, "message": "cover art not found."}}
            )
        # if not attachment.file:
        #     common_tasks.fetch_remote_attachment(attachment)
        cover = attachment.file
        mapping = {"nginx": "X-Accel-Redirect", "apache2": "X-Sendfile"}
        # path = get_file_path_view(cover)
        file_header = mapping["nginx"]
        # let the proxy set the content-type
        r = response.Response({}, content_type='')
        r[file_header] = cover.url

        return r

    @action(
        detail=False,
        methods=["get", "post"],
        url_name="get_artist",
        url_path="getArtist",
    )
    def get_artist(self, request, *args, **kwargs):
        data = request.GET or request.POST

        artist = Artist.objects.filter(pk=data["id"]).first()
        if not artist:
            return response.Response(
                {"error": {"code": 70, "message": "Artist not found."}}
            )
        data = serializers.GetArtistSerializer(artist).data
        payload = {"artist": data}

        return response.Response(payload, status=200)

    @action(
        detail=False, methods=["get", "post"], url_name="get_song", url_path="getSong"
    )
    def get_song(self, request, *args, **kwargs):
        data = request.GET or request.POST

        track = Track.objects.filter(pk=data["id"]).first()
        if not track:
            return response.Response(
                {"error": {"code": 70, "message": "Track not found."}}
            )
        data = serializers.GetSongSerializer(track).data
        payload = {"song": data}

        return response.Response(payload, status=200)

    @action(
        detail=False,
        methods=["get", "post"],
        url_name="get_artist_info2",
        url_path="getArtistInfo2",
    )
    def get_artist_info2(self, request, *args, **kwargs):
        payload = {"artist-info2": {}}

        return response.Response(payload, status=200)

    @action(
        detail=False, methods=["get", "post"], url_name="get_album", url_path="getAlbum"
    )
    def get_album(self, request, *args, **kwargs):
        req_data = request.GET or request.POST

        album = Album.objects.filter(pk=req_data["id"]).first()
        if not album:
            return response.Response(
                {"error": {"code": 70, "message": "Album not found."}}
            )
        data = serializers.GetAlbumSerializer(album).data
        payload = {"album": data}
        return response.Response(payload, status=200)

    @action(detail=False, methods=["get", "post"], url_name="stream", url_path="stream")
    def stream(self, request, *args, **kwargs):
        data = request.GET or request.POST
        track = Track.objects.filter(pk=data["id"]).first()
        max_bitrate = data.get("maxBitRate")
        try:
            max_bitrate = min(max(int(max_bitrate), 0), 320) or None
        except (TypeError, ValueError):
            max_bitrate = None

        if max_bitrate:
            max_bitrate = max_bitrate * 1000

        _format = data.get("format") or None
        if max_bitrate and not _format:
            _format = settings.SUBSONIC_DEFAULT_TRANSCODING_FORMAT
        elif _format == "raw":
            _format = None

        return handle_serve(
            track=track,
            user=request.user,
            _format=_format,
            max_bitrate=max_bitrate,
            # Subsonic clients don't expect 302 redirection unfortunately,
            # So we have to proxy media files
            proxy_media=True,
        )

    @action(
        detail=False, methods=["get", "post"], url_name="scrobble", url_path="scrobble"
    )
    def scrobble(self, request, *args, **kwargs):
        """
        回传正在播放的音乐信息 ?id=1&albumId=1&submission=true
        """
        return response.Response({})

    @action(
        detail=False,
        methods=["get", "post"],
        url_name="get_genres",
        url_path="getGenres",
    )
    def get_genres(self, request, *args, **kwargs):

        data = {
            "genres": {"genre": [{
                "songCount": 0,
                "albumCount": 0,
                "value": "Rock",
            }]}
        }
        return response.Response(data)

    @action(
        detail=False,
        methods=["get", "post"],
        url_name="get_album_list2",
        url_path="getAlbumList2",
    )
    def get_album_list2(self, request, *args, **kwargs):
        data = request.GET or request.POST

        queryset = Album.objects.order_by("artist__name")
        filterset = AlbumList2FilterSet(data, queryset=queryset)
        queryset = filterset.qs
        al_type = data.get("type", "alphabeticalByArtist")
        if al_type == "alphabeticalByArtist":
            queryset = queryset.order_by("artist__name")
        elif al_type == "random":
            queryset = queryset.order_by("?")
        elif al_type == "alphabeticalByName" or not al_type:
            queryset = queryset.order_by("name")
        elif al_type == "recent" or not al_type:
            # 最近播放的
            queryset = queryset.exclude(max_year=0).order_by("-max_year")
        elif al_type == "newest" or not al_type:
            queryset = queryset.order_by("-created_at")
        elif al_type == "frequent":
            # 播放量最多的
            queryset = queryset.order_by("-plays_count")
        elif al_type == "byGenre" and data.get("genre"):
            genre = data.get("genre")
            queryset = queryset.filter(genre__name=genre)
        elif al_type == "byYear":
            try:
                boundaries = [
                    int(data.get("fromYear", 0)),
                    int(data.get("toYear", 99999999)),
                ]

            except (TypeError, ValueError):
                return response.Response(
                    {
                        "error": {
                            "code": 10,
                            "message": "Invalid fromYear or toYear parameter",
                        }
                    }
                )
            # because, yeah, the specification explicitly state that fromYear can be greater
            # than toYear, to indicate reverse ordering…
            # http://www.subsonic.org/pages/api.jsp#getAlbumList2
            from_year = min(boundaries)
            to_year = max(boundaries)
            queryset = queryset.filter(
                max_year__gte=from_year, max_year__lte=to_year
            )
            if boundaries[0] <= boundaries[1]:
                queryset = queryset.order_by("max_year")
            else:
                queryset = queryset.order_by("-max_year")
        try:
            offset = int(data["offset"])
        except (TypeError, KeyError, ValueError):
            offset = 0

        try:
            size = int(data["size"])
        except (TypeError, KeyError, ValueError):
            size = 50

        size = min(size, 500)
        queryset = queryset[offset: offset + size]
        data = {"albumList2": {"album": serializers.get_album_list2_data(queryset)}}
        return response.Response(data)

    @action(
        detail=False,
        methods=["get", "post"],
        url_name="get_indexes",
        url_path="getIndexes",
    )
    def get_indexes(self, request, *args, **kwargs):
        artists = Artist.objects.all()

        data = serializers.GetArtistsSerializer(artists).data
        payload = {"indexes": data}

        return response.Response(payload, status=200)

    @action(
        detail=False,
        methods=["get", "post"],
        url_name="get_music_folders",
        url_path="getMusicFolders",
    )
    def get_music_folders(self, request, *args, **kwargs):
        """
        获取音乐文件夹
        """
        data = {"musicFolders": {"musicFolder": [{"id": 1, "name": "Music"}]}}
        return response.Response(data, status=200)

    @action(
        detail=False,
        methods=["get", "post"],
        url_name="get_music_directory",
        url_path="getMusicDirectory",
    )
    def get_music_directory(self, request, *args, **kwargs):
        """
        获取音乐文件夹
        """
        data = {
            "directory": {
                "id": "10",
                "parent": "1",
                "name": "ABBA",
                "starred": "2013-11-02T12:30:00",
                "child": [
                    {
                        "id": "11",
                        "parent": "10",
                        "title": "Arrival",
                        "artist": "ABBA",
                        "isDir": "true",
                        "coverArt": "22"
                    },
                    {
                        "id": "12",
                        "parent": "10",
                        "title": "Super Trouper",
                        "artist": "ABBA",
                        "isDir": "true",
                        "coverArt": "23"
                    }
                ]
            }
        }
        return response.Response(data)

    @action(
        detail=False,
        methods=["get", "post"],
        url_name="get_playlists",
        url_path="getPlaylists",
    )
    def get_playlists(self, request, *args, **kwargs):
        req_data = request.GET or request.POST
        print(req_data)
        qs = Playlist.objects.filter(user=request.user).all()
        data = {
            "playlists": {"playlist": [serializers.get_playlist_data(p) for p in qs]}
        }
        return response.Response(data)

    @action(
        detail=False,
        methods=["get", "post"],
        url_name="get_starred2",
        url_path="getStarred2",
    )
    def get_starred2(self, request, *args, **kwargs):
        favorites = request.user.track_favorites.all()
        data = {"starred2": {"song": serializers.get_starred_tracks_data(favorites)}}
        return response.Response(data)

    @action(detail=False, methods=["get", "post"], url_name="star", url_path="star")
    def star(self, request, *args, **kwargs):
        req_data = request.GET or request.POST
        track = Track.objects.filter(id=req_data.get("id")).first()
        if not track:
            return response.Response({"error": {"code": 70, "message": "Track not found."}})
        TrackFavorite.add(user=request.user, track=track)
        return response.Response({"status": "ok"})

    @action(detail=False, methods=["get", "post"], url_name="unstar", url_path="unstar")
    def unstar(self, request, *args, **kwargs):
        req_data = request.GET or request.POST
        track = Track.objects.filter(id=req_data.get("id")).first()
        if not track:
            return response.Response({"error": {"code": 70, "message": "Track not found."}})
        request.user.track_favorites.filter(track=track).delete()
        return response.Response({"status": "ok"})

    @action(
        detail=False,
        methods=["get", "post"],
        url_name="get_scan_status",
        url_path="getScanStatus",
    )
    def get_scan_status(self, request, *args, **kwargs):
        data = {
            "scanStatus": {
                "scanning": False,
                "count": "5422"
            }
        }
        return response.Response(data)

    @action(
        detail=False,
        methods=["get", "post"],
        url_name="start_scan",
        url_path="startScan",
    )
    def start_scan(self, request, *args, **kwargs):
        data = {
            "scanStatus": {
                "scanning": True,
                "count": "5411"
            }
        }
        return response.Response(data)
