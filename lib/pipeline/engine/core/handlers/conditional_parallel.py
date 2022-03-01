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
import traceback

from pipeline.core.data.hydration import hydrate_data
from pipeline.core.flow.gateway import ConditionalParallelGateway
from pipeline.engine.models import PipelineProcess, Status
from pipeline.exceptions import PipelineException

from .base import FlowElementHandler

logger = logging.getLogger("pipeline_engine")

__all__ = ["ConditionalParallelGatewayHandler"]


class ConditionalParallelGatewayHandler(FlowElementHandler):
    @staticmethod
    def element_cls():
        return ConditionalParallelGateway

    def handle(self, process, element, status):
        if status.loop > 1:
            process.top_pipeline.context.recover_variable()

        try:
            hydrate_context = hydrate_data(process.top_pipeline.context.variables)
            targets = element.targets_meet_condition(hydrate_context)
        except PipelineException as e:
            logger.error(traceback.format_exc())
            Status.objects.fail(element, ex_data=str(e))
            return self.HandleResult(next_node=None, should_return=True, should_sleep=True)

        children = []

        for target in targets:
            try:
                child = PipelineProcess.objects.fork_child(
                    parent=process, current_node_id=target.id, destination_id=element.converge_gateway_id
                )
            except PipelineException as e:
                logger.error(traceback.format_exc())
                Status.objects.fail(element, ex_data=str(e))
                return self.HandleResult(next_node=None, should_return=True, should_sleep=True)

            children.append(child)

        process.join(children)

        Status.objects.finish(element)

        return self.HandleResult(next_node=None, should_return=True, should_sleep=True)
