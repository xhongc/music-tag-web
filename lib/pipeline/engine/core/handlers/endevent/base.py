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

from pipeline.core.flow import activity
from pipeline.engine import states
from pipeline.engine.models import Data, Status

from ..base import FlowElementHandler

logger = logging.getLogger("celery")


class EndEventHandler(FlowElementHandler):
    @staticmethod
    def element_cls():
        raise NotImplementedError()

    def handle(self, process, element, status):
        pipeline = process.pop_pipeline()
        if process.pipeline_stack:
            # pop subprocess and return to top of stack
            pipeline.context.write_output(pipeline)
            Status.objects.finish(element)
            sub_process_node = process.top_pipeline.node(pipeline.id)
            Status.objects.finish(sub_process_node)
            # extract subprocess output
            process.top_pipeline.context.extract_output(sub_process_node)
            return self.HandleResult(next_node=sub_process_node.next(), should_return=False, should_sleep=False)
        else:
            with Status.objects.lock(pipeline.id):
                # save data and destroy process
                pipeline.context.write_output(pipeline)
                Data.objects.write_node_data(pipeline)
                Status.objects.finish(element)

                Status.objects.transit(pipeline.id, to_state=states.FINISHED, is_pipeline=True)
                # PipelineInstance.objects.set_finished(process.root_pipeline.id)
                element.pipeline_finish(process.root_pipeline.id)
                for act in pipeline.spec.activities:
                    if isinstance(act, activity.SubProcess):
                        act.pipeline.context.clear()
                pipeline.context.clear()
                process.destroy()
                return self.HandleResult(next_node=None, should_return=True, should_sleep=False)
