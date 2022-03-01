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

from datetime import datetime
from abc import ABCMeta, abstractmethod
from typing import List, Optional, Dict, Set, Any

from .models import (
    State,
    Node,
    Schedule,
    ScheduleType,
    Data,
    DataInput,
    ExecutionData,
    ExecutionHistory,
    ExecutionShortHistory,
    CallbackData,
    ProcessInfo,
    SuspendedProcessInfo,
    DispatchProcess,
    ContextValue,
)

# plugin interface

__version__ = "5.0.0"


def version():
    return __version__


class Service(metaclass=ABCMeta):
    """
    服务对象接口
    """

    def pre_execute(self, data: ExecutionData, root_pipeline_data: ExecutionData):
        """
        execute 执行前执行的逻辑

        :param data: 节点执行数据
        :type data: ExecutionData
        :param root_pipeline_data: 根流程执行数据
        :type root_pipeline_data: ExecutionData
        """

    @abstractmethod
    def execute(self, data: ExecutionData, root_pipeline_data: ExecutionData) -> bool:
        """
        execute 逻辑

        :param data: 节点执行数据
        :type data: ExecutionData
        :param root_pipeline_data: 根流程执行数据
        :type root_pipeline_data: ExecutionData
        :return: 是否执行成功
        :rtype: bool
        """

    @abstractmethod
    def schedule(
        self,
        schedule: Schedule,
        data: ExecutionData,
        root_pipeline_data: ExecutionData,
        callback_data: Optional[CallbackData] = None,
    ) -> bool:
        """
        schedule 逻辑

        :param schedule: Schedule 对象
        :type schedule: Schedule
        :param data: 节点执行数据
        :type data: ExecutionData
        :param root_pipeline_data: 根流程执行数据
        :type root_pipeline_data: ExecutionData
        :param callback_data: 回调数据, defaults to None
        :type callback_data: Optional[CallbackData], optional
        :return: [description]
        :rtype: bool
        """

    @abstractmethod
    def need_schedule(self) -> bool:
        """
        服务是否需要调度

        :return: 是否需要调度
        :rtype: bool
        """

    @abstractmethod
    def schedule_type(self) -> Optional[ScheduleType]:
        """
        服务调度类型

        :return: 调度类型
        :rtype: Optional[ScheduleType]
        """

    @abstractmethod
    def is_schedule_done(self) -> bool:
        """
        调度是否完成

        :return: 调度是否完成
        :rtype: bool
        """

    @abstractmethod
    def schedule_after(
        self,
        schedule: Optional[Schedule],
        data: ExecutionData,
        root_pipeline_data: ExecutionData,
    ) -> int:
        """
        计算下一次调度间隔

        :param schedule: 调度对象，未进行调度时传入为空
        :type schedule: Optional[Schedule]
        :param data: 节点执行数据
        :type data: ExecutionData
        :param root_pipeline_data: 根流程执行数据
        :type root_pipeline_data: ExecutionData
        :return: 调度间隔，单位为秒
        :rtype: int
        """

    @abstractmethod
    def setup_runtime_attributes(self, **attrs):
        """
        装载运行时属性

        :param attrs: 运行时属性
        :type attrs: Dict[str, Any]
        """


class ExecutableEvent(metaclass=ABCMeta):
    """
    可执行结束节点接口
    """

    @abstractmethod
    def execute(pipeline_stack: List[str], root_pipeline_id: str):
        """
        execute 逻辑

        :param pipeline_stack: 流程栈
        :type pipeline_stack: List[str]
        :param root_pipeline_id: 根流程 ID
        :type root_pipeline_id: str
        """


class Variable(metaclass=ABCMeta):
    """
    变量接口
    """

    @abstractmethod
    def get(self) -> Any:
        """
        获取变量值

        :return: 变量值
        :rtype: Any
        """


# runtime interface


