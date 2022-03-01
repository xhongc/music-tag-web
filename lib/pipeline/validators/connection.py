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

from django.utils.translation import ugettext_lazy as _

from pipeline.exceptions import ConnectionValidateError
from pipeline.utils.graph import Graph
from pipeline.validators.rules import NODE_RULES
from pipeline.validators.utils import get_nodes_dict
from pipeline.core.constants import PE


def validate_graph_connection(data):
    """
    节点连接合法性校验
    """
    nodes = get_nodes_dict(data)

    result = {"result": True, "message": {}, "failed_nodes": []}

    for i in nodes:
        node_type = nodes[i][PE.type]
        rule = NODE_RULES[node_type]
        message = ""
        for j in nodes[i][PE.target]:
            if nodes[j][PE.type] not in rule["allowed_out"]:
                message += _("不能连接%s类型节点\n") % nodes[i][PE.type]
            if rule["min_in"] > len(nodes[i][PE.source]) or len(nodes[i][PE.source]) > rule["max_in"]:
                message += _("节点的入度最大为%s，最小为%s\n") % (rule["max_in"], rule["min_in"])
            if rule["min_out"] > len(nodes[i][PE.target]) or len(nodes[i][PE.target]) > rule["max_out"]:
                message += _("节点的出度最大为%s，最小为%s\n") % (rule["max_out"], rule["min_out"])
        if message:
            result["failed_nodes"].append(i)
            result["message"][i] = message

        if result["failed_nodes"]:
            raise ConnectionValidateError(failed_nodes=result["failed_nodes"], detail=result["message"])


def validate_graph_without_circle(data):
    """
    validate if a graph has not cycle

    return {
        "result": False,
        "message": "error message",
        "error_data": ["node1_id", "node2_id", "node1_id"]
    }
    """

    nodes = [data[PE.start_event][PE.id], data[PE.end_event][PE.id]]
    nodes += list(data[PE.gateways].keys()) + list(data[PE.activities].keys())
    flows = [[flow[PE.source], flow[PE.target]] for _, flow in list(data[PE.flows].items())]
    cycle = Graph(nodes, flows).get_cycle()
    if cycle:
        return {"result": False, "message": "pipeline graph has circle", "error_data": cycle}
    return {"result": True, "data": []}
