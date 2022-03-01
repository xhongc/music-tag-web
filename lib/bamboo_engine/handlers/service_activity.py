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
from typing import Optional

from bamboo_engine import states
from bamboo_engine.config import Settings

from bamboo_engine.context import Context
from bamboo_engine.template import Template
from bamboo_engine.eri import (
    ProcessInfo,
    ContextValue,
    ContextValueType,
    ExecutionData,
    CallbackData,
    ScheduleType,
    NodeType,
    Schedule,
)
from bamboo_engine.handler import (
    register_handler,
    NodeHandler,
    ExecuteResult,
    ScheduleResult,
)

logger = logging.getLogger("bamboo_engine")


@register_handler(NodeType.ServiceActivity)
class ServiceActivityHandler(NodeHandler):
    """
    其中所有 set_state 调用都会传入 state version 来确保能够在用户强制失败节点后放弃后续无效的任务执行
    """

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
        top_pipeline_id = process_info.top_pipeline_id
        root_pipeline_id = process_info.root_pipeline_id

        data = self.runtime.get_data(self.node.id)
        root_pipeline_inputs = self._get_plain_inputs(process_info.root_pipeline_id)
        need_render_inputs = data.need_render_inputs()
        render_escape_inputs = data.render_escape_inputs()

        logger.info(
            "root_pipeline[%s] node(%s) activity execute data: %s, root inputs: %s",
            root_pipeline_id,
            self.node.id,
            data,
            root_pipeline_inputs,
        )

        # resolve inputs context references
        inputs_refs = set(Template(need_render_inputs).get_reference())
        logger.info(
            "root_pipeline[%s] node(%s) activity original refs: %s",
            root_pipeline_id,
            self.node.id,
            inputs_refs,
        )

        additional_refs = self.runtime.get_context_key_references(pipeline_id=top_pipeline_id, keys=inputs_refs)
        inputs_refs = inputs_refs.union(additional_refs)
        logger.info(
            "root_pipeline[%s] node(%s) activity final refs: %s",
            root_pipeline_id,
            self.node.id,
            inputs_refs,
        )

        # prepare context
        context_values = self.runtime.get_context_values(pipeline_id=top_pipeline_id, keys=inputs_refs)

        # pre extract loop outputs
        loop_value = loop + Settings.RERUN_INDEX_OFFSET
        need_render_inputs[self.LOOP_KEY] = loop_value
        if self.LOOP_KEY in data.outputs:
            loop_output_key = data.outputs[self.LOOP_KEY]
            context_values.append(ContextValue(key=loop_output_key, type=ContextValueType.PLAIN, value=loop_value))

        # pre extract inner_loop outputs
        inner_loop_value = inner_loop + Settings.RERUN_INDEX_OFFSET
        need_render_inputs[self.INNER_LOOP_KEY] = inner_loop_value
        if self.INNER_LOOP_KEY in data.outputs:
            inner_loop_output_key = data.outputs[self.INNER_LOOP_KEY]
            context_values.append(
                ContextValue(
                    key=inner_loop_output_key,
                    type=ContextValueType.PLAIN,
                    value=inner_loop_value,
                )
            )

        logger.info(
            "root_pipeline[%s] node(%s) activity context values: %s",
            root_pipeline_id,
            self.node.id,
            context_values,
        )

        context = Context(self.runtime, context_values, root_pipeline_inputs)
        # hydrate will call user code, use try to catch unexpected error
        try:
            hydrated_context = context.hydrate(deformat=True)
        except Exception as e:
            logger.exception(
                "root_pipeline[%s] node(%s) activity context hydrate error",
                root_pipeline_id,
                self.node.id,
            )
            service_data = ExecutionData(inputs=data.plain_inputs(), outputs={})
            service_data.outputs.ex_data = "inputs hydrate failed(%s), check node log for details" % e
            service_data.outputs._result = False
            service_data.outputs._loop = loop
            service_data.outputs._inner_loop = inner_loop

            self.runtime.set_execution_data(node_id=self.node.id, data=service_data)
            self.runtime.set_state(
                node_id=self.node.id,
                version=version,
                to_state=states.FAILED,
                set_archive_time=True,
            )
            return ExecuteResult(
                should_sleep=True,
                schedule_ready=False,
                schedule_type=None,
                schedule_after=-1,
                dispatch_processes=[],
                next_node_id=None,
            )

        logger.info(
            "root_pipeline[%s] node(%s) actvity hydrated context: %s",
            root_pipeline_id,
            self.node.id,
            hydrated_context,
        )

        # resolve inputs
        execute_inputs = Template(need_render_inputs).render(hydrated_context)
        execute_inputs.update(render_escape_inputs)

        # data prepare
        service_data = ExecutionData(inputs=execute_inputs, outputs={})
        root_pipeline_data = ExecutionData(inputs=root_pipeline_inputs, outputs={})

        # execute
        service = self.runtime.get_service(code=self.node.code, version=self.node.version)
        service.setup_runtime_attributes(
            id=self.node.id,
            version=version,
            top_pipeline_id=top_pipeline_id,
            root_pipeline_id=root_pipeline_id,
            loop=loop,
            inner_loop=inner_loop,
        )

        # start monitor
        monitoring = False
        if self.node.timeout is not None:
            monitoring = True
            self.runtime.start_timeout_monitor(
                process_id=process_info.process_id,
                node_id=self.node.id,
                version=version,
                timeout=self.node.timeout,
            )

        # pre_execute and excute
        logger.debug(
            "root_pipeline[%s] node(%s) service data before execute: %s",
            self.node.id,
            root_pipeline_id,
            service_data,
        )
        logger.debug(
            "root_pipeline[%s] node(%s) root pipeline data before execute: %s",
            self.node.id,
            root_pipeline_id,
            root_pipeline_data,
        )
        execute_success = False
        try:
            service.pre_execute(data=service_data, root_pipeline_data=root_pipeline_data)
            execute_success = service.execute(data=service_data, root_pipeline_data=root_pipeline_data)
        except Exception:
            ex_data = traceback.format_exc()
            service_data.outputs.ex_data = ex_data
            logger.warning("root_pipeline[%s]service execute fail: %s", process_info.root_pipeline_id, ex_data)
        logger.debug("root_pipeline[%s] service data after execute: %s", root_pipeline_id, service_data)
        service_data.outputs._result = execute_success
        service_data.outputs._loop = loop
        service_data.outputs._inner_loop = inner_loop

        # execute success
        if execute_success:

            need_schedule = service.need_schedule()
            next_node_id = None

            if not need_schedule:
                if monitoring:
                    self.runtime.stop_timeout_monitor(
                        process_id=process_info.process_id,
                        node_id=self.node.id,
                        version=version,
                        timeout=self.node.timeout,
                    )

                self.runtime.set_state(
                    node_id=self.node.id,
                    version=version,
                    to_state=states.FINISHED,
                    set_archive_time=True,
                )

                context.extract_outputs(
                    pipeline_id=top_pipeline_id,
                    data_outputs=data.outputs,
                    execution_data_outputs=service_data.outputs,
                )
                next_node_id = self.node.target_nodes[0]

            self.runtime.set_execution_data(node_id=self.node.id, data=service_data)

            return ExecuteResult(
                should_sleep=need_schedule,
                schedule_ready=need_schedule,
                schedule_type=service.schedule_type(),
                schedule_after=service.schedule_after(
                    schedule=None,
                    data=service_data,
                    root_pipeline_data=root_pipeline_data,
                ),
                dispatch_processes=[],
                next_node_id=next_node_id,
            )

        # pre_execute failed or execute failed
        if monitoring:
            self.runtime.stop_timeout_monitor(
                process_id=process_info.process_id,
                node_id=self.node.id,
                version=version,
                timeout=self.node.timeout,
            )

        if not self.node.error_ignorable:
            self.runtime.set_state(
                node_id=self.node.id,
                version=version,
                to_state=states.FAILED,
                set_archive_time=True,
            )

            self.runtime.set_execution_data(node_id=self.node.id, data=service_data)

            context.extract_outputs(
                pipeline_id=top_pipeline_id,
                data_outputs=data.outputs,
                execution_data_outputs=service_data.outputs,
            )

            return ExecuteResult(
                should_sleep=True,
                schedule_ready=False,
                schedule_type=None,
                schedule_after=-1,
                dispatch_processes=[],
                next_node_id=None,
            )

        # pre_execute failed or execute failed and error ignore
        self.runtime.set_state(
            node_id=self.node.id,
            version=version,
            to_state=states.FINISHED,
            set_archive_time=True,
            error_ignored=True,
        )

        self.runtime.set_execution_data(node_id=self.node.id, data=service_data)

        context.extract_outputs(
            pipeline_id=top_pipeline_id,
            data_outputs=data.outputs,
            execution_data_outputs=service_data.outputs,
        )

        return ExecuteResult(
            should_sleep=False,
            schedule_ready=False,
            schedule_type=None,
            schedule_after=-1,
            dispatch_processes=[],
            next_node_id=self.node.target_nodes[0],
        )

    def _finish_schedule(
        self,
        process_info: ProcessInfo,
        schedule: Schedule,
        data_outputs: dict,
        execution_data: ExecutionData,
        error_ignored: bool,
        root_pipeline_inputs: dict,
    ) -> ScheduleResult:
        if self.node.timeout is not None:
            self.runtime.stop_timeout_monitor(
                process_id=process_info.process_id,
                node_id=self.node.id,
                version=schedule.version,
                timeout=self.node.timeout,
            )

        self.runtime.set_state(
            node_id=self.node.id,
            version=schedule.version,
            to_state=states.FINISHED,
            set_archive_time=True,
            error_ignored=error_ignored,
        )

        context = Context(self.runtime, [], root_pipeline_inputs)
        context.extract_outputs(
            pipeline_id=process_info.top_pipeline_id,
            data_outputs=data_outputs,
            execution_data_outputs=execution_data.outputs,
        )

        return ScheduleResult(
            has_next_schedule=False,
            schedule_after=-1,
            schedule_done=True,
            next_node_id=self.node.target_nodes[0],
        )

    def schedule(
        self,
        process_info: ProcessInfo,
        loop: int,
        inner_loop: int,
        schedule: Schedule,
        callback_data: Optional[CallbackData] = None,
    ) -> ScheduleResult:
        """
        节点的 schedule 处理逻辑

        :param process_id: 进程 ID
        :type process_id: int
        :param schedule: Schedule 实例
        :type schedule: Schedule
        :param callback_data: 回调数据, defaults to None
        :type callback_data: Optional[CallbackData], optional
        :return: 调度结果
        :rtype: ScheduleResult
        """
        # data prepare
        top_pipeline_id = process_info.top_pipeline_id
        root_pipeline_id = process_info.root_pipeline_id

        data_outputs = self.runtime.get_data_outputs(self.node.id)
        service_data = self.runtime.get_execution_data(self.node.id)

        root_pipeline_inputs = self._get_plain_inputs(root_pipeline_id)
        root_pipeline_data = ExecutionData(inputs=root_pipeline_inputs, outputs={})
        logger.info(
            "root_pipeline[%s] node(%s) activity schedule data: %s, root inputs: %s",
            root_pipeline_id,
            self.node.id,
            service_data,
            root_pipeline_inputs,
        )

        # schedule
        service = self.runtime.get_service(code=self.node.code, version=self.node.version)
        service.setup_runtime_attributes(
            id=self.node.id,
            version=schedule.version,
            top_pipeline_id=top_pipeline_id,
            root_pipeline_id=root_pipeline_id,
            loop=loop,
            inner_loop=inner_loop,
        )

        schedule_success = False
        schedule.times += 1
        try:
            schedule_success = service.schedule(
                schedule=schedule,
                data=service_data,
                root_pipeline_data=root_pipeline_data,
                callback_data=callback_data,
            )
        except Exception:
            service_data.outputs.ex_data = traceback.format_exc()

        service_data.outputs._result = schedule_success
        service_data.outputs._loop = loop
        service_data.outputs._inner_loop = inner_loop

        self.runtime.add_schedule_times(schedule.id)
        self.runtime.set_execution_data(node_id=self.node.id, data=service_data)

        monitoring = self.node.timeout is not None
        schedule_type = service.schedule_type()

        # schedule success
        if schedule_success:
            if schedule_type == ScheduleType.CALLBACK:
                return self._finish_schedule(
                    process_info=process_info,
                    schedule=schedule,
                    data_outputs=data_outputs,
                    execution_data=service_data,
                    error_ignored=False,
                    root_pipeline_inputs=root_pipeline_inputs,
                )
            else:
                is_schedule_done = service.is_schedule_done()

                # poll or multi-callback finished
                if is_schedule_done:
                    return self._finish_schedule(
                        process_info=process_info,
                        schedule=schedule,
                        data_outputs=data_outputs,
                        execution_data=service_data,
                        error_ignored=False,
                        root_pipeline_inputs=root_pipeline_inputs,
                    )

                has_next_schedule = schedule_type == ScheduleType.POLL
                return ScheduleResult(
                    has_next_schedule=has_next_schedule,
                    schedule_after=service.schedule_after(
                        schedule=schedule,
                        data=service_data,
                        root_pipeline_data=root_pipeline_data,
                    ),
                    schedule_done=False,
                    next_node_id=None,
                )

        if monitoring:
            self.runtime.stop_timeout_monitor(
                process_id=process_info.process_id,
                node_id=self.node.id,
                version=schedule.version,
                timeout=self.node.timeout,
            )

        # schedule fail
        if not self.node.error_ignorable:
            self.runtime.set_state(
                node_id=self.node.id,
                version=schedule.version,
                to_state=states.FAILED,
                set_archive_time=True,
            )

            context = Context(self.runtime, [], root_pipeline_inputs)
            context.extract_outputs(
                pipeline_id=process_info.top_pipeline_id,
                data_outputs=data_outputs,
                execution_data_outputs=service_data.outputs,
            )

            return ScheduleResult(
                has_next_schedule=False,
                schedule_after=-1,
                schedule_done=False,
                next_node_id=None,
            )

        # schedule fail and error ignore
        return self._finish_schedule(
            process_info=process_info,
            schedule=schedule,
            data_outputs=data_outputs,
            execution_data=service_data,
            error_ignored=True,
            root_pipeline_inputs=root_pipeline_inputs,
        )
