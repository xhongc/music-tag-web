import re
import urllib.parse
from datetime import datetime
from typing import Union

from django.conf import settings
from django.db.models import Q, functions
from rest_framework.response import Response

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


def normalize_query(
        query_string,
        findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
        normspace=re.compile(r"\s{2,}").sub,
):
    """Splits the query string in individual keywords, getting rid of unnecessary spaces
    and grouping quoted words together.
    Example:

    >>> normalize_query('  some random  words "with   quotes  " and   spaces')
    ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

    """
    return [normspace(" ", (t[0] or t[1]).strip()) for t in findterms(query_string)]


def get_query(query_string, search_fields):
    """Returns a query, that is a combination of Q objects. That combination
    aims to search keywords within a model by testing the given search fields.

    """
    query = None  # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None  # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = Union[or_query, q]
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


def order_for_search(qs, field):
    """
    When searching, it's often more useful to have short results first,
    this function will order the given qs based on the length of the given field
    """
    return qs.annotate(__size=functions.Length(field)).order_by("__size", "pk")


def try_int(v):
    try:
        int_v = int(v)
    except (TypeError, KeyError, ValueError):
        int_v = 0
    return int_v