class PluginManagerMixin:
    """
    插件管理接口，声明了插件（服务，可执行结束节点，变量）管理相关的接口
    """

    @abstractmethod
    def get_service(self, code: str, version: str) -> Service:
        """
        根据代号与版本获取特定服务对象实例

        :param code: 服务唯一代号
        :type code: str
        :param version: 服务版本
        :type version: str
        :return: 服务对象实例
        :rtype: Service
        """

    @abstractmethod
    def get_executable_end_event(self, code: str) -> ExecutableEvent:
        """
        根据代号获取特定可执行结束事件实例

        :param code: 可执行结束事件唯一代号
        :type code: str
        :return: 可执行结束事件实例
        :rtype: ExecutableEvent:
        """

    @abstractmethod
    def get_compute_variable(
        self,
        code: str,
        key: str,
        value: Variable,
        additional_data: dict,
    ) -> Variable:
        """
        根据代号获取变量实例

        :param code: 唯一代号
        :type code: str
        :param key: 变量 key
        :type key: str
        :param value: 变量配置
        :type value: Any
        :param additional_data: 额外数据字典
        :type additional_data: dict
        :return: 变量实例
        :rtype: Variable
        """


class EngineAPIHooksMixin:
    """
    引擎 API 执行时调用的钩子相关接口声明
    """

    def pre_prepare_run_pipeline(
        self, pipeline: dict, root_pipeline_data: dict, root_pipeline_context: dict, subprocess_context: dict, **options
    ):
        """
        调用 pre_prepare_run_pipeline 前执行的钩子

        :param pipeline: 流程描述对象
        :type pipeline: dict
        :param root_pipeline_data 根流程数据
        :type root_pipeline_data: dict
        :param root_pipeline_context 根流程上下文
        :type root_pipeline_context: dict
        :param subprocess_context 子流程预置流程上下文
        :type subprocess_context: dict
        """

    def post_prepare_run_pipeline(
        self, pipeline: dict, root_pipeline_data: dict, root_pipeline_context: dict, subprocess_context: dict, **options
    ):
        """
        调用 pre_prepare_run_pipeline 后执行的钩子

        :param pipeline: 流程描述对象
        :type pipeline: dict
        :param root_pipeline_data 根流程数据
        :type root_pipeline_data: dict
        :param root_pipeline_context 根流程上下文
        :type root_pipeline_context: dict
        :param subprocess_context 子流程预置流程上下文
        :type subprocess_context: dict
        """

    def pre_pause_pipeline(self, pipeline_id: str):
        """
        暂停 pipeline 前执行的钩子

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        """

    def post_pause_pipeline(self, pipeline_id: str):
        """
        暂停 pipeline 后执行的钩子

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        """

    def pre_revoke_pipeline(self, pipeline_id: str):
        """
        撤销 pipeline 前执行的钩子

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        """

    def post_revoke_pipeline(self, pipeline_id: str):
        """
        撤销 pipeline 后执行的钩子

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        """

    def pre_resume_pipeline(self, pipeline_id: str):
        """
        继续 pipeline 前执行的钩子

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        """

    def post_resume_pipeline(self, pipeline_id: str):
        """
        继续 pipeline 后执行的钩子

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        """

    def pre_resume_node(self, node_id: str):
        """
        继续节点后执行的钩子

        :param node_id: 节点 ID
        :type node_id: str
        """

    def post_resume_node(self, node_id: str):
        """
        继续节点后执行的钩子

        :param node_id: [description]节点 ID
        :type node_id: str
        """

    def pre_pause_node(self, node_id: str):
        """
        暂停节点前执行的钩子

        :param node_id: 节点 ID
        :type node_id: str
        """

    def post_pause_node(self, node_id: str):
        """
        暂停节点后执行的钩子

        :param node_id: [description]节点 ID
        :type node_id: str
        """

    def pre_retry_node(self, node_id: str, data: Optional[dict]):
        """
        重试节点前执行的钩子

        :param node_id: 节点 ID
        :type node_id: str
        :param data: 重试时使用的节点执行输入
        :type data: Optional[dict]
        """

    def post_retry_node(self, node_id: str, data: Optional[dict]):
        """
        重试节点后执行的钩子

        :param node_id: 节点 ID
        :type node_id: str
        :param data: 重试时使用的节点执行输入
        :type data: Optional[dict]
        """

    def pre_skip_node(self, node_id: str):
        """
        跳过节点前执行的钩子

        :param node_id: 节点 ID
        :type node_id: str
        """

    def post_skip_node(self, node_id: str):
        """
        跳过节点后执行的钩子

        :param node_id: 节点 ID
        :type node_id: str
        """

    def pre_skip_exclusive_gateway(self, node_id: str, flow_id: str):
        """
        跳过分支网关前执行的钩子

        :param node_id: 节点 ID
        :type node_id: str
        :param flow_id: 跳过后选择的目标流 ID
        :type flow_id: str
        """

    def post_skip_exclusive_gateway(self, node_id: str, flow_id: str):
        """
        跳过分支网关后执行的钩子

        :param node_id: 节点 ID
        :type node_id: str
        :param flow_id: 跳过后选择的目标流 ID
        :type flow_id: str
        """

    def pre_skip_conditional_parallel_gateway(self, node_id: str, flow_ids: list, converge_gateway_id: str):
        """
        跳过条件并行网关前执行的钩子

        :param node_id: 节点 ID
        :type node_id: str
        :param flow_ids: 跳过后选择的目标流 ID 列表
        :type flow_ids: list
        :param converge_gateway_id: 目标汇聚网关 ID
        :type converge_gateway_id: str
        """

    def post_skip_conditional_parallel_gateway(self, node_id: str, flow_ids: list, converge_gateway_id: str):
        """
        跳过条件并行网关后执行的钩子

        :param node_id: 节点 ID
        :type node_id: str
        :param flow_ids: 跳过后选择的目标流 ID 列表
        :type flow_ids: list
        :param converge_gateway_id: 目标汇聚网关 ID
        :type converge_gateway_id: str
        """

    def pre_forced_fail_activity(self, node_id: str, ex_data: str):
        """
        强制失败节点前执行的钩子

        :param node_id: 节点 ID
        :type node_id: str
        :param ex_data: 写入节点执行数据的失败信息
        :type ex_data: str
        """

    def post_forced_fail_activity(self, node_id: str, ex_data: str, old_version: str, new_version: str):
        """
        强制失败节点后执行的钩子

        :param node_id: 节点 ID
        :type node_id: str
        :param ex_data: 写入节点执行数据的失败信息
        :type ex_data: str
        :param old_version: 强制失败前的节点版本
        :type old_version: str
        :param new_version: 强制失败后的节点版本
        :type new_version: str
        """

    def pre_callback(self, node_id: str, version: str, data: str):
        """
        回调节点前执行的钩子

        :param node_id: 节点 ID
        :type node_id: str
        :param version: 节点执行版本
        :type version: str
        :param data: 回调数据
        :type data: str
        """

    def post_callback(self, node_id: str, version: str, data: str):
        """
        回调节点后执行的钩子

        :param node_id: 节点 ID
        :type node_id: str
        :param version: 节点执行版本
        :type version: str
        :param data: 回调数据
        :type data: str
        """

    def pre_retry_subprocess(self, node_id: str):
        """
        子流程重试前执行的钩子

        :param node_id: 子流程节点 ID
        :type node_id: str
        """

    def post_retry_subprocess(self, node_id: str):
        """
        子流程重试后执行的钩子

        :param node_id: 子流程节点 ID
        :type node_id: str
        """


