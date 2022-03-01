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

from bamboo_engine.context import Context
from bamboo_engine.config import Settings
from bamboo_engine.template import Template
from bamboo_engine.eri import ProcessInfo, ContextValue, ContextValueType, NodeType
from bamboo_engine.handler import register_handler, NodeHandler, ExecuteResult

logger = logging.getLogger("bamboo_engine")


@register_handler(NodeType.SubProcess)
class SubProcessHandler(NodeHandler):
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
        data = self.runtime.get_data(self.node.id)
        root_pipeline_inputs = self._get_plain_inputs(process_info.root_pipeline_id)
        need_render_inputs = data.need_render_inputs()
        render_escape_inputs = data.render_escape_inputs()
        top_pipeline_id = process_info.top_pipeline_id
        root_pipeline_id = process_info.root_pipeline_id

        logger.info(
            "root_pipeline[%s] node(%s) subprocess data: %s",
            root_pipeline_id,
            self.node.id,
            data,
        )

        # reset inner_loop of nodes in subprocess
        self.runtime.reset_children_state_inner_loop(self.node.id)

        # resolve inputs context references
        inputs_refs = Template(need_render_inputs).get_reference()
        logger.info(
            "root_pipeline[%s] node(%s) subprocess original refs: %s",
            root_pipeline_id,
            self.node.id,
            inputs_refs,
        )

        additional_refs = self.runtime.get_context_key_references(pipeline_id=top_pipeline_id, keys=inputs_refs)
        inputs_refs = inputs_refs.union(additional_refs)
        logger.info(
            "root_pipeline[%s] node(%s) subprocess final refs: %s",
            root_pipeline_id,
            self.node.id,
            inputs_refs,
        )

        # prepare context
        context_values = self.runtime.get_context_values(pipeline_id=top_pipeline_id, keys=inputs_refs)

        # pre extract loop outputs
        loop_value = loop + Settings.RERUN_INDEX_OFFSET
        if self.LOOP_KEY in data.outputs:
            loop_output_key = data.outputs[self.LOOP_KEY]
            context_values.append(
                ContextValue(
                    key=loop_output_key,
                    type=ContextValueType.PLAIN,
                    value=loop_value,
                )
            )
        logger.info(
            "root_pipeline[%s] node(%s) subprocess parent context values: %s",
            root_pipeline_id,
            self.node.id,
            context_values,
        )

        context = Context(self.runtime, context_values, root_pipeline_inputs)
        hydrated_context = context.hydrate(deformat=True)
        logger.info(
            "root_pipeline[%s] node(%s) subprocess parent hydrated context: %s",
            root_pipeline_id,
            self.node.id,
            hydrated_context,
        )

        # resolve inputs
        subprocess_inputs = Template(need_render_inputs).render(hydrated_context)
        subprocess_inputs.update(render_escape_inputs)
        sub_context_values = {
            key: ContextValue(key=key, type=ContextValueType.PLAIN, value=value)
            for key, value in subprocess_inputs.items()
        }
        logger.info(
            "root_pipeline[%s] node(%s) subprocess inject context: %s",
            root_pipeline_id,
            self.node.id,
            sub_context_values,
        )

        # update subprocess context, inject subprocess data
        self.runtime.upsert_plain_context_values(self.node.id, sub_context_values)
        process_info.pipeline_stack.append(self.node.id)
        self.runtime.set_pipeline_stack(process_info.process_id, process_info.pipeline_stack)

        return ExecuteResult(
            should_sleep=False,
            schedule_ready=False,
            schedule_type=None,
            schedule_after=-1,
            dispatch_processes=[],
            next_node_id=self.node.start_event_id,
        )
