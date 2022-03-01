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

from pipeline.core.flow.gateway import ConvergeGateway
from pipeline.engine import exceptions
from pipeline.engine.models import Status

from .base import FlowElementHandler

logger = logging.getLogger("pipeline_engine")

__all__ = ["ConvergeGatewayHandler"]


class ConvergeGatewayHandler(FlowElementHandler):
    @staticmethod
    def element_cls():
        return ConvergeGateway

    def handle(self, process, element, status):
        # try to sync data if current process has children
        if process.children:
            try:
                process.sync_with_children()
            except exceptions.ChildDataSyncError:
                logger.error(traceback.format_exc())
                # clean children and update current_node to prevent re execute child process
                process.clean_children()
                Status.objects.fail(element, ex_data="Sync branch context error, check data backend status please.")
                return self.HandleResult(next_node=None, should_return=True, should_sleep=True)

        Status.objects.finish(element)
        return self.HandleResult(next_node=element.next(), should_return=False, should_sleep=False)