class TaskMixin:
    """
    引擎任务派发相关接口
    """

    @abstractmethod
    def execute(self, process_id: int, node_id: str, root_pipeline_id: str, parent_pipeline_id: str):
        """
        派发执行任务，执行任务被拉起执行时应该调用 Engine 实例的 execute 方法

        :param process_id: 进程 ID
        :type process_id: int
        :param node_id: 节点 ID
        :type node_id: str
        :param root_pipeline_id: 根流程 ID
        :type root_pipeline_id: str
        :param parent_pipeline_id: 父流程 ID
        :type parent_pipeline_id: str
        """

    @abstractmethod
    def schedule(
        self,
        process_id: int,
        node_id: str,
        schedule_id: str,
        callback_data_id: Optional[int] = None,
    ):
        """
        派发调度任务，调度任务被拉起执行时应该调用 Engine 实例的 schedule 方法

        :param process_id: 进程 ID
        :type process_id: int
        :param node_id: 节点 ID
        :type node_id: str
        :param schedule_id: 调度 ID
        :type schedule_id: str
        :param callback_data_id: 回调数据, defaults to None
        :type callback_data_id: Optional[int], optional
        """

    @abstractmethod
    def set_next_schedule(
        self,
        process_id: int,
        node_id: str,
        schedule_id: str,
        schedule_after: int,
        callback_data_id: Optional[int] = None,
    ):
        """
        设置下次调度时间，调度倒数归零后应该执行 Engine 实例的 schedule 方法

        :param process_id: 进程 ID
        :type process_id: int
        :param node_id: 节点 ID
        :type node_id: str
        :param schedule_id: 调度 ID
        :type schedule_id: str
        :param schedule_after: 调度倒数
        :type schedule_after: int
        :param callback_data_id: 回调数据, defaults to None
        :type callback_data_id: Optional[int], optional
        """

    @abstractmethod
    def start_timeout_monitor(self, process_id: int, node_id: str, version: str, timeout: int):
        """
        开始对某个节点执行的超时监控，若超时时间归零后节点未进入归档状态，则强制失败该节点

        :param process_id: 进程 ID
        :type process_id: int
        :param node_id: 节点 ID
        :type node_id: str
        :param version: 执行版本
        :type version: str
        :param timeout: 超时时间，单位为秒
        :type timeout: int
        """

    @abstractmethod
    def stop_timeout_monitor(
        self,
        process_id: int,
        node_id: str,
        version: str,
    ):
        """
        停止对某个节点的超时监控

        :param process_id: 进程 ID
        :type process_id: int
        :param node_id: 节点 ID
        :type node_id: str
        :param version: 执行版本
        :type version: str
        """


