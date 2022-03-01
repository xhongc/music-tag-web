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

from pipeline.builder.flow.base import *  # noqa

__all__ = ["EmptyEndEvent", "EmptyStartEvent", "ExecutableEndEvent"]


class EmptyStartEvent(Element):
    def type(self):
        return PE.EmptyStartEvent


class EmptyEndEvent(Element):
    def type(self):
        return PE.EmptyEndEvent


class ExecutableEndEvent(Element):
    def __init__(self, type, **kwargs):
        self._type = type
        super(ExecutableEndEvent, self).__init__(**kwargs)

    def type(self):
        return self._type
