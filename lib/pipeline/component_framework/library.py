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

from pipeline.component_framework.constants import LEGACY_PLUGINS_VERSION
from pipeline.exceptions import ComponentNotExistException


class ComponentLibrary(object):
    components = {}

    def __new__(cls, *args, **kwargs):
        if args:
            component_code = args[0]
        else:
            component_code = kwargs.get("component_code", None)
        version = kwargs.get("version", None)
        if not component_code:
            raise ValueError(
                "please pass a component_code in args or kwargs: "
                "ComponentLibrary('code') or ComponentLibrary(component_code='code')"
            )
        return cls.get_component_class(component_code=component_code, version=version)

    @classmethod
    def component_list(cls):
        components = []
        for _, component_map in cls.components.items():
            components.extend(component_map.values())

        return components

    @classmethod
    def get_component_class(cls, component_code, version=None):
        version = version or LEGACY_PLUGINS_VERSION
        component_cls = cls.components.get(component_code, {}).get(version)
        if component_cls is None:
            raise ComponentNotExistException("component %s does not exist." % component_code)
        return component_cls

    @classmethod
    def get_component(cls, component_code, data_dict, version=None):
        version = version or LEGACY_PLUGINS_VERSION
        return cls.get_component_class(component_code=component_code, version=version)(data_dict)

    @classmethod
    def register_component(cls, component_code, version, component_cls):
        cls.components.setdefault(component_code, {})[version] = component_cls

    @classmethod
    def codes(cls):
        return cls.components.keys()

    @classmethod
    def versions(cls, code):
        return cls.components.get(code, {}).keys()
