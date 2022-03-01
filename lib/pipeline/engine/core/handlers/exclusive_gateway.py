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
from copy import deepcopy

from pipeline.core.data.hydration import hydrate_data
from pipeline.core.flow.gateway import ExclusiveGateway
from pipeline.engine.models import Status
from pipeline.exceptions import PipelineException

from .base import FlowElementHandler

logger = logging.getLogger("pipeline_engine")

__all__ = ["ExclusiveGatewayHandler"]


class ExclusiveGatewayHandler(FlowElementHandler):
    @staticmethod
    def element_cls():
        return ExclusiveGateway

    def handle(self, process, element, status):
        if status.loop > 1:
            process.top_pipeline.context.recover_variable()
        try:
            # use temp variables instead of real variables to prevent output pre extract error
            temp_variables = deepcopy(process.top_pipeline.context.variables)
            hydrate_context = hydrate_data(temp_variables)
            logger.info("[{}] hydrate_context: {}".format(element.id, hydrate_context))
            next_node = element.next(hydrate_context)
        except PipelineException as e:
            logger.error(traceback.format_exc())
            Status.objects.fail(element, ex_data=str(e))
            return self.HandleResult(next_node=None, should_return=True, should_sleep=True)
        Status.objects.finish(element)
        return self.HandleResult(next_node=next_node, should_return=False, should_sleep=False)
