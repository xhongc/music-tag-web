import random
import urllib.parse
from datetime import datetime

from django.conf import settings
from rest_framework.response import Response

from applications.music.models import Track, Album
from applications.subsonic.constants import EXTENSION_TO_MIMETYPE


def get_type_from_ext(path):
    extension = path.split(".")[-1]
    return EXTENSION_TO_MIMETYPE.get(extension)


def get_content_disposition(filename):
    filename = f"filename*=UTF-8''{urllib.parse.quote(filename)}"
    return f"attachment; {filename}"


def handle_serve(
        track, user, _format=None, max_bitrate=None, proxy_media=True, download=False):
    # we update the accessed_date
    now = datetime.now()
    track.accessed_date = now
    track.save(update_fields=["accessed_date"])
    file_path = track.path.replace(str(settings.BASE_DIR), "").encode("utf-8")
    mt = track.mimetype

    if mt:
        response = Response(content_type=mt)
    else:
        response = Response()
    mapping = {"nginx": "X-Accel-Redirect", "apache2": "X-Sendfile"}
    file_header = mapping[settings.REVERSE_PROXY_TYPE]
    response[file_header] = file_path
    if download:
        filename = track.name
        response["Content-Disposition"] = get_content_disposition(filename)
    if mt:
        response["Content-Type"] = mt

    return response


def mock_track():
    alnum = Album.objects.order_by("?").first()

    for i in range(150):
        Track.objects.create(
            name="test2",
            album_id=alnum.id
        )
        print(i)
