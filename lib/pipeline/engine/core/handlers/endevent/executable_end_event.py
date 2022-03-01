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

from pipeline.core.flow.event import ExecutableEndEvent
from pipeline.engine.models import Status

from .base import EndEventHandler

logger = logging.getLogger("celery")


class ExecutableEndEventHandler(EndEventHandler):
    @staticmethod
    def element_cls():
        return ExecutableEndEvent

    def handle(self, process, element, status):
        try:
            element.execute(
                in_subprocess=process.in_subprocess,
                root_pipeline_id=process.root_pipeline.id,
                current_pipeline_id=process.top_pipeline.id,
            )
        except Exception:
            ex_data = traceback.format_exc()
            element.data.outputs.ex_data = ex_data
            logger.error(ex_data)

            Status.objects.fail(element, ex_data)
            return self.HandleResult(next_node=None, should_return=False, should_sleep=True)

        return super(ExecutableEndEventHandler, self).handle(process, element, status)
