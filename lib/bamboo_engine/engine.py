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

# 引擎核心模块

import time
import random
import logging
import traceback
from typing import Optional
from contextlib import contextmanager


from . import states
from . import validator
from .local import set_node_info, clear_node_info, CurrentNodeInfo
from .exceptions import InvalidOperationError, NotFoundError, StateVersionNotMatchError
from .handler import HandlerFactory
from .metrics import (
    ENGINE_RUNNING_PROCESSES,
    ENGINE_RUNNING_SCHEDULES,
    ENGINE_PROCESS_RUNNING_TIME,
    ENGINE_SCHEDULE_RUNNING_TIME,
    ENGINE_NODE_EXECUTE_TIME,
    ENGINE_NODE_SCHEDULE_TIME,
    setup_gauge,
    setup_histogram,
)
from .eri import (
    EngineRuntimeInterface,
    ScheduleType,
    NodeType,
    State,
    ExecutionData,
    DataInput,
    Node,
)
from .utils.string import get_lower_case_name
from .utils.host import get_hostname

logger = logging.getLogger("bamboo_engine")


class Engine:
    """
    流程引擎，封装流程核心调度逻辑
    """

    PURE_SKIP_ENABLE_NODE_TYPE = {NodeType.ServiceActivity, NodeType.EmptyStartEvent}

    def __init__(self, runtime: EngineRuntimeInterface):
        self.runtime = runtime
        self._hostname = get_hostname()

    # api
    def run_pipeline(
        self,
        pipeline: dict,
        root_pipeline_data: Optional[dict] = None,
        root_pipeline_context: Optional[dict] = None,
        subprocess_context: Optional[dict] = None,
        **options
    ):
        """
        运行流程

        :param pipeline: 流程数据
        :type pipeline: dict
        :param root_pipeline_data 根流程数据
        :type root_pipeline_data: dict
        :param root_pipeline_context 根流程上下文
        :type root_pipeline_context: dict
        :param subprocess_context 子流程预置流程上下文
        :type subprocess_context: dict
        """

        root_pipeline_data = {} if root_pipeline_data is None else root_pipeline_data
        root_pipeline_context = {} if root_pipeline_context is None else root_pipeline_context
        subprocess_context = {} if subprocess_context is None else subprocess_context
        cycle_tolerate = options.get("cycle_tolerate", False)
        validator.validate_and_process_pipeline(pipeline, cycle_tolerate)

        self.runtime.pre_prepare_run_pipeline(
            pipeline, root_pipeline_data, root_pipeline_context, subprocess_context, **options
        )

        process_id = self.runtime.prepare_run_pipeline(
            pipeline, root_pipeline_data, root_pipeline_context, subprocess_context, **options
        )
        # execute from start event
        self.runtime.execute(
            process_id=process_id,
            node_id=pipeline["start_event"]["id"],
            root_pipeline_id=pipeline["id"],
            parent_pipeline_id=pipeline["id"],
        )

        self.runtime.post_prepare_run_pipeline(
            pipeline, root_pipeline_data, root_pipeline_context, subprocess_context, **options
        )

    def pause_pipeline(self, pipeline_id: str):
        """
        暂停流程

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        """
        if not self.runtime.has_state(pipeline_id):
            raise NotFoundError("node({}) does not exist".format(pipeline_id))

        self.runtime.pre_pause_pipeline(pipeline_id)

        self.runtime.set_state(node_id=pipeline_id, to_state=states.SUSPENDED)

        self.runtime.post_pause_pipeline(pipeline_id)

    def revoke_pipeline(self, pipeline_id: str):
        """
        撤销流程

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        """
        if not self.runtime.has_state(pipeline_id):
            raise NotFoundError("node({}) does not exist".format(pipeline_id))

        self.runtime.pre_revoke_pipeline(pipeline_id)

        self.runtime.set_state(node_id=pipeline_id, to_state=states.REVOKED)

        self.runtime.post_revoke_pipeline(pipeline_id)

    def resume_pipeline(self, pipeline_id: str):
        """
        继续流程

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        """
        state = self.runtime.get_state(pipeline_id)

        if state.name != states.SUSPENDED:
            raise InvalidOperationError("pipeline({}) state is: {}".format(pipeline_id, state.name))

        info_list = self.runtime.get_suspended_process_info(pipeline_id)

        self.runtime.pre_resume_pipeline(pipeline_id)

        self.runtime.set_state(node_id=pipeline_id, to_state=states.RUNNING)

        if info_list:
            self.runtime.batch_resume(process_id_list=[i.process_id for i in info_list])
            for info in info_list:
                self.runtime.execute(
                    process_id=info.process_id,
                    node_id=info.current_node,
                    root_pipeline_id=info.root_pipeline_id,
                    parent_pipeline_id=info.top_pipeline_id,
                )

        self.runtime.post_resume_pipeline(pipeline_id)

    def pause_node_appoint(self, node_id: str):
        """
        预约暂停节点

        :param node_id: 节点 ID
        :type node_id: str
        """
        node = self.runtime.get_node(node_id)

        if node.type == NodeType.SubProcess:
            raise InvalidOperationError("can not use pause_node_appoint api for {}".format(node.type))

        self.runtime.pre_pause_node(node_id)

        self.runtime.set_state(node_id=node_id, to_state=states.SUSPENDED)

        self.runtime.post_pause_node(node_id)

    def resume_node_appoint(self, node_id: str):
        """
        继续由于节点暂停被阻塞的流程的执行

        :param node_id: 节点 ID
        :type node_id: str
        """
        node = self.runtime.get_node(node_id)

        if node.type == NodeType.SubProcess:
            raise InvalidOperationError("can not use pause_node_appoint api for {}".format(node.type))

        self.runtime.pre_resume_node(node_id)

        info_list = self.runtime.get_suspended_process_info(node_id)

        self.runtime.set_state(node_id=node_id, to_state=states.READY)

        # found process suspended by node suspend
        for info in info_list:
            self.runtime.resume(process_id=info.process_id)
            self.runtime.execute(
                process_id=info.process_id,
                node_id=info.current_node,
                root_pipeline_id=info.root_pipeline_id,
                parent_pipeline_id=info.top_pipeline_id,
            )

        self.runtime.post_resume_node(node_id)

    def retry_node(self, node_id: str, data: Optional[dict] = None):
        """
        重试节点

        :param node_id: 节点 ID
        :type node_id: str
        :param data: 重试时使用的输入数据, defaults to None
        :type data: Optional[dict], optional
        """
        node = self.runtime.get_node(node_id)

        if not node.can_retry:
            raise InvalidOperationError("can not retry node({}) with can_retry({})".format(node_id, node.can))

        state = self.runtime.get_state(node_id)

        process_info = self._ensure_state_is_fail_and_return_process_info(state)

        self.runtime.pre_retry_node(node_id, data)

        if data is not None:
            self.runtime.set_data_inputs(
                node_id,
                {k: DataInput(need_render=True, value=v) for k, v in data.items()},
            )

        self._add_history(node_id, state)

        self.runtime.set_state(
            node_id=node_id,
            to_state=states.READY,
            is_retry=True,
            refresh_version=True,
            clear_started_time=True,
            clear_archived_time=True,
        )

        self.runtime.execute(
            process_id=process_info.process_id,
            node_id=node_id,
            root_pipeline_id=process_info.root_pipeline_id,
            parent_pipeline_id=process_info.top_pipeline_id,
        )

        self.runtime.post_retry_node(node_id, data)

    def retry_subprocess(self, node_id: str):
        """
        重试进入失败的子流程

        :param node_id: 子流程 ID
        :type node_id: str
        :raises InvalidOperationError: [description]
        """
        node = self.runtime.get_node(node_id)

        if node.type is not NodeType.SubProcess:
            raise InvalidOperationError("node({}) type is not SubProcess".format(node_id))

        state = self.runtime.get_state(node_id)

        process_info = self._ensure_state_is_fail_and_return_process_info(state)

        self.runtime.pre_retry_subprocess(node_id)

        # reset pipeline stack
        if process_info.pipeline_stack[-1] == node_id:
            self.runtime.set_pipeline_stack(process_info.process_id, process_info.pipeline_stack[:-1])

        self._add_history(node_id, state)

        self.runtime.set_state(
            node_id=node_id,
            to_state=states.READY,
            is_retry=True,
            refresh_version=True,
            clear_started_time=True,
            clear_archived_time=True,
        )

        self.runtime.execute(
            process_id=process_info.process_id,
            node_id=node_id,
            root_pipeline_id=process_info.root_pipeline_id,
            parent_pipeline_id=process_info.top_pipeline_id,
        )

        self.runtime.post_retry_subprocess(node_id)

    def skip_node(self, node_id: str):
        """
        跳过失败的节点继续执行

        :param node_id: 节点 ID
        :type node_id: str
        :raises InvalidOperationError: [description]
        :raises InvalidOperationError: [description]
        """
        node = self.runtime.get_node(node_id)

        if not node.can_skip:
            raise InvalidOperationError("can not skip this node")

        if node.type not in self.PURE_SKIP_ENABLE_NODE_TYPE:
            raise InvalidOperationError("can not use skip_node api for {}".format(node.type))

        state = self.runtime.get_state(node_id)

        process_info = self._ensure_state_is_fail_and_return_process_info(state)

        self.runtime.pre_skip_node(node_id)

        # pure skip node type only has 1 next node
        next_node_id = node.target_nodes[0]

        self._add_history(node_id, state)

        self.runtime.set_state(
            node_id=node_id,
            to_state=states.FINISHED,
            is_skip=True,
            refresh_version=True,
            set_archive_time=True,
        )

        # 跳过节点时不再做节点输出提取到上下文的操作
        # 因为节点失败的位置未知，可能提取出来的变量是无法预知的，会导致不可预知的行为
        self.runtime.execute(
            process_id=process_info.process_id,
            node_id=next_node_id,
            root_pipeline_id=process_info.root_pipeline_id,
            parent_pipeline_id=process_info.top_pipeline_id,
        )

        self.runtime.post_skip_node(node_id)

    def skip_exclusive_gateway(self, node_id: str, flow_id: str):
        """
        跳过执行失败的分支网关继续执行

        :param node_id: 节点 ID
        :type node_id: str
        :param flow_id: 需要继续执行的流 ID
        :type flow_id: str
        :raises InvalidOperationError: [description]
        """
        node = self.runtime.get_node(node_id)

        if node.type != NodeType.ExclusiveGateway:
            raise InvalidOperationError("{} is not exclusive gateway, actual: {}".format(node_id, node.type.value))

        next_node_id = node.targets[flow_id]

        state = self.runtime.get_state(node_id)

        process_info = self._ensure_state_is_fail_and_return_process_info(state)

        self.runtime.pre_skip_exclusive_gateway(node_id, flow_id)

        self._add_history(node_id, state)

        self.runtime.set_state(
            node_id=node_id,
            to_state=states.FINISHED,
            is_skip=True,
            refresh_version=True,
            set_archive_time=True,
        )

        self.runtime.execute(
            process_id=process_info.process_id,
            node_id=next_node_id,
            root_pipeline_id=process_info.root_pipeline_id,
            parent_pipeline_id=process_info.top_pipeline_id,
        )

        self.runtime.post_skip_exclusive_gateway(node_id, flow_id)

    def skip_conditional_parallel_gateway(self, node_id: str, flow_ids: list, converge_gateway_id: str):
        """
        跳过执行失败的条件并行网关继续执行

        :param node_id: 节点 ID
        :type node_id: str
        :param flow_ids: 需要继续执行的流 ID 列表
        :type flow_ids: list
        :param converge_gateway_id: 目标汇聚网关 ID
        :type converge_gateway_id: str
        :raises InvalidOperationError: [description]
        """
        node = self.runtime.get_node(node_id)

        if node.type != NodeType.ConditionalParallelGateway:
            raise InvalidOperationError(
                "{} is not conditional parallel gateway, actual: {}".format(node_id, node.type.value)
            )

        state = self.runtime.get_state(node_id)
        process_info = self._ensure_state_is_fail_and_return_process_info(state)
        process_id = process_info.process_id

        self.runtime.pre_skip_conditional_parallel_gateway(node_id, flow_ids, converge_gateway_id)

        self.runtime.sleep(process_id)
        fork_targets = [node.targets[flow_id] for flow_id in flow_ids]
        from_to = {target: converge_gateway_id for target in fork_targets}
        dispatch_processes = self.runtime.fork(
            parent_id=process_info.process_id,
            root_pipeline_id=process_info.root_pipeline_id,
            pipeline_stack=process_info.pipeline_stack,
            from_to=from_to,
        )
        children = [d.process_id for d in dispatch_processes]
        self.runtime.join(process_id, children)
        for d in dispatch_processes:
            self.runtime.execute(
                process_id=d.process_id,
                node_id=d.node_id,
                root_pipeline_id=process_info.root_pipeline_id,
                parent_pipeline_id=process_info.top_pipeline_id,
            )

        self._add_history(node_id, state)

        self.runtime.set_state(
            node_id=node_id,
            to_state=states.FINISHED,
            is_skip=True,
            refresh_version=True,
            set_archive_time=True,
        )

        self.runtime.post_skip_conditional_parallel_gateway(node_id, flow_ids, converge_gateway_id)

    def forced_fail_activity(self, node_id: str, ex_data: str):
        """
        强制失败某个 Activity

        :param node_id: 节点 ID
        :type node_id: str
        :param ex_data: 强制失败时写入节点有慈航数据的信息
        :type ex_data: str
        :raises InvalidOperationError: [description]
        :raises InvalidOperationError: [description]
        """
        node = self.runtime.get_node(node_id)

        if node.type != NodeType.ServiceActivity:
            raise InvalidOperationError("{} is not activity, actual: {}".format(node_id, node.type.value))

        state = self.runtime.get_state(node_id)

        if state.name != states.RUNNING:
            raise InvalidOperationError("{} state is not RUNNING, actual: {}".format(node_id, state.name))

        process_id = self.runtime.get_process_id_with_current_node_id(node_id)

        if not process_id:
            raise InvalidOperationError("can not find process with current node id: {}".format(node_id))

        self.runtime.pre_forced_fail_activity(node_id, ex_data)

        outputs = self.runtime.get_execution_data_outputs(node_id)

        outputs["ex_data"] = ex_data
        outputs["_forced_failed"] = True

        old_ver = state.version
        new_ver = self.runtime.set_state(
            node_id=node_id,
            to_state=states.FAILED,
            refresh_version=True,
            set_archive_time=True,
        )

        self.runtime.set_execution_data_outputs(node_id, outputs)

        self.runtime.kill(process_id)

        self.runtime.post_forced_fail_activity(node_id, ex_data, old_ver, new_ver)

    def callback(self, node_id: str, version: str, data: dict):
        """
        回调某个节点

        :param node_id: 节点 ID
        :type node_id: str
        :param version: 回调执行版本
        :type version: str
        :param data: 回调数据
        :type data: dict
        :raises InvalidOperationError: [description]
        :raises InvalidOperationError: [description]
        :raises InvalidOperationError: [description]
        :raises InvalidOperationError: [description]
        """

        process_info = self.runtime.get_sleep_process_info_with_current_node_id(node_id)

        if not process_info:
            raise InvalidOperationError("can not find process with current node id: {}".format(node_id))

        state = self.runtime.get_state(node_id)

        schedule = self.runtime.get_schedule_with_node_and_version(node_id, version)

        if state.version != version:
            self.runtime.expire_schedule(schedule.id)
            raise InvalidOperationError("node version {} not exist".format(version))

        if schedule.finished:
            raise InvalidOperationError("scheudle is already finished")

        if schedule.expired:
            raise InvalidOperationError("scheudle is already expired")

        self.runtime.pre_callback(node_id, version, data)

        data_id = self.runtime.set_callback_data(node_id, state.version, data)

        self.runtime.schedule(process_info.process_id, node_id, schedule.id, data_id)

        self.runtime.post_callback(node_id, version, data)

    # engine event
    @setup_gauge(ENGINE_RUNNING_PROCESSES)
    @setup_histogram(ENGINE_PROCESS_RUNNING_TIME)
    def execute(self, process_id: int, node_id: str, root_pipeline_id: str, parent_pipeline_id: str):
        """
        在某个进程上从某个节点开始进入推进循环

        :param process_id: 进程 ID
        :type process_id: int
        :param node_id: 节点 ID
        :type node_id: str
        :param root_pipeline_id: 根流程 ID
        :type root_pipeline_id: str
        :param parent_pipeline_id: 父流程 ID
        :type parent_pipeline_id: str
        """
        current_node_id = node_id

        # 推进前准备
        try:
            process_info = self.runtime.get_process_info(process_id)
            self.runtime.wake_up(process_id)
        except Exception:
            ex_data = traceback.format_exc()
            logger.exception(
                "[%s]execute node(%s) prepare fail",
                root_pipeline_id,
                current_node_id,
            )

            self.runtime.sleep(process_id)

            outputs = self.runtime.get_execution_data_outputs(current_node_id)
            outputs["ex_data"] = ex_data
            self.runtime.set_execution_data_outputs(current_node_id, outputs)

            self.runtime.set_state(
                node_id=current_node_id,
                to_state=states.FAILED,
                root_id=root_pipeline_id,
                parent_id=parent_pipeline_id,
                set_started_time=True,
                set_archive_time=True,
            )

            return

        # 推进循环
        while True:
            # 进程心跳
            try:
                self.runtime.beat(process_id)
            except Exception:
                # do not fail the flow when beat failed
                logger.exception("process(%s) beat error" % process_id)

            try:
                # 遇到推进终点后需要尝试唤醒父进程
                if current_node_id == process_info.destination_id:
                    self.runtime.die(process_id)
                    wake_up_seccess = self.runtime.child_process_finish(process_info.parent_id, process_id)

                    if wake_up_seccess:

                        self.runtime.execute(
                            process_id=process_info.parent_id,
                            node_id=process_info.destination_id,
                            root_pipeline_id=process_info.root_pipeline_id,
                            parent_pipeline_id=process_info.top_pipeline_id,
                        )

                    return

                logger.info("[pipeline-trace](root_pipeline: %s) execute node %s" % (root_pipeline_id, current_node_id))
                self.runtime.set_current_node(process_id, current_node_id)

                # 冻结检测
                if self.runtime.is_frozen(process_id):
                    logger.info(
                        "root pipeline[%s] freeze at node %s",
                        process_info.root_pipeline_id,
                        current_node_id,
                    )
                    self.runtime.freeze(process_id)
                    return

                node_state_map = self.runtime.batch_get_state_name(process_info.pipeline_stack)

                # 检测根流程是否被撤销
                if node_state_map[process_info.root_pipeline_id] == states.REVOKED:
                    self.runtime.die(process_id)
                    logger.info(
                        "root pipeline[%s] revoked checked at node %s",
                        process_info.root_pipeline_id,
                        current_node_id,
                    )
                    return

                # 检测流程栈中是否有被暂停的流程
                for pid in process_info.pipeline_stack:
                    if node_state_map[pid] == states.SUSPENDED:
                        logger.info(
                            "root pipeline[%s] process %s suspended by subprocess %s",
                            process_info.root_pipeline_id,
                            process_id,
                            pid,
                        )
                        self.runtime.suspend(process_id, pid)
                        return

                node = self.runtime.get_node(current_node_id)
                node_state = self.runtime.get_state_or_none(current_node_id)
                loop = 1
                inner_loop = 1
                reset_mark_bit = False

                if node_state:
                    rerun_limit = self.runtime.node_rerun_limit(process_info.root_pipeline_id, current_node_id)
                    # 重入次数超过限制
                    if (
                        node_state.name == states.FINISHED
                        and node.type != NodeType.SubProcess
                        and node_state.loop > rerun_limit
                    ):
                        exec_outputs = self.runtime.get_execution_data_outputs(current_node_id)
                        exec_outputs["ex_data"] = "node execution exceed rerun limit {}".format(rerun_limit)

                        self.runtime.set_execution_data_outputs(current_node_id, exec_outputs)
                        self.runtime.set_state(
                            node_id=current_node_id,
                            to_state=states.FAILED,
                            set_archive_time=True,
                        )
                        self.runtime.sleep(process_id)

                        return

                    # 检测节点是否被预约暂停
                    if node_state.name == states.SUSPENDED:
                        # 预约暂停的节点在预约时获取不到 root_id 和 parent_id，故在此进行设置
                        self.runtime.set_state_root_and_parent(
                            node_id=current_node_id,
                            root_id=process_info.root_pipeline_id,
                            parent_id=process_info.top_pipeline_id,
                        )
                        self.runtime.suspend(process_id, current_node_id)
                        logger.info(
                            "root_pipeline[%s] process %s suspended by node %s",
                            process_info.root_pipeline_id,
                            process_id,
                            current_node_id,
                        )
                        return

                    # 设置状态前检测
                    if node_state.name not in states.INVERTED_TRANSITION[states.RUNNING]:
                        self.runtime.sleep(process_id)
                        return

                    if node_state.name == states.FINISHED:
                        loop = node_state.loop + 1
                        inner_loop = node_state.inner_loop + 1
                        reset_mark_bit = True

                    # 重入前记录历史
                    if node_state.name == states.FINISHED:
                        self._add_history(node_id=current_node_id, state=node_state)

                version = self.runtime.set_state(
                    node_id=current_node_id,
                    to_state=states.RUNNING,
                    loop=loop,
                    inner_loop=inner_loop,
                    root_id=process_info.root_pipeline_id,
                    parent_id=process_info.top_pipeline_id,
                    set_started_time=True,
                    reset_skip=reset_mark_bit,
                    reset_retry=reset_mark_bit,
                    reset_error_ignored=reset_mark_bit,
                    refresh_version=reset_mark_bit,
                )
                set_node_info(CurrentNodeInfo(node_id=current_node_id, version=version, loop=loop))

                logger.info(
                    "root pipeline[%s] before execute %s(%s) state: %s",
                    process_info.root_pipeline_id,
                    node.__class__.__name__,
                    current_node_id,
                    node_state,
                )
                handler = HandlerFactory.get_handler(node, self.runtime)
                type_label = self._get_metrics_node_type(node)
                execute_start = time.time()
                execute_result = handler.execute(process_info, loop, inner_loop, version)
                logger.info(
                    "root pipeline[%s] node(%s) execute result: %s",
                    process_info.root_pipeline_id,
                    node.id,
                    execute_result.__dict__,
                )

                ENGINE_NODE_EXECUTE_TIME.labels(type=type_label, hostname=self._hostname).observe(
                    time.time() - execute_start
                )

                # 进程是否要进入睡眠
                if execute_result.should_sleep:
                    self.runtime.sleep(process_id)

                # 节点是否准备好进入调度
                if execute_result.schedule_ready:
                    schedule = self.runtime.set_schedule(
                        process_id=process_id,
                        node_id=current_node_id,
                        version=version,
                        schedule_type=execute_result.schedule_type,
                    )
                    if execute_result.schedule_type == ScheduleType.POLL:
                        self.runtime.schedule(process_id, current_node_id, schedule.id)
                # 是否有待调度的子进程
                elif execute_result.dispatch_processes:
                    children = [d.process_id for d in execute_result.dispatch_processes]
                    logger.info(
                        "root pipeline[%s] with top pipeline[%s] dispatch %s children: %s",
                        process_info.root_pipeline_id,
                        process_info.top_pipeline_id,
                        len(execute_result.dispatch_processes),
                        execute_result.dispatch_processes,
                    )
                    self.runtime.join(process_id, children)
                    for d in execute_result.dispatch_processes:
                        self.runtime.execute(
                            process_id=d.process_id,
                            node_id=d.node_id,
                            root_pipeline_id=process_info.root_pipeline_id,
                            parent_pipeline_id=process_info.top_pipeline_id,
                        )

                if execute_result.should_die:
                    self.runtime.die(process_id)

                if execute_result.should_sleep or execute_result.should_die:
                    return

                current_node_id = execute_result.next_node_id
            except Exception as e:
                ex_data = traceback.format_exc()
                logger.warning(
                    "[%s]execute exception catch at node(%s): %s",
                    process_info.root_pipeline_id,
                    current_node_id,
                    ex_data,
                )

                # state version already changed, so give up this execute
                if isinstance(e, StateVersionNotMatchError):
                    logger.warning(
                        "[%s]execute exception catch StateVersionNotMatchError at node(%s): %s",
                        process_info.root_pipeline_id,
                        current_node_id,
                        ex_data,
                    )
                    return

                # make sure sleep call at first, because remain operations may have been completed in execute
                self.runtime.sleep(process_info.process_id)

                outputs = self.runtime.get_execution_data_outputs(current_node_id)
                outputs["ex_data"] = ex_data
                self.runtime.set_execution_data_outputs(current_node_id, outputs)

                self.runtime.set_state(
                    node_id=current_node_id,
                    to_state=states.FAILED,
                    root_id=process_info.root_pipeline_id,
                    parent_id=process_info.top_pipeline_id,
                    set_started_time=True,
                    set_archive_time=True,
                )

                return
            finally:
                clear_node_info()

    @setup_gauge(ENGINE_RUNNING_SCHEDULES)
    @setup_histogram(ENGINE_SCHEDULE_RUNNING_TIME)
    def schedule(
        self,
        process_id: int,
        node_id: str,
        schedule_id: str,
        callback_data_id: Optional[int] = None,
    ):
        """
        在某个进程上开始某个节点的调度

        :param process_id: 进程 ID
        :type process_id: int
        :param node_id: 节点 ID
        :type node_id: str
        :param schedule_id: 调度对象 ID
        :type schedule_id: str
        :param callback_data_id: 回调数据 ID, defaults to None
        :type callback_data_id: Optional[int], optional
        """
        root_pipeline_id = ""
        try:
            process_info = self.runtime.get_process_info(process_id)
            root_pipeline_id = process_info.root_pipeline_id

            state = self.runtime.get_state(node_id)
            schedule = self.runtime.get_schedule(schedule_id)

            # engine context prepare
            set_node_info(CurrentNodeInfo(node_id=node_id, version=state.version, loop=state.loop))

            # schedule alredy finished
            if schedule.finished:
                logger.warning(
                    "root pipeline[%s] schedule(%s) %s with version %s already finished",
                    root_pipeline_id,
                    schedule_id,
                    node_id,
                    schedule.version,
                )
                return

            # 检查 schedule 是否过期
            if state.version != schedule.version:
                logger.info(
                    "root pipeline[%s] schedule(%s) %s with version %s expired, current version: %s",
                    root_pipeline_id,
                    schedule_id,
                    node_id,
                    schedule.version,
                    state.version,
                )
                self.runtime.expire_schedule(schedule_id)
                return

            # 检查节点状态是否合法
            if state.name != states.RUNNING:
                logger.info(
                    "root pipeline[%s] schedule(%s) %s with version %s state is not running: %s",
                    root_pipeline_id,
                    schedule_id,
                    node_id,
                    schedule.version,
                    state.name,
                )
                self.runtime.expire_schedule(schedule_id)
                return

            # try to get lock
            lock_get = self.runtime.apply_schedule_lock(schedule_id)

            if not lock_get:
                # only retry at multiple calback type
                if schedule.type is not ScheduleType.MULTIPLE_CALLBACK:
                    logger.info(
                        "root pipeline[%s] schedule(%s) %s with version %s is not multiple callback type, will not retry to get lock",  # noqa
                        root_pipeline_id,
                        schedule_id,
                        node_id,
                        schedule.version,
                    )
                    return

                try_after = random.randint(1, 5)
                logger.info(
                    "root pipeline[%s] schedule(%s) lock %s with data %s fetch fail, try after %s",
                    root_pipeline_id,
                    node_id,
                    schedule_id,
                    callback_data_id,
                    try_after,
                )
                self.runtime.set_next_schedule(
                    process_id=process_id,
                    node_id=node_id,
                    schedule_id=schedule_id,
                    callback_data_id=callback_data_id,
                    schedule_after=try_after,
                )
                return

            logger.info(
                "[pipeline-trace](root_pipeline: %s) schedule node %s with version %s"
                % (root_pipeline_id, node_id, schedule.version)
            )
            with self._schedule_lock_keeper(schedule_id):
                # 进程心跳
                self.runtime.beat(process_id)

                # fetch callback data
                callback_data = None
                if callback_data_id:
                    callback_data = self.runtime.get_callback_data(callback_data_id)

                # fetch node info and start schedule
                node = self.runtime.get_node(node_id)
                handler = HandlerFactory.get_handler(node, self.runtime)
                type_label = self._get_metrics_node_type(node)

                logger.info(
                    "root pipeline[%s] before schedule node %s with data %s",
                    root_pipeline_id,
                    node,
                    callback_data,
                )
                schedule_start = time.time()
                schedule_result = handler.schedule(process_info, state.loop, state.inner_loop, schedule, callback_data)
                ENGINE_NODE_SCHEDULE_TIME.labels(type=type_label, hostname=self._hostname).observe(
                    time.time() - schedule_start
                )
                logger.info(
                    "root pipeline[%s] node(%s) schedule result: %s",
                    process_info.root_pipeline_id,
                    node.id,
                    schedule_result.__dict__,
                )

                if schedule_result.has_next_schedule:
                    self.runtime.set_next_schedule(
                        process_info.process_id,
                        node_id,
                        schedule_id,
                        schedule_result.schedule_after,
                    )

                if schedule_result.schedule_done:
                    self.runtime.finish_schedule(schedule_id)
                    self.runtime.execute(
                        process_id=process_id,
                        node_id=schedule_result.next_node_id,
                        root_pipeline_id=process_info.root_pipeline_id,
                        parent_pipeline_id=process_info.top_pipeline_id,
                    )
        except Exception as e:
            ex_data = traceback.format_exc()
            logger.warning(
                "root pipeline[%s] schedule exception catch at node(%s): %s",
                root_pipeline_id,
                node_id,
                ex_data,
            )

            # state version already changed, so give up this schedule
            if isinstance(e, StateVersionNotMatchError):
                logger.exception(
                    "root pipeline[%s] schedule exception catch StateVersionNotMatchError at node(%s): %s",
                    root_pipeline_id,
                    node_id,
                    ex_data,
                )
                return

            # make sure release_schedule_lock call at first,
            # because remain operations may have been completed in execute
            self.runtime.release_schedule_lock(schedule_id)

            outputs = self.runtime.get_execution_data_outputs(node_id)
            outputs["ex_data"] = ex_data
            self.runtime.set_execution_data_outputs(node_id, outputs)

            self.runtime.set_state(node_id=node_id, to_state=states.FAILED, set_archive_time=True)
        finally:
            clear_node_info()

    # help method
    @contextmanager
    def _schedule_lock_keeper(self, schedule_id: int):
        yield
        self.runtime.release_schedule_lock(schedule_id)

    def _add_history(
        self,
        node_id: str,
        state: Optional[State] = None,
        exec_data: Optional[ExecutionData] = None,
    ) -> int:
        if not state:
            state = self.runtime.get_state(node_id)

        if not exec_data:
            try:
                exec_data = self.runtime.get_execution_data(node_id)
            except NotFoundError:
                # execution data may be lack with some node
                logger.warning("can't not find execution data for %s at loop %s" % (node_id, state.loop))
                history_inputs = {}
                history_outputs = {}
            else:
                history_inputs = exec_data.inputs
                history_outputs = exec_data.outputs

        return self.runtime.add_history(
            node_id=node_id,
            started_time=state.started_time,
            archived_time=state.archived_time,
            loop=state.loop,
            skip=state.skip,
            retry=state.retry,
            version=state.version,
            inputs=history_inputs,
            outputs=history_outputs,
        )

    def _ensure_state_is_fail_and_return_process_info(self, state: State) -> str:
        if state.name != states.FAILED:
            raise InvalidOperationError("{} state is not FAILED, actual {}".format(state.node_id, state.name))

        process_info = self.runtime.get_sleep_process_info_with_current_node_id(state.node_id)

        if not process_info:
            raise InvalidOperationError("can not find sleep process with current node id: {}".format(state.node_id))

        return process_info

    def _get_metrics_node_type(self, node: Node) -> str:
        if node.type != NodeType.ServiceActivity:
            return get_lower_case_name(node.type.value)

        return "{}_{}".format(node.code, node.version)
