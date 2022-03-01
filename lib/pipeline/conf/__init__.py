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

from django.conf import settings as django_settings

from pipeline.conf import default_settings


class PipelineSettings(object):
    def __getattr__(self, key):
        if hasattr(django_settings, key):
            return getattr(django_settings, key)

        if hasattr(default_settings, key):
            return getattr(default_settings, key)

        raise AttributeError("Settings object has no attribute %s" % key)


settings = PipelineSettings()
