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


# API 模块用于向外暴露接口，bamboo-engine 的使用者应该永远只用这个模块与 bamboo-engien 进行交互


import logging
import functools
import traceback
from typing import Optional, Any, List

from .utils.object import Representable
from .eri import EngineRuntimeInterface, ContextValue
from .engine import Engine
from .template import Template
from .context import Context
from .utils.constants import VAR_CONTEXT_MAPPING

logger = logging.getLogger("bamboo_engine")


class EngineAPIResult(Representable):
    """
    api 统一返回结果
    """

    def __init__(
        self,
        result: bool,
        message: str,
        exc: Optional[Exception] = None,
        data: Optional[Any] = None,
        exc_trace: Optional[str] = None,
    ):
        """
        :param result: 是否执行成功
        :type result: bool
        :param message: 附加消息，result 为 False 时关注
        :type message: str
        :param exc: 异常对象
        :type exc: Exception
        :param data: 数据
        :type data: Any
        """
        self.result = result
        self.message = message
        self.exc = exc
        self.data = data
        self.exc_trace = exc_trace


def _ensure_return_api_result(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            data = func(*args, **kwargs)
        except Exception as e:
            logger.exception("{} raise error.".format(func.__name__))
            trace = traceback.format_exc()
            return EngineAPIResult(result=False, message="fail", exc=e, data=None, exc_trace=trace)

        if isinstance(data, EngineAPIResult):
            return data
        return EngineAPIResult(result=True, message="success", exc=None, data=data, exc_trace=None)

    return wrapper


@_ensure_return_api_result
def run_pipeline(runtime: EngineRuntimeInterface, pipeline: dict, **options) -> EngineAPIResult:
    """
    执行 pipeline

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param pipeline: pipeline 描述对象
    :type pipeline: dict
    :return: 执行结果
    :rtype: EngineAPIResult
    """

    Engine(runtime).run_pipeline(pipeline, **options)


@_ensure_return_api_result
def pause_pipeline(runtime: EngineRuntimeInterface, pipeline_id: str) -> EngineAPIResult:
    """
    暂停 pipeline 的执行

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param pipeline_id: piipeline id
    :type pipeline_id: str
    :return: 执行结果
    :rtype: EngineAPIResult
    """

    Engine(runtime).pause_pipeline(pipeline_id)


@_ensure_return_api_result
def revoke_pipeline(runtime: EngineRuntimeInterface, pipeline_id: str) -> EngineAPIResult:
    """
    撤销 pipeline，使其无法继续执行

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param pipeline_id: pipeline id
    :type pipeline_id: str
    :return: 执行结果
    :rtype: EngineAPIResult
    """
    Engine(runtime).revoke_pipeline(pipeline_id)


@_ensure_return_api_result
def resume_pipeline(runtime: EngineRuntimeInterface, pipeline_id: str) -> EngineAPIResult:
    """
    继续被 pause_pipeline 接口暂停的 pipeline 的执行

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param pipeline_id: pipeline id
    :type pipeline_id: str
    :return: 执行结果
    :rtype: EngineAPIResult
    """
    Engine(runtime).resume_pipeline(pipeline_id)


@_ensure_return_api_result
def pause_node_appoint(runtime: EngineRuntimeInterface, node_id: str) -> EngineAPIResult:
    """
    预约暂停某个节点的执行

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param node_id: 节点 id
    :type node_id: str
    :return: 执行结果
    :rtype: EngineAPIResult
    """
    Engine(runtime).pause_node_appoint(node_id)


@_ensure_return_api_result
def resume_node_appoint(runtime: EngineRuntimeInterface, node_id: str) -> EngineAPIResult:
    """
    继续由于某个节点而暂停的 pipeline 的执行

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param node_id: 节点 id
    :type node_id: str
    :return: 执行结果
    :rtype: EngineAPIResult
    """
    Engine(runtime).resume_node_appoint(node_id)


@_ensure_return_api_result
def retry_node(runtime: EngineRuntimeInterface, node_id: str, data: Optional[dict] = None) -> EngineAPIResult:
    """
    重试某个执行失败的节点

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param node_id: 失败的节点 id
    :type node_id: str
    :param data: 重试时使用的节点执行输入
    :type data: dict
    :return: 执行结果
    :rtype: EngineAPIResult
    """
    Engine(runtime).retry_node(node_id, data)


@_ensure_return_api_result
def retry_subprocess(runtime: EngineRuntimeInterface, node_id: str) -> EngineAPIResult:
    """
    重试进入失败的子流程节点

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param node_id: 子流程节点 id
    :type node_id: str
    :return: [description]
    :rtype: EngineAPIResult
    """
    Engine(runtime).retry_subprocess(node_id)


@_ensure_return_api_result
def skip_node(runtime: EngineRuntimeInterface, node_id: str) -> EngineAPIResult:
    """
    跳过某个执行失败的节点（仅限 event，activity）

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param node_id: 失败的节点 id
    :type node_id: str
    :return: 执行结果
    :rtype: EngineAPIResult
    """
    Engine(runtime).skip_node(node_id)


@_ensure_return_api_result
def skip_exclusive_gateway(runtime: EngineRuntimeInterface, node_id: str, flow_id: str) -> EngineAPIResult:
    """
    跳过某个执行失败的分支网关

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param node_id: 失败的分支网关 id
    :type node_id: str
    :param flow_id: 需要往下执行的 flow id
    :type flow_id: str
    :return: 执行结果
    :rtype: EngineAPIResult
    """
    Engine(runtime).skip_exclusive_gateway(node_id, flow_id)


@_ensure_return_api_result
def skip_conditional_parallel_gateway(
    runtime: EngineRuntimeInterface,
    node_id: str,
    flow_ids: list,
    converge_gateway_id: str,
) -> EngineAPIResult:
    """
    跳过某个执行失败的条件并行网关

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param node_id: 失败的分支网关 id
    :type node_id: str
    :param flow_ids: 需要往下执行的 flow id 列表
    :type flow_ids: list
    :param converge_gateway_id: 目标汇聚网关 id
    :type converge_gateway_id: str
    :return: 执行结果
    :rtype: EngineAPIResult
    """
    Engine(runtime).skip_conditional_parallel_gateway(node_id, flow_ids, converge_gateway_id)


@_ensure_return_api_result
def forced_fail_activity(runtime: EngineRuntimeInterface, node_id: str, ex_data: str) -> EngineAPIResult:
    """
    强制失败某个 activity 节点

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param node_id: 节点 ID
    :type node_id: str
    :param message: 异常信息
    :type message: str
    :return: 执行结果
    :rtype: EngineAPIResult
    """
    Engine(runtime).forced_fail_activity(node_id, ex_data)


@_ensure_return_api_result
def callback(runtime: EngineRuntimeInterface, node_id: str, version: str, data: dict) -> EngineAPIResult:
    """
    回调某个节点

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param version: 节点执行版本
    :param version: str
    :param data: 节点 ID
    :type data: dict
    :return: 执行结果
    :rtype: EngineAPIResult
    """
    Engine(runtime).callback(node_id, version, data)


@_ensure_return_api_result
def get_pipeline_states(runtime: EngineRuntimeInterface, root_id: str, flat_children=True) -> EngineAPIResult:
    """
    返回某个任务的状态树

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param root_id: 根节点 ID
    :type root_id: str
    :param flat_children: 是否将所有子节点展开
    :type flat_children: bool
    :return: 执行结果
    :rtype: EngineAPIResult
    """
    states = runtime.get_state_by_root(root_id)
    if not states:
        return {}

    root_state = None
    children = {}
    for s in states:
        if s.node_id != root_id:
            children[s.node_id] = {
                "id": s.node_id,
                "state": s.name,
                "root_id:": s.root_id,
                "parent_id": s.parent_id,
                "version": s.version,
                "loop": s.loop,
                "retry": s.retry,
                "skip": s.skip,
                "error_ignorable": s.error_ignored,
                "error_ignored": s.error_ignored,
                "created_time": s.created_time,
                "started_time": s.started_time,
                "archived_time": s.archived_time,
                "children": {},
            }
        else:
            root_state = s

    if not flat_children:
        # set node children
        for node_id, state in children.items():
            if state["parent_id"] in children:
                children[state["parent_id"]]["children"][node_id] = state

        # pop sub child
        for node_id in list(children.keys()):
            if children[node_id]["parent_id"] != root_state.node_id:
                children.pop(node_id)

    state_tree = {}
    state_tree[root_state.node_id] = {
        "id": root_state.node_id,
        "state": root_state.name,
        "root_id:": root_state.root_id,
        "parent_id": root_state.root_id,
        "version": root_state.version,
        "loop": root_state.loop,
        "retry": root_state.retry,
        "skip": root_state.skip,
        "error_ignorable": s.error_ignored,
        "error_ignored": s.error_ignored,
        "created_time": root_state.created_time,
        "started_time": root_state.started_time,
        "archived_time": root_state.archived_time,
        "children": children,
    }
    return state_tree


@_ensure_return_api_result
def get_children_states(runtime: EngineRuntimeInterface, node_id: str) -> EngineAPIResult:
    """
    返回某个节点及其所有子节点的状态

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param node_id: 父流程 ID
    :type node_id: str
    :return: 执行结果
    :rtype: EngineAPIResult
    """
    parent_state = runtime.get_state_or_none(node_id)
    if not parent_state:
        return {}

    states = runtime.get_state_by_parent(node_id)
    children = {}
    for s in states:
        children[s.node_id] = {
            "id": s.node_id,
            "state": s.name,
            "root_id:": s.root_id,
            "parent_id": s.parent_id,
            "version": s.version,
            "loop": s.loop,
            "retry": s.retry,
            "skip": s.skip,
            "error_ignorable": s.error_ignored,
            "error_ignored": s.error_ignored,
            "created_time": s.created_time,
            "started_time": s.started_time,
            "archived_time": s.archived_time,
            "children": {},
        }

    state_tree = {}
    state_tree[parent_state.node_id] = {
        "id": parent_state.node_id,
        "state": parent_state.name,
        "root_id:": parent_state.root_id,
        "parent_id": parent_state.root_id,
        "version": parent_state.version,
        "loop": parent_state.loop,
        "retry": parent_state.retry,
        "skip": parent_state.skip,
        "error_ignorable": parent_state.error_ignored,
        "error_ignored": parent_state.error_ignored,
        "created_time": parent_state.created_time,
        "started_time": parent_state.started_time,
        "archived_time": parent_state.archived_time,
        "children": children,
    }
    return state_tree


@_ensure_return_api_result
def get_execution_data_inputs(runtime: EngineRuntimeInterface, node_id: str) -> EngineAPIResult:
    """
    获取某个节点执行数据的输入数据

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param node_id: 节点 ID
    :type node_id: str
    :return: 执行结果
    :rtype: EngineAPIResult
    """
    return runtime.get_execution_data_inputs(node_id)


@_ensure_return_api_result
def get_execution_data_outputs(runtime: EngineRuntimeInterface, node_id: str) -> EngineAPIResult:
    """
    获取某个节点的执行数据输出

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param node_id: 节点 ID
    :type node_id: str
    :return: 执行结果
    :rtype: EngineAPIResult
    """
    return runtime.get_execution_data_outputs(node_id)


@_ensure_return_api_result
def get_execution_data(runtime: EngineRuntimeInterface, node_id: str) -> EngineAPIResult:
    """
    获取某个节点的执行数据

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param node_id: 节点 ID
    :type node_id: str
    :return: 执行结果
    :rtype: EngineAPIResult
    """
    data = runtime.get_execution_data(node_id)
    return {"inputs": data.inputs, "outputs": data.outputs}


@_ensure_return_api_result
def get_data(runtime: EngineRuntimeInterface, node_id: str) -> EngineAPIResult:
    """
    获取某个节点的原始输入数据

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param node_id: 节点 ID
    :type node_id: str
    :return: 执行结果
    :rtype: EngineAPIResult
    """
    data = runtime.get_data(node_id)
    return {
        "inputs": {k: {"need_render": v.need_render, "value": v.value} for k, v in data.inputs.items()},
        "outputs": data.outputs,
    }


@_ensure_return_api_result
def get_node_histories(runtime: EngineRuntimeInterface, node_id: str, loop: int = -1) -> EngineAPIResult:
    """
    获取某个节点的历史记录概览

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param node_id: 节点 ID
    :type node_id: str
    :param loop: 重入次数, -1 表示不过滤重入次数
    :type loop: int, optional
    :return: 执行结果
    :rtype: EngineAPIResult
    """
    return [
        {
            "id": h.id,
            "node_id": h.node_id,
            "started_time": h.started_time,
            "archived_time": h.archived_time,
            "loop": h.loop,
            "skip": h.skip,
            "version": h.version,
            "inputs": h.inputs,
            "outputs": h.outputs,
        }
        for h in runtime.get_histories(node_id, loop)
    ]


@_ensure_return_api_result
def get_node_short_histories(runtime: EngineRuntimeInterface, node_id: str, loop: int = -1) -> EngineAPIResult:
    """
    获取某个节点的简要历史记录

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param node_id: 节点 ID
    :type node_id: str
    :param loop: 重入次数, -1 表示不过滤重入次数
    :type loop: int, optional
    :return: 执行结果
    :rtype: EngineAPIResult
    """
    return [
        {
            "id": h.id,
            "node_id": h.node_id,
            "started_time": h.started_time,
            "archived_time": h.archived_time,
            "loop": h.loop,
            "skip": h.skip,
            "version": h.version,
        }
        for h in runtime.get_short_histories(node_id, loop)
    ]


@_ensure_return_api_result
def get_pipeline_debug_info(runtime: EngineRuntimeInterface, pipeline_id: str):
    """
    获取某个流程的调试信息

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param pipeline_id: 流程 ID
    :type pipeline_id: str
    :return: 执行结果
    :rtype: EngineAPIResult
    """

    return {
        "contex_values": runtime.get_context(pipeline_id),
        "processes": runtime.get_process_info_with_root_pipeline(pipeline_id),
    }


@_ensure_return_api_result
def get_node_debug_info(runtime: EngineRuntimeInterface, node_id: str):
    """
    获取某个节点的调试信息

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param node_id: 节点 ID
    :type node_id: str
    :return: 执行结果
    :rtype: EngineAPIResult
    """

    data = None
    state = None
    err = []

    try:
        data = runtime.get_data(node_id)
    except Exception as e:
        err.append(str(e))

    try:
        state = runtime.get_state(node_id)
    except Exception as e:
        err.append(str(e))

    return {
        "node": runtime.get_node(node_id),
        "data": data,
        "state": state,
        "err": err,
    }


@_ensure_return_api_result
def preview_node_inputs(
    runtime: EngineRuntimeInterface,
    pipeline: dict,
    node_id: str,
    subprocess_stack: List[str] = [],
    root_pipeline_data: dict = {},
    parent_params: dict = {},
):
    """
    预览某个节点的输入结果

    :param pipeline: 预处理后的流程树数据
    :type  pipeline: dict
    :param node_id: 节点 ID
    :type node_id: str
    :param subprocess_stack: 子流程，需保证顺序
    :type subprocess_stack: List[str]
    :param root_pipeline_data: root流程数据
    :param parent_params: 父流程传入参数
    :return: 执行结果
    :rtype: EngineAPIResult
    """
    context_values = [
        ContextValue(key=key, type=VAR_CONTEXT_MAPPING[info["type"]], value=info["value"], code=info.get("custom_type"))
        for key, info in list(pipeline["data"].get("inputs", {}).items()) + list(parent_params.items())
    ]
    context = Context(runtime, context_values, root_pipeline_data)

    if subprocess_stack:
        subprocess = subprocess_stack[0]
        child_pipeline = pipeline["activities"][subprocess]["pipeline"]
        param_data = {key: info["value"] for key, info in pipeline["activities"][subprocess]["params"].items()}
        hydrated_context = context.hydrate(deformat=True)
        hydrated_param_data = Template(param_data).render(hydrated_context)
        formatted_param_data = {key: {"value": value, "type": "plain"} for key, value in hydrated_param_data.items()}
        return preview_node_inputs(
            runtime=runtime,
            pipeline=child_pipeline,
            node_id=node_id,
            subprocess_stack=subprocess_stack[1:],
            root_pipeline_data=root_pipeline_data,
            parent_params=formatted_param_data,
        )
    raw_inputs = pipeline["activities"][node_id]["component"]["inputs"]
    raw_inputs = {key: info["value"] for key, info in raw_inputs.items()}
    hydrated_context = context.hydrate(deformat=True)
    inputs = Template(raw_inputs).render(hydrated_context)
    return inputs
