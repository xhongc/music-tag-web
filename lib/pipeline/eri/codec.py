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

import json

from typing import Any

from django.utils.module_loading import import_string

DATA_JSON_ENCODER_PATH = None
DATA_JSON_OBJECT_HOOK_PATH = None

_LOCAL = {}


def _get_local(key, path):
    if key in _LOCAL:
        return _LOCAL[key]

    try:
        _LOCAL[key] = import_string(path)
    except ImportError:
        _LOCAL[key] = None

    return _LOCAL[key]


def _get_data_json_encoder():
    if not DATA_JSON_ENCODER_PATH:
        return None
    return _get_local("data_json_encoder", DATA_JSON_ENCODER_PATH)


def _get_data_json_object_hook():
    if not DATA_JSON_OBJECT_HOOK_PATH:
        return None
    return _get_local("data_json_object_hook", DATA_JSON_OBJECT_HOOK_PATH)


def data_json_loads(data: str) -> Any:
    return json.loads(data, object_hook=_get_data_json_object_hook())


def data_json_dumps(data: Any) -> str:
    return json.dumps(data, cls=_get_data_json_encoder())
