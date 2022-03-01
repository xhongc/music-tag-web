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

from bamboo_engine import states
from bamboo_engine.context import Context
from bamboo_engine.eri import ProcessInfo, NodeType, ContextValue, ContextValueType
from bamboo_engine.exceptions import NotFoundError
from bamboo_engine.handler import register_handler, NodeHandler, ExecuteResult

logger = logging.getLogger("bamboo_engine")


@register_handler(NodeType.EmptyStartEvent)
class EmptyStartEventHandler(NodeHandler):
    def execute(self, process_info: ProcessInfo, loop: int, inner_loop: int, version: str) -> ExecuteResult:
        """
        节点的 execute 处理逻辑

        :param runtime: 引擎运行时实例
        :type runtime: EngineRuntimeInterface
        :param process_info: 进程信息
        :type process_id: ProcessInfo
        :return: 执行结果
        :rtype: ExecuteResult
        """

        try:
            data = self.runtime.get_data(self.node.id)
        except NotFoundError:
            need_pre_render = False
        else:
            need_pre_render = True

        if need_pre_render:
            top_pipeline_id = process_info.top_pipeline_id
            root_pipeline_inputs = self._get_plain_inputs(process_info.root_pipeline_id)
            upsert_context_dict = dict()
            pre_render_keys = data.inputs["pre_render_keys"].value

            logger.info("top_pipeline({}) pre_render_keys are: {}".format(top_pipeline_id, ",".join(pre_render_keys)))

            refs = self.runtime.get_context_key_references(pipeline_id=top_pipeline_id, keys=set(pre_render_keys))

            context_values = self.runtime.get_context_values(
                pipeline_id=top_pipeline_id, keys=set(pre_render_keys).union(refs)
            )
            context = Context(self.runtime, context_values, root_pipeline_inputs)
            hydrated_context = context.hydrate(deformat=False)
            for context_value in context_values:
                context_key = context_value.key
                if context_key in pre_render_keys:
                    upsert_context_dict[context_key] = ContextValue(
                        key=context_key,
                        type=ContextValueType.PLAIN,
                        value=hydrated_context[context_key],
                    )

            logger.info(f"top_pipeline({top_pipeline_id}) pre_render_keys results are: {upsert_context_dict}")
            self.runtime.upsert_plain_context_values(top_pipeline_id, upsert_context_dict)

        self.runtime.set_state(node_id=self.node.id, to_state=states.FINISHED, set_archive_time=True)

        return ExecuteResult(
            should_sleep=False,
            schedule_ready=False,
            schedule_type=None,
            schedule_after=-1,
            dispatch_processes=[],
            next_node_id=self.node.target_nodes[0],
        )