class ProcessMixin:
    """
    进程相关接口
    """

    @abstractmethod
    def beat(self, process_id: int):
        """
        进程心跳

        :param process_id: 进程 ID
        :type process_id: int
        """

    @abstractmethod
    def wake_up(self, process_id: int):
        """
        将当前进程标记为唤醒状态

        :param process_id: 进程 ID
        :type process_id: int
        """

    @abstractmethod
    def sleep(self, process_id: int):
        """
        将当前进程标记为睡眠状态

        :param process_id: 进程 ID
        :type process_id: int
        """

    @abstractmethod
    def suspend(self, process_id: int, by: str):
        """
        将当前进程标记为阻塞状态

        :param process_id: 进程 ID
        :type process_id: int
        :param by: 造成阻塞的节点信息
        :type by: str
        """

    @abstractmethod
    def resume(self, process_id: int):
        """
        将进程标记为非阻塞状态

        :param process_id: 进程 ID
        :type process_id: int
        """

    @abstractmethod
    def batch_resume(self, process_id_list: List[int]):
        """
        批量将进程标记为非阻塞状态

        :param process_id_list: 进程 ID 列表
        :type process_id_list: List[int]
        """

    @abstractmethod
    def die(self, process_id: int):
        """
        将当前进程标记为非存活状态

        :param process_id: 进程 ID
        :type process_id: int
        """

    @abstractmethod
    def get_process_info(self, process_id: int) -> ProcessInfo:
        """
        获取某个进程的基本信息

        :param process_id: 进程 ID
        :type process_id: int
        :return: 进程基本信息
        :rtype: ProcessInfo
        """

    @abstractmethod
    def get_process_info_with_root_pipeline(self, pipeline_id: str) -> List[ProcessInfo]:
        """
        根据根流程 ID 获取一批进程的信息

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        :return: 进程基本信息
        :rtype: List[ProcessInfo]
        """

    @abstractmethod
    def kill(self, process_id: int):
        """
        强制结束某个进程正在进行的活动，并将其标志为睡眠状态

        :param process_id: 进程 ID
        :type process_id: int
        """

    @abstractmethod
    def get_suspended_process_info(self, suspended_by: str) -> List[SuspendedProcessInfo]:
        """
        获取由于 pipeline 暂停而被暂停执行的进程信息

        : param suspended_by: 进程 ID
        : type suspended_by: str
        : return: 暂停的进程信息
        : rtype: SuspendedProcessInfo
        """

    @abstractmethod
    def get_sleep_process_info_with_current_node_id(self, node_id: str) -> Optional[ProcessInfo]:
        """
        获取由于处于睡眠状态且当前节点 ID 为 node_id 的进程 ID

        : param node_id: 节点 ID
        : type node_id: str
        : return: 进程 ID
        : rtype: str
        """

    @abstractmethod
    def get_process_id_with_current_node_id(self, node_id: str) -> Optional[int]:
        """
        获取当前节点 ID 为 node_id 且存活的进程 ID

        : param node_id: 节点 ID
        : type node_id: str
        : return: 进程 ID
        : rtype: str
        """

    @abstractmethod
    def set_current_node(self, process_id: int, node_id: str):
        """
        将进程当前处理节点标记为 node

        :param process_id: 进程 ID
        :type process_id: int
        :param node_id: 节点 ID
        :type node_id: str
        """

    @abstractmethod
    def child_process_finish(self, parent_id: int, process_id: int) -> bool:
        """
        标记某个进程的子进程执行完成，并返回是否能够唤醒父进程继续执行的标志位

        :param parent_id: 父进程 ID
        :type parent_id: int
        :param process_id: 子进程 ID
        :type process_id: int
        :return: 是否能够唤醒父进程继续执行
        :rtype: bool
        """

    @abstractmethod
    def is_frozen(self, process_id: int) -> bool:
        """
        检测当前进程是否需要被冻结

        :param process_id: 进程 ID
        :type process_id: int
        :return: 是否需要被冻结
        :rtype: bool
        """

    @abstractmethod
    def freeze(self, process_id: int):
        """
        冻结当前进程

        :param process_id: 进程 ID
        :type process_id: int
        """

    @abstractmethod
    def fork(
        self,
        parent_id: str,
        root_pipeline_id: str,
        pipeline_stack: List[str],
        from_to: Dict[str, str],
    ) -> List[DispatchProcess]:
        """
        根据当前进程 fork 出多个子进程

        :param parent_id: 父进程 ID
        :type parent_id: str
        :param root_pipeline_id: 根流程 ID
        :type root_pipeline_id: str
        :param pipeline_stack: 子流程栈
        :type pipeline_stack: List[str]
        :param from_to: 子进程的执行开始节点和目标节点
        :type from_to: Dict[str, str]
        :return: 待调度进程信息列表
        :rtype: List[DispatchProcess]
        """

    @abstractmethod
    def join(self, process_id: int, children_id: List[str]):
        """
        让父进程等待子进程

        :param process_id: 父进程 ID
        :type process_id: int
        :param children_id: 子进程 ID 列表
        :type children_id: List[str]
        """

    @abstractmethod
    def set_pipeline_stack(self, process_id: int, stack: List[str]):
        """
        设置进程的流程栈

        :param process_id: 进程 ID
        :type process_id: int
        :param stack: 流程栈
        :type stack: List[str]
        """


