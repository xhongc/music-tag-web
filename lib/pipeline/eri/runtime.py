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
from typing import Optional, List

from django.conf import settings
from django.db import transaction

from kombu import Exchange, Queue, Connection

from bamboo_engine import states
from bamboo_engine.template import Template
from bamboo_engine.eri import interfaces
from bamboo_engine.eri import EngineRuntimeInterface, NodeType, ContextValueType

from pipeline.eri import codec
from pipeline.eri.imp.plugin_manager import PipelinePluginManagerMixin
from pipeline.eri.imp.hooks import HooksMixin
from pipeline.eri.imp.process import ProcessMixin
from pipeline.eri.imp.node import NodeMixin
from pipeline.eri.imp.state import StateMixin
from pipeline.eri.imp.schedule import ScheduleMixin
from pipeline.eri.imp.data import DataMixin
from pipeline.eri.imp.context import ContextMixin
from pipeline.eri.imp.execution_history import ExecutionHistoryMixin
from pipeline.eri.imp.task import TaskMixin
from pipeline.eri.celery.queues import QueueResolver

from pipeline.eri.models import Node, Data, ContextValue, Process, ContextOutputs, LogEntry, ExecutionHistory, State


class BambooDjangoRuntime(
    TaskMixin,
    ExecutionHistoryMixin,
    ContextMixin,
    DataMixin,
    ScheduleMixin,
    StateMixin,
    NodeMixin,
    ProcessMixin,
    PipelinePluginManagerMixin,
    HooksMixin,
    EngineRuntimeInterface,
):
    CONTEXT_VALUE_TYPE_MAP = {
        "plain": ContextValueType.PLAIN.value,
        "splice": ContextValueType.SPLICE.value,
        "lazy": ContextValueType.COMPUTE.value,
    }

    ERI_SUPPORT_VERSION = 5

    def __init__(self):
        try:
            eri_version = interfaces.version()
        except AttributeError:
            raise RuntimeError(
                "bamboo_engine eri do not support version fetch, please make sure bamboo_engine version >= 1.1.6"
            )

        major_version = int(eri_version.split(".")[0])
        if major_version > self.ERI_SUPPORT_VERSION:
            raise RuntimeError(
                "unsupported bamboo_engine eri version: %s, expect version: <= %s.x.x"
                % (eri_version, self.ERI_SUPPORT_VERSION)
            )

    def _data_inputs_assemble(self, pipeline_id: str, node_id: str, node_inputs: dict) -> (dict, List[ContextValue]):
        inputs = {}
        context_values = []
        for k, v in node_inputs.items():
            if v["type"] == "lazy":
                if k.startswith("${") and k.endswith("}"):
                    cv_key = "${%s_%s}" % (k[2:-1], node_id)
                else:
                    cv_key = "${%s_%s}" % (k, node_id)
                if len(cv_key) > 128:
                    raise ValueError("var key %s length exceeds 128" % cv_key)
                context_values.append(
                    ContextValue(
                        pipeline_id=pipeline_id,
                        key=cv_key,
                        type=ContextValueType.COMPUTE.value,
                        serializer=self.JSON_SERIALIZER,
                        value=json.dumps(v["value"]),
                        code=v.get("custom_type", ""),
                    )
                )
                inputs[k] = {"need_render": True, "value": cv_key}
            else:
                inputs[k] = {"need_render": v["type"] == "splice", "value": v["value"]}
            # inject need_render from node_inputs[item].need_render
            if not v.get("need_render", True):
                inputs[k]["need_render"] = False
        return inputs, context_values

    def _gen_executable_end_event_node(self, event: dict, pipeline: dict, root_id: str, parent_id: str) -> Node:
        return Node(
            node_id=event["id"],
            detail=json.dumps(
                {
                    "id": event["id"],
                    "type": NodeType.ExecutableEndEvent.value,
                    "targets": {},
                    "root_pipeline_id": root_id,
                    "parent_pipeline_id": parent_id,
                    "can_skip": False,
                    "can_retry": True,
                    "code": event["type"],
                }
            ),
        )

    def _gen_event_node(self, event: dict, pipeline: dict, root_id: str, parent_id: str) -> Node:
        return Node(
            node_id=event["id"],
            detail=json.dumps(
                {
                    "id": event["id"],
                    "type": event["type"],
                    "targets": {event["outgoing"]: pipeline["flows"][event["outgoing"]]["target"]}
                    if event["type"] == NodeType.EmptyStartEvent.value
                    else {},
                    "root_pipeline_id": root_id,
                    "parent_pipeline_id": parent_id,
                    "can_skip": event["type"] == NodeType.EmptyStartEvent.value,
                    "can_retry": True,
                }
            ),
        )

    def _gen_gateway_node(self, gateway: dict, pipeline: dict, root_id: str, parent_id: str) -> Node:
        if gateway["type"] != NodeType.ConvergeGateway.value:
            targets = {flow_id: pipeline["flows"][flow_id]["target"] for flow_id in gateway["outgoing"]}
        else:
            targets = {gateway["outgoing"]: pipeline["flows"][gateway["outgoing"]]["target"]}

        detail = {
            "id": gateway["id"],
            "type": gateway["type"],
            "targets": targets,
            "root_pipeline_id": root_id,
            "parent_pipeline_id": parent_id,
            "can_retry": True,
            "can_skip": False,
        }

        if gateway["type"] == NodeType.ExclusiveGateway.value:
            detail["can_skip"] = True
            detail["conditions"] = [
                {
                    "name": flow_id,
                    "evaluation": cond["evaluate"],
                    "target_id": pipeline["flows"][flow_id]["target"],
                    "flow_id": flow_id,
                }
                for flow_id, cond in gateway["conditions"].items()
            ]
        elif gateway["type"] == NodeType.ParallelGateway.value:
            detail["converge_gateway_id"] = gateway["converge_gateway_id"]

        elif gateway["type"] == NodeType.ConditionalParallelGateway.value:
            detail["conditions"] = [
                {
                    "name": flow_id,
                    "evaluation": cond["evaluate"],
                    "target_id": pipeline["flows"][flow_id]["target"],
                    "flow_id": flow_id,
                }
                for flow_id, cond in gateway["conditions"].items()
            ]
            detail["converge_gateway_id"] = gateway["converge_gateway_id"]
        elif gateway["type"] == NodeType.ConvergeGateway.value:
            pass
        else:
            raise ValueError("unsupport gateway type {}: {}".format(gateway["type"], gateway))

        return Node(node_id=gateway["id"], detail=json.dumps(detail))

    def _gen_activity_node(self, act: dict, pipeline: dict, root_id: str, parent_id: str) -> Node:
        return Node(
            node_id=act["id"],
            detail=json.dumps(
                {
                    "id": act["id"],
                    "type": NodeType.ServiceActivity.value,
                    "targets": {act["outgoing"]: pipeline["flows"][act["outgoing"]]["target"]},
                    "root_pipeline_id": root_id,
                    "parent_pipeline_id": parent_id,
                    "can_skip": act["skippable"],
                    "code": act["component"]["code"],
                    "version": act["component"].get("version", "legacy"),
                    "timeout": act.get("timeout"),
                    "error_ignorable": act["error_ignorable"],
                    "can_retry": act["retryable"],
                }
            ),
        )

    def _gen_subproc_node(self, subproc: dict, pipeline: dict, root_id: str, parent_id: str) -> Node:
        return Node(
            node_id=subproc["id"],
            detail=json.dumps(
                {
                    "id": subproc["id"],
                    "type": NodeType.SubProcess.value,
                    "targets": {subproc["outgoing"]: pipeline["flows"][subproc["outgoing"]]["target"]},
                    "root_pipeline_id": root_id,
                    "parent_pipeline_id": parent_id,
                    "can_skip": False,
                    "can_retry": True,
                    "start_event_id": subproc["pipeline"]["start_event"]["id"],
                }
            ),
        )

    def _prepare(
        self, pipeline: dict, root_id: str, subprocess_context: dict, parent_id: Optional[str] = None
    ) -> (List[Node], List[Data], List[ContextValue], List[ContextOutputs]):

        parent_id = parent_id or root_id

        nodes = []
        datas = []
        context_values = []
        context_outputs = []

        node_outputs = {}
        context_var_references = {}
        final_references = {}

        # collect all node outputs and initial reference
        for key, input_data in pipeline["data"]["inputs"].items():
            source_act = input_data.get("source_act")
            source_key = input_data.get("source_key")
            if not source_act:
                context_var_references[key] = Template(input_data["value"]).get_reference()
                final_references[key] = set()
                context_values.append(
                    ContextValue(
                        pipeline_id=pipeline["id"],
                        key=key,
                        type=self.CONTEXT_VALUE_TYPE_MAP[input_data["type"]],
                        serializer=self.JSON_SERIALIZER,
                        value=json.dumps(input_data["value"]),
                        code=input_data.get("custom_type", ""),
                    )
                )
            else:
                if isinstance(source_act, list):
                    for sa in source_act:
                        node_outputs.setdefault(sa["source_act"], {})[sa["source_key"]] = key
                else:
                    node_outputs.setdefault(source_act, {})[source_key] = key

        # pre_render_keys in start_event
        if "pre_render_keys" in pipeline["data"] and pipeline["data"]["pre_render_keys"]:
            datas.append(
                Data(
                    node_id=pipeline["start_event"]["id"],
                    inputs=codec.data_json_dumps(
                        {"pre_render_keys": {"need_render": False, "value": pipeline["data"]["pre_render_keys"]}}
                    ),
                    outputs={},
                )
            )

        # process activities
        for act in pipeline["activities"].values():
            if act["type"] == NodeType.ServiceActivity.value:
                # node
                nodes.append(self._gen_activity_node(act=act, pipeline=pipeline, root_id=root_id, parent_id=parent_id))
                # data
                data_inputs, compute_cvs = self._data_inputs_assemble(parent_id, act["id"], act["component"]["inputs"])
                datas.append(
                    Data(
                        node_id=act["id"],
                        inputs=codec.data_json_dumps(data_inputs),
                        outputs=json.dumps(node_outputs.get(act["id"], {})),
                    )
                )
                # compute context values
                for cv in compute_cvs:
                    context_values.append(cv)
                    final_references[cv.key] = set()
                    context_var_references[cv.key] = Template(cv.value).get_reference()

            elif act["type"] == NodeType.SubProcess.value:
                # node
                nodes.append(
                    self._gen_subproc_node(subproc=act, pipeline=pipeline, root_id=root_id, parent_id=parent_id)
                )
                # data
                data_inputs, compute_cvs = self._data_inputs_assemble(parent_id, act["id"], act["params"])
                datas.append(
                    Data(
                        node_id=act["id"],
                        inputs=codec.data_json_dumps(data_inputs),
                        outputs=json.dumps(node_outputs.get(act["id"], {})),
                    )
                )
                # compute context values
                for cv in compute_cvs:
                    context_values.append(cv)
                    final_references[cv.key] = set()
                    context_var_references[cv.key] = Template(cv.value).get_reference()

                # subprocess output
                context_outputs.append(
                    ContextOutputs(pipeline_id=act["id"], outputs=json.dumps(act["pipeline"]["data"]["outputs"]))
                )

                # subprocess preset context
                for key, value in subprocess_context.items():
                    serialized, serializer = self._serialize(value)
                    context_values.append(
                        ContextValue(
                            pipeline_id=act["id"],
                            key=key,
                            type=self.CONTEXT_VALUE_TYPE_MAP["plain"],
                            serializer=serializer,
                            value=serialized,
                            references="[]",
                        )
                    )

                sub_nodes, sub_datas, sub_ctx_values, sub_ctx_outputs = self._prepare(
                    pipeline=act["pipeline"],
                    root_id=root_id,
                    subprocess_context=subprocess_context,
                    parent_id=act["id"],
                )

                nodes.extend(sub_nodes)
                datas.extend(sub_datas)
                context_values.extend(sub_ctx_values)
                context_outputs.extend(sub_ctx_outputs)
            else:
                raise ValueError("unsupport act type {}: {}".format(act["type"], act["id"]))

        # process events
        nodes.append(
            self._gen_event_node(event=pipeline["start_event"], pipeline=pipeline, root_id=root_id, parent_id=parent_id)
        )
        if pipeline["end_event"]["type"] == NodeType.EmptyEndEvent.value:
            nodes.append(
                self._gen_event_node(
                    event=pipeline["end_event"], pipeline=pipeline, root_id=root_id, parent_id=parent_id
                )
            )
        else:
            nodes.append(
                self._gen_executable_end_event_node(
                    event=pipeline["end_event"], pipeline=pipeline, root_id=root_id, parent_id=parent_id
                )
            )

        # process gateways
        for gateway in pipeline["gateways"].values():
            nodes.append(
                self._gen_gateway_node(gateway=gateway, pipeline=pipeline, root_id=root_id, parent_id=parent_id)
            )

        # resolve final references (BFS)
        # convert a:b, b:c,d -> a:b,c,d b:c,d
        for key, references in context_var_references.items():
            queue = []
            queue.extend(references)

            while queue:
                r = queue.pop()

                # processed
                if r in final_references[key]:
                    continue

                final_references[key].add(r)
                if r in context_var_references:
                    queue.extend(context_var_references[r])

        for cv in context_values:
            if cv.pipeline_id != parent_id:
                continue
            fr = final_references.get(cv.key)
            cv.references = json.dumps(list(fr)) if fr else "[]"

        if parent_id == root_id:
            context_outputs.append(ContextOutputs(pipeline_id=root_id, outputs=json.dumps(pipeline["data"]["outputs"])))

        return nodes, datas, context_values, context_outputs

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

        queue = options.get("queue", "")
        priority = options.get("priority", 100)
        pipeline_id = pipeline["id"]

        nodes, datas, context_values, context_outputs = self._prepare(
            pipeline=pipeline, root_id=pipeline["id"], subprocess_context=subprocess_context
        )
        datas.append(
            Data(
                node_id=pipeline_id,
                inputs=codec.data_json_dumps(
                    {k: {"need_render": False, "value": v} for k, v in root_pipeline_data.items()}
                ),
                outputs="{}",
            )
        )
        for key, value in root_pipeline_context.items():
            serialized, serializer = self._serialize(value)
            context_values.append(
                ContextValue(
                    pipeline_id=pipeline_id,
                    key=key,
                    type=self.CONTEXT_VALUE_TYPE_MAP["plain"],
                    serializer=serializer,
                    value=serialized,
                    references="[]",
                )
            )
        batch_size = getattr(settings, "BAMBOO_DJANGO_ERI_PREPARE_BATCH_SIZE", 500)

        with transaction.atomic():
            pid = Process.objects.create(
                root_pipeline_id=pipeline_id,
                queue=queue,
                priority=priority,
                pipeline_stack='["{}"]'.format(pipeline_id),
            ).id
            self.set_state(
                node_id=pipeline_id,
                to_state=states.RUNNING,
                root_id=pipeline_id,
                parent_id="",
                set_started_time=True,
            )

            Node.objects.bulk_create(nodes, batch_size=batch_size)
            Data.objects.bulk_create(datas, batch_size=batch_size)
            ContextValue.objects.bulk_create(context_values, batch_size=batch_size)
            ContextOutputs.objects.bulk_create(context_outputs, batch_size=batch_size)

        return pid

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
        return int(getattr(settings, "BAMBOO_DJANGO_ERI_NODE_RERUN_LIMIT", 100))

    def add_queue(self, name: str, routing_key: Optional[str] = ""):
        """
        在 Broker 中新增用户自定义队列，注意配合 CELERY_CREATE_MISSING_QUEUES 选项使用

        :param name: 队列名
        :type name: str
        :param routing_key: routing key
        :type routing_key: str
        """
        queue_resolver = QueueResolver(name)

        exchange = Exchange("default", type="direct")
        with Connection(settings.BROKER_URL) as conn:
            with conn.channel() as channel:
                for queue_config in queue_resolver.routes_config().values():
                    queue = Queue(
                        queue_config["queue"], exchange, routing_key=queue_config["routing_key"], max_priority=255
                    )
                    queue.declare(channel=channel)

    def get_plain_log_for_node(self, node_id: str, history_id: int = -1, version: str = None) -> str:
        """
        读取某个节点某一次执行的日志

        :param node_id: 节点 ID
        :type node_id: str
        :param history_id: 执行历史 ID, -1 表示获取最新日志
        :type history_id: int, optional
        :param version: 节点执行版本，当该参数与执行历史 ID 同时存在时，以版本为准
        :return: 节点日志
        :rtype: str
        """
        if not version:
            if history_id != -1:
                qs = ExecutionHistory.objects.filter(id=history_id).only("version")
            else:
                qs = State.objects.filter(node_id=node_id).only("version")

            if not qs:
                return ""
            version = qs.first().version

        return "\n".join(
            [
                e.message
                for e in LogEntry.objects.order_by("id").filter(node_id=node_id, version=version).only("message")
            ]
        )
