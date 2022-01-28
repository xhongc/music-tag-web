# -*- coding: utf-8 -*-
"""
框架补充相关代码
"""

from django.http import Http404
from rest_framework import exceptions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import set_rollback

from component.drf.mapping import exception_mapping


def exception_handler(exc, context):
    """
    Returns the response that should be used for any given exception.

    By default we handle the REST framework `APIException`, and also
    Django's built-in `Http404` and `PermissionDenied` exceptions.

    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    (Rewrite default method exception_handler)
    """
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, "auth_header", None):
            headers["WWW-Authenticate"] = exc.auth_header
        if getattr(exc, "wait", None):
            headers["Retry-After"] = "%d" % exc.wait

        if isinstance(exc.detail, (list, dict)):
            data = exc.detail
        else:
            data = {"detail": exc.detail}

        set_rollback()
        # code is added blow
        exc_class_name = exc.__class__.__name__
        if exc_class_name in exception_mapping:
            message_list = []
            # data type is in (list, dict)
            if isinstance(data, dict):
                for (k, v) in data.items():
                    if isinstance(v, list):
                        # remove 'non_field_errors' key name
                        if k in (api_settings.NON_FIELD_ERRORS_KEY, "detail"):
                            message_list.extend([str(i) for i in v])
                        else:
                            message_list.extend(["{0}: {1}".format(str(k), str(i)) for i in v])
                    else:
                        message_list.append(str(v))
            elif isinstance(data, list):
                message_list.extend([str(item) for item in data])
            raise exception_mapping[exc_class_name](";".join(message_list))
        else:
            return Response(data, status=exc.status_code, headers=headers)

    return None