class StateMixin:
    """
    状态相关接口
    """

    @abstractmethod
    def get_state(self, node_id: str) -> State:
        """
        获取某个节点的状态对象

        : param node_id: 节点 ID
        : type node_id: str
        : return: State 实例
        : rtype: State
        """

    @abstractmethod
    def get_state_or_none(self, node_id: str) -> Optional[State]:
        """
        获取某个节点的状态对象，如果不存在则返回 None

        : param node_id: 节点 ID
        : type node_id: str
        : return: State 实例
        : rtype: State
        """

    @abstractmethod
    def get_state_by_root(self, root_id: str) -> List[State]:
        """
        根据根节点 ID 获取一批节点状态

        :param root_id: 根节点 ID
        :type root_id: str
        :return: 节点状态列表
        :rtype: List[State]
        """

    @abstractmethod
    def get_state_by_parent(self, parent_id: str) -> List[State]:
        """
        根据父节点 ID 获取一批节点状态

        :param parent_id: 父节点 ID
        :type parent_id: str
        :return: 节点状态列表
        :rtype: List[State]
        """

    @abstractmethod
    def batch_get_state_name(self, node_id_list: List[str]) -> Dict[str, str]:
        """
        批量获取一批节点的状态

        :param node_id_list: 节点 ID 列表
        :type node_id_list: List[str]
        :return: 节点ID -> 状态名称
        :rtype: Dict[str, str]
        """

    @abstractmethod
    def has_state(self, node_id: str) -> bool:
        """
        是否存在某个节点的的状态

        :param node_id: 节点 ID
        :type node_id: str
        :return: 该节点状态是否存在
        :rtype: bool
        """

    @abstractmethod
    def reset_state_inner_loop(self, node_id: str) -> str:
        """
        设置节点的当前流程重入次数

        :param node_id: 节点 ID
        :type node_id: str
        """

    @abstractmethod
    def reset_children_state_inner_loop(self, node_id: str):
        """
        批量设置子流程节点的所有子节点inner_loop次数

        :param node_id: 子流程节点 ID
        :type node_id: str
        """

    @abstractmethod
    def set_state(
        self,
        node_id: str,
        to_state: str,
        loop: int = -1,
        inner_loop: int = -1,
        version: str = None,
        root_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        is_retry: bool = False,
        is_skip: bool = False,
        reset_retry: bool = False,
        reset_skip: bool = False,
        error_ignored: bool = False,
        reset_error_ignored: bool = False,
        refresh_version: bool = False,
        clear_started_time: bool = False,
        set_started_time: bool = False,
        clear_archived_time: bool = False,
        set_archive_time: bool = False,
    ) -> str:
        """
        设置节点的状态，如果节点存在，进行状态转换时需要满足状态转换状态机

        :param node_id: 节点 ID
        :type node_id: str
        :param to_state: 目标状态
        :type to_state: str
        :param loop: 循环次数, 为 -1 时表示不设置
        :type loop: int, optional
        :param inner_loop: 当前流程循环次数, 为 -1 时表示不设置
        :type inner_loop: int, optional
        :param version: 目标状态版本，为空时表示不做版本校验
        :type version: Optional[str], optional
        :param root_id: 根节点 ID，为空时表示不设置
        :type root_id: Optional[str], optional
        :param parent_id: 父节点 ID，为空时表示不设置
        :type parent_id: Optional[str], optional
        :param is_retry: 是否增加重试次数
        :type is_retry: bool, optional
        :param is_skip: 是否将跳过设置为 True
        :type is_skip: bool, optional
        :param reset_retry: 是否重置重试次数
        :type reset_retry: bool, optional
        :param reset_skip: 是否重置跳过标志
        :type reset_skip: bool, optional
        :param error_ignored: 是否为忽略错误跳过
        :type error_ignored: bool, optional
        :param reset_error_ignored: 是否重置忽略错误标志
        :type reset_error_ignored: bool, optional
        :param refresh_version: 是否刷新版本号
        :type refresh_version: bool, optional
        :param clear_started_time: 是否清空开始时间
        :type clear_started_time: bool, optional
        :param set_started_time: 是否设置开始时间
        :type set_started_time: bool, optional
        :param clear_archived_time: 是否清空归档时间
        :type clear_archived_time: bool, optional
        :param set_archive_time: 是否设置归档时间
        :type set_archive_time: bool, optional
        :return: 该节点最新版本
        :rtype: str
        """

    @abstractmethod
    def set_state_root_and_parent(self, node_id: str, root_id: str, parent_id: str):
        """
        设置节点的根流程和父流程 ID

        :param node_id: 节点 ID
        :type node_id: str
        :param root_id: 根流程 ID
        :type root_id: str
        :param parent_id: 父流程 ID
        :type parent_id: str
        """


