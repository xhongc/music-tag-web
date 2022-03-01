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

from pipeline.core.data import var
from pipeline.core.flow.event import EmptyStartEvent
from pipeline.engine.models import Status

from .base import FlowElementHandler

logger = logging.getLogger("pipeline_engine")

__all__ = ["EmptyStartEventHandler"]


class EmptyStartEventHandler(FlowElementHandler):
    @staticmethod
    def element_cls():
        return EmptyStartEvent

    @staticmethod
    def _hydrate(value):
        return value.get() if issubclass(value.__class__, var.Variable) else value

    def handle(self, process, element, status):
        # 进行变量预渲染
        if hasattr(element.data, "inputs"):
            for pre_render_key in element.data.inputs.get("pre_render_keys", []):
                context_variables = process.top_pipeline.context.variables
                if pre_render_key in context_variables:
                    context_variables[pre_render_key] = self._hydrate(context_variables[pre_render_key])

        Status.objects.finish(element)
        return self.HandleResult(next_node=element.next(), should_return=False, should_sleep=False)
