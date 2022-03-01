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

from bamboo_engine import metrics
from bamboo_engine.eri import (
    Node,
    NodeType,
    ServiceActivity,
    SubProcess,
    ExclusiveGateway,
    ParallelGateway,
    ConditionalParallelGateway,
    ConvergeGateway,
    EmptyStartEvent,
    EmptyEndEvent,
    ExecutableEndEvent,
    Condition,
)

from pipeline.eri.models import Node as DBNode


class NodeMixin:
    def _get_node(self, node: DBNode):
        node_detail = json.loads(node.detail)
        node_type = node_detail["type"]
        targets = node_detail["targets"]
        common_args = dict(
            id=node.node_id,
            target_flows=list(targets.keys()),
            target_nodes=list(targets.values()),
            targets=node_detail["targets"],
            root_pipeline_id=node_detail["root_pipeline_id"],
            parent_pipeline_id=node_detail["parent_pipeline_id"],
            can_skip=node_detail["can_skip"],
            can_retry=node_detail["can_retry"],
        )

        if node_type == NodeType.ServiceActivity.value:
            return ServiceActivity(
                type=NodeType.ServiceActivity,
                code=node_detail["code"],
                version=node_detail["version"],
                timeout=node_detail["timeout"],
                error_ignorable=node_detail["error_ignorable"],
                **common_args
            )

        elif node_type == NodeType.SubProcess.value:
            return SubProcess(type=NodeType.SubProcess, start_event_id=node_detail["start_event_id"], **common_args)

        elif node_type == NodeType.ExclusiveGateway.value:
            return ExclusiveGateway(
                type=NodeType.ExclusiveGateway,
                conditions=[Condition(**c) for c in node_detail["conditions"]],
                **common_args
            )

        elif node_type == NodeType.ParallelGateway.value:
            return ParallelGateway(
                type=NodeType.ParallelGateway, converge_gateway_id=node_detail["converge_gateway_id"], **common_args
            )

        elif node_type == NodeType.ConditionalParallelGateway.value:
            return ConditionalParallelGateway(
                type=NodeType.ConditionalParallelGateway,
                converge_gateway_id=node_detail["converge_gateway_id"],
                conditions=[Condition(**c) for c in node_detail["conditions"]],
                **common_args
            )

        elif node_type == NodeType.ConvergeGateway.value:
            return ConvergeGateway(type=NodeType.ConvergeGateway, **common_args)

        elif node_type == NodeType.EmptyStartEvent.value:
            return EmptyStartEvent(type=NodeType.EmptyStartEvent, **common_args)

        elif node_type == NodeType.EmptyEndEvent.value:
            return EmptyEndEvent(type=NodeType.EmptyEndEvent, **common_args)

        elif node_type == NodeType.ExecutableEndEvent.value:
            return ExecutableEndEvent(type=NodeType.ExecutableEndEvent, code=node_detail["code"], **common_args)

        else:
            raise ValueError("unknown node type: {}".format(node_type))

    @metrics.setup_histogram(metrics.ENGINE_RUNTIME_NODE_READ_TIME)
    def get_node(self, node_id: str) -> Node:
        """
        获取某个节点的详细信息

        :param node_id: 节点 ID
        :type node_id: str
        :return: Node 实例
        :rtype: Node
        """
        node = DBNode.objects.get(node_id=node_id)
        return self._get_node(node)