class NodeMixin:
    """
    节点相关接口
    """

    @abstractmethod
    def get_node(self, node_id: str) -> Node:
        """
        获取某个节点的详细信息

        :param node_id: 节点 ID
        :type node_id: str
        :return: Node 实例
        :rtype: Node
        """


class ScheduleMixin:
    """
    调度实例相关接口
    """

    @abstractmethod
    def set_schedule(
        self,
        process_id: int,
        node_id: str,
        version: str,
        schedule_type: ScheduleType,
    ) -> Schedule:
        """
        设置 schedule 对象

        :param process_id: 进程 ID
        :type process_id: int
        :param node_id: 节点 ID
        :type node_id: str
        :param version: 执行版本
        :type version: str
        :param schedule_type: 调度类型
        :type schedule_type: ScheduleType
        :return: 调度对象实例
        :rtype: Schedule
        """

    @abstractmethod
    def get_schedule(self, schedule_id: str) -> Schedule:
        """
        获取 Schedule 对象

        :param schedule_id: 调度实例 ID
        :type schedule_id: str
        :return: Schedule 对象实例
        :rtype: Schedule
        """

    @abstractmethod
    def get_schedule_with_node_and_version(self, node_id: str, version: str) -> Schedule:
        """
        通过节点 ID 和执行版本来获取 Scheudle 对象

        :param node_id: 节点 ID
        :type node_id: str
        :param version: 执行版本
        :type version: str
        :return: Schedule 对象
        :rtype: Schedule
        """

    @abstractmethod
    def apply_schedule_lock(self, schedule_id: str) -> bool:
        """
        获取 Schedule 对象的调度锁，返回是否成功获取锁

        :param schedule_id: 调度实例 ID
        :type schedule_id: str
        :return: 是否成功获取锁
        :rtype: bool
        """

    @abstractmethod
    def release_schedule_lock(self, schedule_id: int):
        """
        释放指定 Schedule 的调度锁

        :param schedule_id: Schedule ID
        :type schedule_id: int
        """

    @abstractmethod
    def expire_schedule(self, schedule_id: int):
        """
        将某个 Schedule 对象标记为已过期

        :param schedule_id: 调度实例 ID
        :type schedule_id: int
        """

    @abstractmethod
    def finish_schedule(self, schedule_id: int):
        """
        将某个 Schedule 对象标记为已完成

        :param schedule_id: 调度实例 ID
        :type schedule_id: int
        """

    @abstractmethod
    def add_schedule_times(self, schedule_id: int):
        """
        将某个 Schedule 对象的调度次数 +1

        :param schedule_id: 调度实例 ID
        :type schedule_id: int
        """


