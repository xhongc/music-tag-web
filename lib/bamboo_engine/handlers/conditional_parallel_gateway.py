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
import json
import logging

from bamboo_engine.utils.boolrule import BoolRule
from bamboo_engine.template.template import Template

from bamboo_engine import states
from bamboo_engine.eri import NodeType, ProcessInfo
from bamboo_engine.context import Context
from bamboo_engine.handler import register_handler, NodeHandler, ExecuteResult
from bamboo_engine.utils.string import transform_escape_char

logger = logging.getLogger("bamboo_engine")


@register_handler(NodeType.ConditionalParallelGateway)
class ConditionalParallelGatewayHandler(NodeHandler):
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
        evaluations = [c.evaluation for c in self.node.conditions]
        top_pipeline_id = process_info.top_pipeline_id
        root_pipeline_id = process_info.root_pipeline_id

        root_pipeline_inputs = self._get_plain_inputs(root_pipeline_id)

        # resolve conditions references
        evaluation_refs = set()
        for e in evaluations:
            refs = Template(e).get_reference()
            evaluation_refs = evaluation_refs.union(refs)

        logger.info(
            "root_pipeline[%s] node(%s) evaluation original refs: %s",
            root_pipeline_id,
            self.node.id,
            evaluation_refs,
        )
        additional_refs = self.runtime.get_context_key_references(pipeline_id=top_pipeline_id, keys=evaluation_refs)
        evaluation_refs = evaluation_refs.union(additional_refs)

        logger.info(
            "root_pipeline[%s] node(%s) evaluation final refs: %s",
            root_pipeline_id,
            self.node.id,
            evaluation_refs,
        )
        context_values = self.runtime.get_context_values(pipeline_id=top_pipeline_id, keys=evaluation_refs)
        context = Context(self.runtime, context_values, root_pipeline_inputs)
        try:
            hydrated_context = {k: transform_escape_char(v) for k, v in context.hydrate(deformat=True).items()}
        except Exception as e:
            logger.exception(
                "root_pipeline[%s] node(%s) context hydrate error",
                root_pipeline_id,
                self.node.id,
            )
            return self._execute_fail("evaluation context hydrate failed(%s), check node log for details." % e)

        # check conditions
        fork_targets = []
        for c in self.node.conditions:
            resolved_evaluate = Template(c.evaluation).render(hydrated_context)
            logger.info(
                "root_pipeline[%s] node(%s) render evaluation %s: %s with %s",
                root_pipeline_id,
                self.node.id,
                c.evaluation,
                resolved_evaluate,
                hydrated_context,
            )
            try:
                result = BoolRule(resolved_evaluate).test()
                logger.info(
                    "root_pipeline[%s] node(%s) %s test result: %s",
                    root_pipeline_id,
                    self.node.id,
                    resolved_evaluate,
                    result,
                )
            except Exception as e:
                # test failed
                return self._execute_fail(
                    "evaluate[{}] fail with data[{}] message: {}".format(
                        c.resolved_evaluate, json.dumps(hydrated_context), e
                    )
                )
            else:
                if result:
                    fork_targets.append(c.target_id)

        # all miss
        if not fork_targets:
            return self._execute_fail("all conditions of branches are not meet")

        # fork
        from_to = {}
        for target in fork_targets:
            from_to[target] = self.node.converge_gateway_id

        dispatch_processes = self.runtime.fork(
            parent_id=process_info.process_id,
            root_pipeline_id=process_info.root_pipeline_id,
            pipeline_stack=process_info.pipeline_stack,
            from_to=from_to,
        )

        self.runtime.set_state(node_id=self.node.id, to_state=states.FINISHED, set_archive_time=True)

        return ExecuteResult(
            should_sleep=True,
            schedule_ready=False,
            schedule_type=None,
            schedule_after=-1,
            dispatch_processes=dispatch_processes,
            next_node_id=None,
        )
