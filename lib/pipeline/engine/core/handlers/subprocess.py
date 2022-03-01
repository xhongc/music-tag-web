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

from pipeline.conf import default_settings
from pipeline.core.data.hydration import hydrate_node_data
from pipeline.core.flow.activity import SubProcess

from .base import FlowElementHandler

logger = logging.getLogger("pipeline_engine")

__all__ = ["SubprocessHandler"]


class SubprocessHandler(FlowElementHandler):
    @staticmethod
    def element_cls():
        return SubProcess

    def handle(self, process, element, status):
        # rerun mode
        if status.loop > 1:
            element.prepare_rerun_data()
            element.pipeline.context.recover_variable()
            process.top_pipeline.context.recover_variable()

        # set loop count
        element.data.outputs._loop = status.loop + default_settings.PIPELINE_RERUN_INDEX_OFFSET

        # pre output extract
        process.top_pipeline.context.extract_output(element, set_miss=False)

        # hydrate data
        hydrate_node_data(element)

        # context injection
        data = element.pipeline.data
        context = element.pipeline.context
        for k, v in list(data.get_inputs().items()):
            context.set_global_var(k, v)

        sub_pipeline = element.pipeline
        process.push_pipeline(sub_pipeline, is_subprocess=True)
        process.take_snapshot()
        return self.HandleResult(next_node=sub_pipeline.start_event, should_return=False, should_sleep=False)