class ContextMixin:
    """
    流程上下文相关接口
    """

    @abstractmethod
    def get_context_values(self, pipeline_id: str, keys: set) -> List[ContextValue]:
        """
        获取某个流程上下文中的 keys 所指定的键对应变量的值

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        :param keys: 变量键
        :type keys: set
        :return: 变量值信息
        :rtype: List[ContextValue]
        """

    @abstractmethod
    def get_context_key_references(self, pipeline_id: str, keys: set) -> set:
        """
        获取某个流程上下文中 keys 所指定的变量直接和间接引用的其他所有变量的键

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        :param keys: 变量 key 列表
        :type keys: set
        :return: keys 所指定的变量直接和简介引用的其他所有变量的键
        :rtype: set
        """

    @abstractmethod
    def upsert_plain_context_values(self, pipeline_id: str, update: Dict[str, ContextValue]):
        """
        更新或创建新的普通上下文数据

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        :param update: 更新数据
        :type update: Dict[str, ContextValue]
        """

    def get_context(self, pipeline_id: str) -> List[ContextValue]:
        """
        获取某个流程的所有上下文数据

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        :return: [description]
        :rtype: List[ContextValue]
        """

    def get_context_outputs(self, pipeline_id: str) -> Set[str]:
        """
        获取流程上下文需要输出的数据

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        :return: 输出数据 key
        :rtype: Set[str]
        """


class DataMixin:
    """
    节点数据，执行数据，回调数据相关接口
    """

    @abstractmethod
    def get_data(self, node_id: str) -> Data:
        """
        获取某个节点的数据对象

        :param node_id: 节点 ID
        :type node_id: str
        :return: 数据对象实例
        :rtype: Data
        """

    @abstractmethod
    def get_data_inputs(self, node_id: str) -> Dict[str, DataInput]:
        """
        获取某个节点的输入数据

        :param node_id: 节点 ID
        :type node_id: str
        :return: 输入数据字典
        :rtype: dict
        """

    @abstractmethod
    def get_data_outputs(self, node_id: str) -> dict:
        """
        获取某个节点的输出数据

        :param node_id: 节点 ID
        :type node_id: str
        :return: 输入数据字典
        :rtype: dict
        """

    @abstractmethod
    def set_data_inputs(self, node_id: str, data: Dict[str, DataInput]):
        """
        将节点数据对象的 inputs 设置为 data

        : param node_id: 节点 ID
        : type node_id: str
        : param data: 目标数据
        : type data: dict
        """

    # execution data relate
    @abstractmethod
    def get_execution_data(self, node_id: str) -> ExecutionData:
        """
        获取某个节点的执行数据

        : param node_id: 节点 ID
        : type node_id: str
        : return: 执行数据实例
        : rtype: ExecutionData
        """

    @abstractmethod
    def get_execution_data_inputs(self, node_id: str) -> dict:
        """
        获取某个节点的执行数据输入

        :param node_id: 节点 ID
        :type node_id: str
        :return: 执行数据输入
        :rtype: dict
        """

    @abstractmethod
    def get_execution_data_outputs(self, node_id: str) -> dict:
        """
        获取某个节点的执行数据输出

        :param node_id: 节点 ID
        :type node_id: str
        :return: 执行数据输出
        :rtype: dict
        """

    @abstractmethod
    def set_execution_data(self, node_id: str, data: ExecutionData):
        """
        设置某个节点的执行数据

        :param node_id: 节点 ID
        :type node_id: str
        :param data: 执行数据实例
        :type data: ExecutionData
        """

    @abstractmethod
    def set_execution_data_inputs(self, node_id: str, inputs: dict):
        """
        设置某个节点的执行数据输入

        :param node_id: 节点 ID
        :type node_id: str
        :param outputs: 输出数据
        :type outputs: dict
        """

    @abstractmethod
    def set_execution_data_outputs(self, node_id: str, outputs: dict):
        """
        设置某个节点的执行数据输出

        :param node_id: 节点 ID
        :type node_id: str
        :param outputs: 输出数据
        :type outputs: dict
        """

    # callback data relate
    @abstractmethod
    def set_callback_data(self, node_id: str, version: str, data: dict) -> int:
        """
        设置某个节点执行数据的回调数据

        :param node_id: 节点 ID
        :type node_id: str
        :param version: 节点执行版本
        :type version: str
        :param data: 回调数据
        :type data: dict
        :return: 回调数据 ID
        :rtype: int
        """

    @abstractmethod
    def get_callback_data(self, data_id: int) -> CallbackData:
        """
        获取回调数据

        :param data_id: Data ID
        :type data_id: int
        :return: 回调数据实例
        :rtype: CallbackData
        """


