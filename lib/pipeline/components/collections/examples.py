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

import logging

from pipeline.component_framework.component import Component
from pipeline.conf import settings
from pipeline.core.flow.activity import Service

logger = logging.getLogger("celery")

__register_ignore__ = not settings.ENABLE_EXAMPLE_COMPONENTS


class SimpleExampleService(Service):
    def execute(self, data, parent_data):
        return True

    def outputs_format(self):
        return []


class SimpleExampleComponent(Component):
    name = "example component"
    code = "example_component"
    bound_service = SimpleExampleService


class PipeExampleService(Service):
    def execute(self, data, parent_data):
        for key, val in list(data.inputs.items()):
            data.set_outputs(key, val)
        return True

    def outputs_format(self):
        return []


class PipeExampleComponent(Component):
    name = "pipe example component"
    code = "pipe_example_component"
    bound_service = PipeExampleService
