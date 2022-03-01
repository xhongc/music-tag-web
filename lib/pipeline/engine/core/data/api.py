# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import contextlib
import logging
import traceback

from django.utils.module_loading import import_string

from pipeline.conf import settings
from pipeline.engine.exceptions import InvalidDataBackendError

logger = logging.getLogger("celery")

_backend = None
_candidate_backend = None


def _import_backend(backend_cls_path):
    try:
        backend_cls = import_string(backend_cls_path)
        return backend_cls()
    except ImportError:
        raise InvalidDataBackendError(
            "data backend({}) import error with exception: {}".format(
                settings.PIPELINE_DATA_BACKEND, traceback.format_exc()
            )
        )


@contextlib.contextmanager
def _candidate_exc_ensure(propagate):
    try:
        yield
    except Exception:
        logger.error("candidate data backend operate error: {}".format(traceback.format_exc()))

        if propagate:
            raise


if not _backend:
    _backend = _import_backend(settings.PIPELINE_DATA_BACKEND)

if not _candidate_backend and settings.PIPELINE_DATA_CANDIDATE_BACKEND:
    _candidate_backend = _import_backend(settings.PIPELINE_DATA_CANDIDATE_BACKEND)


if settings.PIPELINE_DATA_BACKEND_AUTO_EXPIRE and not (_backend and _candidate_backend):
    raise RuntimeError(
        "PIPELINE_DATA_BACKEND and PIPELINE_DATA_CANDIDATE_BACKEND can't both be empty when PIPELINE_DATA_BACKEND_AUTO_EXPIRE is set."  # noqa
    )


def _write_operation(method, *args, **kwargs):
    propagate = False

    try:

        if settings.PIPELINE_DATA_BACKEND_AUTO_EXPIRE and method == "set_object":
            # change set_object to expire_cache
            getattr(_backend, "expire_cache")(
                *args, **kwargs, expires=settings.PIPELINE_DATA_BACKEND_AUTO_EXPIRE_SECONDS
            )
        else:
            getattr(_backend, method)(*args, **kwargs)

    except Exception:
        logger.error("data backend operate error: {}".format(traceback.format_exc()))

        if not _candidate_backend:
            raise

        propagate = True

    if _candidate_backend:
        with _candidate_exc_ensure(propagate):
            getattr(_candidate_backend, method)(*args, **kwargs)


def _read_operation(method, *args, **kwargs):
    result = None
    propagate = False

    try:
        result = getattr(_backend, method)(*args, **kwargs)
    except Exception:
        logger.error("data backend operate error: {}".format(traceback.format_exc()))

        if not _candidate_backend:
            raise

        propagate = True

    if result is None and _candidate_backend:
        with _candidate_exc_ensure(propagate):
            result = getattr(_candidate_backend, method)(*args, **kwargs)

    return result


def set_object(key, obj):
    _write_operation("set_object", key, obj)


def del_object(key):
    _write_operation("del_object", key)


def expire_cache(key, obj, expires):
    _write_operation("expire_cache", key, obj, expires)


def get_object(key):
    return _read_operation("get_object", key)


def cache_for(key):
    return _read_operation("cache_for", key)


def set_schedule_data(schedule_id, parent_data):
    return set_object("%s_schedule_parent_data" % schedule_id, parent_data)


def get_schedule_parent_data(schedule_id):
    return get_object("%s_schedule_parent_data" % schedule_id)


def delete_parent_data(schedule_id):
    return del_object("%s_schedule_parent_data" % schedule_id)
