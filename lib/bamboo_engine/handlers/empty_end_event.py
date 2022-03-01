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
from bamboo_engine.config import Settings
from bamboo_engine.eri import ProcessInfo, NodeType
from bamboo_engine.handler import register_handler, NodeHandler, ExecuteResult
from bamboo_engine.context import Context
from bamboo_engine.template.template import Template

logger = logging.getLogger("bamboo_engine")


@register_handler(NodeType.EmptyEndEvent)
class EmptyEndEventHandler(NodeHandler):
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
        root_pipeline_id = process_info.root_pipeline_id
        pipeline_id = process_info.pipeline_stack.pop()
        root_pipeline_finished = len(process_info.pipeline_stack) == 0

        root_pipeline_inputs = self._get_plain_inputs(process_info.root_pipeline_id)
        if not root_pipeline_finished:
            subproc_state = self.runtime.get_state(pipeline_id)

        # write pipeline data
        context_outputs = self.runtime.get_context_outputs(pipeline_id)
        logger.info(
            "root_pipeline[%s] pipeline(%s) context outputs: %s",
            root_pipeline_id,
            pipeline_id,
            context_outputs,
        )

        context_values = self.runtime.get_context_values(pipeline_id=pipeline_id, keys=context_outputs)
        logger.info(
            "root_pipeline[%s] pipeline(%s) context values: %s",
            root_pipeline_id,
            pipeline_id,
            context_values,
        )

        # caculate outputs values references
        output_value_refs = set(Template([cv.value for cv in context_values]).get_reference())
        logger.info(
            "root_pipeline[%s] node(%s) outputs values refs: %s",
            root_pipeline_id,
            self.node.id,
            output_value_refs,
        )

        additional_refs = self.runtime.get_context_key_references(pipeline_id=pipeline_id, keys=output_value_refs)
        output_value_refs = output_value_refs.union(additional_refs)
        logger.info(
            "root_pipeline[%s] pipeline(%s) outputs values final refs: %s",
            root_pipeline_id,
            pipeline_id,
            output_value_refs,
        )
        context_values.extend(self.runtime.get_context_values(pipeline_id=pipeline_id, keys=output_value_refs))

        context = Context(self.runtime, context_values, root_pipeline_inputs)
        hydrated_context = context.hydrate(deformat=False)
        logger.info(
            "root_pipeline[%s] pipeline(%s) hydrated context: %s",
            root_pipeline_id,
            pipeline_id,
            hydrated_context,
        )

        outputs = {}
        for key in context_outputs:
            outputs[key] = hydrated_context.get(key, key)
        if not root_pipeline_finished:
            outputs[self.LOOP_KEY] = subproc_state.loop + Settings.RERUN_INDEX_OFFSET
            outputs[self.INNER_LOOP_KEY] = subproc_state.inner_loop + Settings.RERUN_INDEX_OFFSET
        self.runtime.set_execution_data_outputs(node_id=pipeline_id, outputs=outputs)

        self.runtime.set_state(node_id=self.node.id, to_state=states.FINISHED, set_archive_time=True)

        self.runtime.set_state(node_id=pipeline_id, to_state=states.FINISHED, set_archive_time=True)

        # root pipeline finish
        if root_pipeline_finished:
            return ExecuteResult(
                should_sleep=False,
                schedule_ready=False,
                schedule_type=None,
                schedule_after=-1,
                dispatch_processes=[],
                next_node_id=None,
                should_die=True,
            )

        # subprocess finish
        subprocess = self.runtime.get_node(pipeline_id)
        self.runtime.set_pipeline_stack(process_info.process_id, process_info.pipeline_stack)

        # extract subprocess outputs to parent context
        subprocess_outputs = self.runtime.get_data_outputs(pipeline_id)
        context.extract_outputs(
            pipeline_id=process_info.pipeline_stack[-1],
            data_outputs=subprocess_outputs,
            execution_data_outputs=outputs,
        )

        return ExecuteResult(
            should_sleep=False,
            schedule_ready=False,
            schedule_type=None,
            schedule_after=-1,
            dispatch_processes=[],
            next_node_id=subprocess.target_nodes[0],
        )
