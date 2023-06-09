"""
Documentation of Subsonic API can be found at http://www.subsonic.org/pages/api.jsp
"""
import datetime
import time

from django.conf import settings
from django.db.models import Count, F
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.gzip import gzip_page
from rest_framework import exceptions
from rest_framework import permissions as rest_permissions
from rest_framework import response, viewsets
from rest_framework.decorators import action

from applications.music.models import Artist, Album, Attachment, Track, Playlist, TrackFavorite, Genre, Folder, \
    PlaylistTrack
from . import authentication, negotiation, serializers
from .serializers import PassSerializers, get_folder_child, get_song_list_data
from .utils import handle_serve, get_query, order_for_search, try_int


@method_decorator(gzip_page, name="dispatch")
class SubsonicViewSet(viewsets.GenericViewSet):
    content_negotiation_class = negotiation.SubsonicContentNegociation
    authentication_classes = [authentication.SubsonicAuthentication]
    permission_classes = [rest_permissions.IsAuthenticated]
    throttling_scopes = {"*": {"authenticated": "subsonic", "anonymous": "subsonic"}}
    serializer_class = PassSerializers

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
        """获取歌手列表"""
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
        """单个歌手信息"""
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
        detail=False,
        methods=["get", "post"],
        url_name="get_top_songs",
        url_path="getTopSongs",
    )
    def get_top_songs(self, request, *args, **kwargs):
        data = request.GET or request.POST
        artist_name = data.get("artist", "")
        count = int(data.get("count", 10))
        tracks = Track.objects.filter(artist__name=artist_name).select_related("album__artist").order_by(
            "-plays_count")[:count]
        data = get_song_list_data(tracks)
        payload = {"topSongs": data}

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
        """单个专辑信息"""
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
        """音乐流式传输"""
        data = request.GET or request.POST
        try:
            track_id = int(data["id"])
            track = Track.objects.filter(pk=track_id).first()
        except Exception:
            folder = Folder.objects.filter(uid=data["id"]).first()
            track = Track.objects.filter(path=folder.path).first()
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
        data = request.GET or request.POST
        track_id = data.get("id")
        album_id = data.get("albumId")
        if track_id:
            Track.objects.filter(pk=track_id).update(plays_count=F("plays_count") + 1,
                                                     accessed_date=datetime.datetime.now())
        if album_id:
            Album.objects.filter(pk=album_id).update(plays_count=F("plays_count") + 1,
                                                     accessed_date=datetime.datetime.now())
        else:
            Album.objects.filter(tracks__id=track_id).update(plays_count=F("plays_count") + 1,
                                                             accessed_date=datetime.datetime.now())
        return response.Response({})

    @action(
        detail=False,
        methods=["get", "post"],
        url_name="get_genres",
        url_path="getGenres",
    )
    def get_genres(self, request, *args, **kwargs):
        queryset = Genre.objects.annotate(_albums_count=Count("albums")).order_by("name")
        _tracks_count_map = dict(
            Genre.objects.annotate(_tracks_count=Count("tracks")).values_list("id", "_tracks_count"))
        data = {
            "genres": {"genre": [serializers.get_genre_data(tag, _tracks_count_map) for tag in queryset]}
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
        queryset = Album.objects.all()
        al_type = data.get("type", "alphabeticalByArtist")
        if al_type == "alphabeticalByArtist":
            queryset = queryset.order_by("artist__name")
        elif al_type == "random":
            queryset = queryset.order_by("?")
        elif al_type == "alphabeticalByName" or not al_type:
            queryset = queryset.order_by("name")
        elif al_type == "recent" or not al_type:
            queryset = queryset.order_by("-accessed_date")
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
        url_name="get_album_list",
        url_path="getAlbumList",
    )
    def get_album_list(self, request, *args, **kwargs):
        data = request.GET or request.POST

        queryset = Album.objects.all()
        al_type = data.get("type", "alphabeticalByArtist")
        if al_type == "alphabeticalByArtist":
            queryset = queryset.order_by("artist__name")
        elif al_type == "random":
            queryset = queryset.order_by("?")
        elif al_type == "alphabeticalByName" or not al_type:
            queryset = queryset.order_by("name")
        elif al_type == "recent" or not al_type:
            # todo最近播放的
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

        data = {"albumList": {"album": serializers.get_album_list2_data(queryset)}}
        return response.Response(data)

    @action(
        detail=False,
        methods=["get", "post"],
        url_name="get_indexes",
        url_path="getIndexes",
    )
    def get_indexes(self, request, *args, **kwargs):
        root_node = Folder.objects.filter(parent_id__isnull=True).first()
        if not root_node:
            return response.Response({"indexes": {}}, status=200)
        folders = Folder.objects.filter(parent_id=root_node.uid).all()
        data = serializers.GetFolderSerializer(folders).data
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
        root_node = Folder.objects.filter(parent_id__isnull=True).first()
        if not root_node:
            data = {"musicFolders": {"musicFolder": [{"id": 1, "name": "music"}]}}
            return response.Response(data, status=200)

        data = {"musicFolders": {"musicFolder": [{"id": root_node.uid, "name": "music"}]}}
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
        data = request.GET or request.POST
        folder_uid = data.get("id")
        try:
            parent_node = Folder.objects.filter(uid=folder_uid).first()
        except Exception:
            return response.Response({
                "directory": {
                    "id": folder_uid,
                    "parent": folder_uid,
                    "name": folder_uid,
                    "starred": "2013-11-02T12:30:00",
                    "child": []
                }
            }, status=200)
        if not parent_node:
            return response.Response({
                "directory": {
                    "id": folder_uid,
                    "parent": folder_uid,
                    "name": folder_uid,
                    "starred": "2013-11-02T12:30:00",
                    "child": []
                }
            }, status=200)

        folders = Folder.objects.filter(parent_id=folder_uid).all()
        child_data = [get_folder_child(i) for i in folders]
        data = {
            "directory": {
                "id": folder_uid,
                "parent": parent_node.parent_id,
                "name": parent_node.name,
                "starred": "2013-11-02T12:30:00",
                "child": child_data
            }
        }
        return response.Response(data)

    @action(
        detail=False,
        methods=["get", "post"],
        url_name="create_playlist",
        url_path="createPlaylist",
    )
    def create_playlist(self, request, *args, **kwargs):
        data = request.GET or request.POST
        name = data.get("name", "")
        create_playlist = True
        play_list_id = data.get("playlistId", "")
        if name and play_list_id:
            return response.Response(
                {
                    "error": {
                        "code": 10,
                        "message": "You can only supply either a playlistId or name, not both.",
                    }
                }
            )
        if play_list_id:
            playlist = request.user.playlists.get(pk=play_list_id)
            create_playlist = False
            if not name and not playlist:
                return response.Response(
                    {
                        "error": {
                            "code": 10,
                            "message": "A valid playlist ID or name must be specified.",
                        }
                    }
                )
        if create_playlist:
            playlist = request.user.playlists.create(name=name)
        ids = []
        for i in data.getlist("songId"):
            try:
                ids.append(int(i))
            except (TypeError, ValueError):
                pass
        if ids:
            tracks = Track.objects.filter(pk__in=ids)
            by_id = {t.id: t for t in tracks}
            sorted_tracks = []
            for i in ids:
                try:
                    sorted_tracks.append(by_id[i])
                except KeyError:
                    pass
            if sorted_tracks:
                playlist.insert_many(sorted_tracks)
        playlist = request.user.playlists.annotate(_tracks_count=Count("playlist_tracks")).get(pk=playlist.pk)
        ret_data = {"playlist": serializers.get_playlist_detail_data(playlist)}
        return response.Response(ret_data)

    @action(
        detail=False,
        methods=["get", "post"],
        url_name="get_playlists",
        url_path="getPlaylists",
    )
    def get_playlists(self, request, *args, **kwargs):
        qs = Playlist.objects.filter(user=request.user)
        qs = qs.select_related("user")
        data = {
            "playlists": {"playlist": [serializers.get_playlist_data(p) for p in qs]}
        }
        return response.Response(data)

    @action(
        detail=False,
        methods=["get", "post"],
        url_name="get_playlist",
        url_path="getPlaylist",
    )
    def get_playlist(self, request, *args, **kwargs):
        data = request.GET or request.POST
        playlist_id = data.get("id")
        playlist = Playlist.objects.filter(pk=playlist_id).first()
        data = {"playlist": serializers.get_playlist_detail_data(playlist)}
        return response.Response(data)

    @action(
        detail=False,
        methods=["get", "post"],
        url_name="update_playlist",
        url_path="updatePlaylist",
    )
    def update_playlist(self, request, *args, **kwargs):
        data = request.GET or request.POST
        play_list_id = data.get("playlistId", "")
        playlist = Playlist.objects.filter(pk=play_list_id).first()
        new_name = data.get("name", "")
        if new_name:
            playlist.name = new_name
            playlist.save(update_fields=["name", "modification_date"])
        try:
            to_remove = int(data["songIndexToRemove"])
            plt = playlist.playlist_tracks.get(index=to_remove)
        except (TypeError, ValueError, KeyError):
            pass
        except PlaylistTrack.DoesNotExist:
            pass
        else:
            plt.delete(update_indexes=True)

        ids = []
        for i in data.getlist("songIdToAdd"):
            try:
                ids.append(int(i))
            except (TypeError, ValueError):
                pass
        if ids:
            tracks = Track.objects.filter(pk__in=ids)
            by_id = {t.id: t for t in tracks}
            sorted_tracks = []
            for i in ids:
                try:
                    sorted_tracks.append(by_id[i])
                except KeyError:
                    pass
            if sorted_tracks:
                playlist.insert_many(sorted_tracks)

        data = {"status": "ok"}
        return response.Response(data)

    @action(
        detail=False,
        methods=["get", "post"],
        url_name="delete_playlist",
        url_path="deletePlaylist",
    )
    def delete_playlist(self, request, *args, **kwargs):
        data = request.GET or request.POST
        playlist_id = data.get("id")
        Playlist.objects.filter(pk=playlist_id).delete()
        data = {"status": "ok"}
        return response.Response(data)

    @action(
        detail=False,
        methods=["get", "post"],
        url_name="get_starred2",
        url_path="getStarred2",
    )
    def get_starred2(self, request, *args, **kwargs):
        favorites = request.user.track_favorites.all()
        data = {"starred2": serializers.get_starred_data(favorites)}
        return response.Response(data)

    @action(detail=False, methods=["get", "post"], url_name="star", url_path="star")
    def star(self, request, *args, **kwargs):
        req_data = request.GET or request.POST
        track_id = req_data.get("id")
        album_id = req_data.get("albumId")
        artist_id = req_data.get("artistId")
        if track_id:
            track = Track.objects.filter(id=track_id).first()
            if not track:
                return response.Response({"error": {"code": 70, "message": "Track not found."}})
            TrackFavorite.add_track(user=request.user, track=track)
        elif album_id:
            album = Album.objects.filter(id=album_id).first()
            if not album:
                return response.Response({"error": {"code": 70, "message": "Album not found."}})
            TrackFavorite.add_album(user=request.user, album=album)
        elif artist_id:
            artist = Artist.objects.filter(id=artist_id).first()
            if not artist:
                return response.Response({"error": {"code": 70, "message": "Artist not found."}})
            TrackFavorite.add_artist(user=request.user, artist=artist)
        else:
            return response.Response(
                {"error": {"code": 10, "message": "Invalid id or albumId parameter"}}
            )

        return response.Response({"status": "ok"})

    @action(detail=False, methods=["get", "post"], url_name="unstar", url_path="unstar")
    def unstar(self, request, *args, **kwargs):
        req_data = request.GET or request.POST
        track_id = req_data.get("id")
        album_id = req_data.get("albumId")
        artist_id = req_data.get("artistId")
        if track_id:
            track = Track.objects.filter(id=track_id).first()
            if not track:
                return response.Response({"error": {"code": 70, "message": "Track not found."}})
            request.user.track_favorites.filter(track=track).delete()
        elif album_id:
            album = Album.objects.filter(id=album_id).first()
            if not album:
                return response.Response({"error": {"code": 70, "message": "Album not found."}})
            request.user.track_favorites.filter(album=album).delete()
        elif artist_id:
            artist = Artist.objects.filter(id=artist_id).first()
            if not artist:
                return response.Response({"error": {"code": 70, "message": "Artist not found."}})
            request.user.track_favorites.filter(artist=artist).delete()
        else:
            return response.Response(
                {"error": {"code": 10, "message": "Invalid id or albumId parameter"}}
            )
        return response.Response({"status": "ok"})

    @action(
        detail=False,
        methods=["get", "post"],
        url_name="set_rating",
        url_path="setRating",
    )
    def set_rating(self, request, *args, **kwargs):
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

    @action(
        detail=False, methods=["get", "post"], url_name="search3", url_path="search3"
    )
    def search3(self, request, *args, **kwargs):
        data = request.GET or request.POST
        query = str(data.get("query", "")).replace("*", "")
        conf = [
            {
                "subsonic": "artist",
                "search_fields": ["name"],
                "queryset": (
                    Artist.objects.with_albums_count().values(
                        "id", "_albums_count", "name"
                    )
                ),
                "serializer": lambda qs: [serializers.get_artist_data(a) for a in qs],
            },
            {
                "subsonic": "album",
                "search_fields": ["name"],
                "queryset": (
                    Album.objects.all()
                ),
                "serializer": serializers.get_album_list2_data,
            },
            {
                "subsonic": "song",
                "search_fields": ["name"],
                "queryset": (
                    Track.objects.select_related("album__artist")
                ),
                "serializer": serializers.get_song_list_data,
            },
        ]
        payload = {"searchResult3": {}}
        for c in conf:
            offset_key = "{}Offset".format(c["subsonic"])
            count_key = "{}Count".format(c["subsonic"])

            offset = try_int(data.get(offset_key, 0))
            size = try_int(data.get(count_key, 20))
            size = min(size, 500)

            queryset = c["queryset"]
            if query:
                queryset = c["queryset"].filter(get_query(query, c["search_fields"]))
            queryset = order_for_search(queryset, c["search_fields"][0])
            queryset = queryset[offset: offset + size]
            payload["searchResult3"][c["subsonic"]] = c["serializer"](queryset)
        return response.Response(payload)

    @action(
        detail=False,
        methods=["get", "post"],
        url_name="get_lyrics",
        url_path="getLyrics",
    )
    def get_lyrics(self, request, *args, **kwargs):
        data = request.GET or request.POST
        artist = data.get("artist")
        title = data.get("title")
        track = Track.objects.filter(artist__name=artist, name=title).first()
        payload = {"lyrics": {
            "artist": artist,
            "title": title,
            "value": track.lyrics if track else ""
        }}
        return response.Response(payload)