class ExecutionHistoryMixin:
    """
    执行历史相关接口
    """

    @abstractmethod
    def add_history(
        self,
        node_id: str,
        started_time: datetime,
        archived_time: datetime,
        loop: int,
        skip: bool,
        retry: int,
        version: str,
        inputs: dict,
        outputs: dict,
    ) -> int:
        """
        为某个节点记录一次执行历史

        : param node_id: 节点 ID
        : type node_id: str
        : param started_time: 开始时间
        : type started_time: datetime
        : param archived_time: 归档时间
        : type archived_time: datetime
        : param loop: 重入计数
        : type loop: int
        : param skip: 是否跳过
        : type skip: bool
        : param retry: 重试次数
        : type retry: int
        : param version: 节点执行版本号
        : type version: str
        : param inputs: 输入数据
        : type inputs: dict
        : param outputs: 输出数据
        : type outputs: dict
        """

    @abstractmethod
    def get_histories(self, node_id: str, loop: int = -1) -> List[ExecutionHistory]:
        """
        返回某个节点的历史记录

        :param node_id: 节点 ID
        :type node_id: str
        :param loop: 重入次数, -1 表示不过滤重入次数
        :type loop: int, optional
        :return: 历史记录列表
        :rtype: List[History]
        """

    @abstractmethod
    def get_short_histories(self, node_id: str, loop: int = -1) -> List[ExecutionShortHistory]:
        """
        返回某个节点的简要历史记录

        :param node_id: 节点 ID
        :type node_id: str
        :param loop: 重入次数, -1 表示不过滤重入次数
        :type loop: int, optional
        :return: 历史记录列表
        :rtype: List[ExecutionShortHistory]
        """


class EngineRuntimeInterface(
    PluginManagerMixin,
    EngineAPIHooksMixin,
    TaskMixin,
    ProcessMixin,
    StateMixin,
    NodeMixin,
    ScheduleMixin,
    ContextMixin,
    DataMixin,
    ExecutionHistoryMixin,
    metaclass=ABCMeta,
):
    @abstractmethod
    def prepare_run_pipeline(
        self, pipeline: dict, root_pipeline_data: dict, root_pipeline_context: dict, subprocess_context: dict, **options
    ) -> int:
        """
        进行 pipeline 执行前的准备工作，并返回 进程 ID，该函数执行完成后即代表
        pipeline 是随时可以通过 execute(process_id, start_event_id) 启动执行的
        一般来说，应该完成以下工作:
        - 准备好进程模型
        - 准备好流程中每个节点的信息
        - 准备好流程中每个节点数据对象的信息

        :param pipeline: pipeline 描述对象
        :type pipeline: dict
        :param root_pipeline_data 根流程数据
        :type root_pipeline_data: dict
        :param root_pipeline_context 根流程上下文
        :type root_pipeline_context: dict
        :param subprocess_context 子流程预置流程上下文
        :type subprocess_context: dict
        :return: 进程 ID
        :rtype: str
        """

    @abstractmethod
    def node_rerun_limit(self, root_pipeline_id: str, node_id: str) -> int:
        """
        返回节点最大重入次数

        :param root_pipeline_id: 根流程 ID
        :type root_pipeline_id: str
        :param node_id: 节点 ID
        :type node_id: str
        :return: 节点最大重入次数
        :rtype: int
        """
