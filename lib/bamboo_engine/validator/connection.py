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

from bamboo_engine.utils.graph import Graph
from bamboo_engine.exceptions import ConnectionValidateError

from .rules import NODE_RULES
from .utils import get_nodes_dict


def validate_graph_connection(data):
    """
    节点连接合法性校验
    """
    nodes = get_nodes_dict(data)

    result = {"result": True, "message": {}, "failed_nodes": []}

    for i in nodes:
        node_type = nodes[i]["type"]
        rule = NODE_RULES[node_type]
        message = ""
        for j in nodes[i]["target"]:
            if nodes[j]["type"] not in rule["allowed_out"]:
                message += "不能连接%s类型节点\n" % nodes[i]["type"]
            if rule["min_in"] > len(nodes[i]["source"]) or len(nodes[i]["source"]) > rule["max_in"]:
                message += "节点的入度最大为%s，最小为%s\n" % (rule["max_in"], rule["min_in"])
            if rule["min_out"] > len(nodes[i]["target"]) or len(nodes[i]["target"]) > rule["max_out"]:
                message += "节点的出度最大为%s，最小为%s\n" % (rule["max_out"], rule["min_out"])
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

    nodes = [data["start_event"]["id"], data["end_event"]["id"]]
    nodes += list(data["gateways"].keys()) + list(data["activities"].keys())
    flows = [[flow["source"], flow["target"]] for _, flow in list(data["flows"].items())]
    cycle = Graph(nodes, flows).get_cycle()
    if cycle:
        return {
            "result": False,
            "message": "pipeline graph has circle",
            "error_data": cycle,
        }
    return {"result": True, "data": []}
