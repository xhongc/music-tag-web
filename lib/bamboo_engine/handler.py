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

# 节点处理器逻辑封装模块

from typing import Optional, List
from abc import ABCMeta, abstractmethod

from bamboo_engine import states

from .eri import (
    EngineRuntimeInterface,
    Node,
    Schedule,
    CallbackData,
    ScheduleType,
    DispatchProcess,
    ProcessInfo,
    NodeType,
)
from .exceptions import NotFoundError, InvalidOperationError


def register_handler(type: NodeType):
    """
    节点 Handler 注册函数

    :param type: 节点类型
    :type type: NodeType
    """

    def register(cls):
        HandlerFactory.add_handler(type, cls)
        return cls

    return register


class ExecuteResult:
    """
    Handler execute 方法返回的结果
    """

    def __init__(
        self,
        should_sleep: bool,
        schedule_ready: bool,
        schedule_type: Optional[ScheduleType],
        schedule_after: int,
        dispatch_processes: List[DispatchProcess],
        next_node_id: Optional[str],
        should_die: bool = False,
    ):
        """

        :param should_sleep: 当前进程是否应该进入休眠
        :type should_sleep: bool
        :param schedule_ready: 被处理的节点是否准备好进入调度
        :type schedule_ready: bool
        :param schedule_type: 被处理的节点的调度类型
        :type schedule_type: Optional[ScheduleType]
        :param schedule_after: 在 schedule_after 秒后开始执行调度
        :type schedule_after: int
        :param dispatch_processes: 需要派发的子进程信息列表
        :type dispatch_processes: List[DispatchProcess]
        :param next_node_id: 推进循环中下一个要处理的节点的 ID
        :type next_node_id: Optional[str]
        :param should_die: 当前进程是否需要进入死亡状态, defaults to False
        :type should_die: bool, optional
        """
        self.should_sleep = should_sleep
        self.schedule_ready = schedule_ready
        self.schedule_type = schedule_type
        self.schedule_after = schedule_after
        self.dispatch_processes = dispatch_processes
        self.next_node_id = next_node_id
        self.should_die = should_die


class ScheduleResult:
    """
    Handler schedule 方法返回的结果
    """

    def __init__(
        self,
        has_next_schedule: bool,
        schedule_after: int,
        schedule_done: bool,
        next_node_id: Optional[str],
    ):
        """

        :param has_next_schedule: 是否还有下次调度
        :type has_next_schedule: bool
        :param schedule_after: 在 schedule_after 秒后开始下次调度
        :type schedule_after: int
        :param schedule_done: 调度是否完成
        :type schedule_done: bool
        :param next_node_id: 调度完成后下一个需要执行的节点的 ID
        :type next_node_id: Optional[str]
        """
        self.has_next_schedule = has_next_schedule
        self.schedule_after = schedule_after
        self.schedule_done = schedule_done
        self.next_node_id = next_node_id


class NodeHandler(metaclass=ABCMeta):
    """
    节点处理器，负责封装不同类型节点的 execute 和 schedule 逻辑
    """

    LOOP_KEY = "_loop"
    INNER_LOOP_KEY = "_inner_loop"

    def __init__(self, node: Node, runtime: EngineRuntimeInterface):
        """

        :param node: 节点实例
        :type node: Node
        :param runtime: 引擎运行时实例
        :type runtime: EngineRuntimeInterface
        """
        self.node = node
        self.runtime = runtime

    @abstractmethod
    def execute(self, process_info: ProcessInfo, loop: int, inner_loop: int, version: str) -> ExecuteResult:
        """
        节点的 execute 处理逻辑

        :param process_info: 进程信息
        :type process_id: ProcessInfo
        :param loop: 重入次数
        :type loop: int
        :param inner_loop: 当前流程重入次数
        :type inner_loop: int
        :param version: 执行版本
        :type version: str
        :return: 执行结果
        :rtype: ExecuteResult
        """

    def schedule(
        self,
        process_info: ProcessInfo,
        loop: int,
        inner_loop: int,
        schedule: Schedule,
        callback_data: Optional[CallbackData] = None,
    ) -> ScheduleResult:
        """
        节点的 schedule 处理逻辑，不支持 schedule 的节点可以不实现该方法

        :param process_info: 进程信息
        :type process_id: ProcessInfo
        :param loop: 重入次数
        :type loop: int
        :param inner_loop: 当前流程重入次数
        :type inner_loop: int
        :param schedule: Schedule 实例
        :type schedule: Schedule
        :param callback_data: 回调数据, defaults to None
        :type callback_data: Optional[CallbackData], optional
        :return: 调度结果
        :rtype: ScheduleResult
        """
        raise NotImplementedError()

    def _execute_fail(self, ex_data: str) -> ExecuteResult:
        exec_outputs = self.runtime.get_execution_data_outputs(self.node.id)

        self.runtime.set_state(node_id=self.node.id, to_state=states.FAILED, set_archive_time=True)

        exec_outputs["ex_data"] = ex_data

        self.runtime.set_execution_data_outputs(self.node.id, exec_outputs)

        return ExecuteResult(
            should_sleep=True,
            schedule_ready=False,
            schedule_type=None,
            schedule_after=-1,
            dispatch_processes=[],
            next_node_id=None,
        )

    def _get_plain_inputs(self, node_id: str):
        return {key: di.value for key, di in self.runtime.get_data_inputs(node_id).items()}


class HandlerFactory:
    """
    节点处理器工厂
    """

    _handlers = {}

    @classmethod
    def add_handler(cls, type: NodeType, handler_cls):
        """
        向工厂中注册某个类型节点的处理器

        :param type: 节点类型
        :type type: NodeType
        :param handler_cls: [description]
        :type handler_cls: [type]
        :raises InvalidOperationError: [description]
        """
        if not issubclass(handler_cls, NodeHandler):
            raise InvalidOperationError(
                "register handler err: {} is not subclass of {}".format(handler_cls, "NodeHandler")
            )
        cls._handlers[type.value] = handler_cls

    @classmethod
    def get_handler(cls, node: Node, runtime: EngineRuntimeInterface) -> NodeHandler:
        """
        获取某个节点的处理器实例

        :param node: 节点实例
        :type node: NodeType
        :param runtime: 引擎运行时实例
        :type runtime: EngineRuntimeInterface
        :raises NotFoundError: [description]
        :return: 节点处理器实例
        :rtype: NodeHandler
        """
        if node.type.value not in cls._handlers:
            raise NotFoundError("can not find handler for {} type node".format(node.type.value))

        return cls._handlers[node.type.value](node, runtime)
