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

from copy import deepcopy

from bamboo_engine.exceptions import ValueError


def format_to_list(notype):
    """
    format a data to list
    :return:
    """
    if isinstance(notype, list):
        return notype
    if not notype:
        return []
    return [notype]


def format_node_io_to_list(node, i=True, o=True):
    if i:
        node["incoming"] = format_to_list(node["incoming"])

    if o:
        node["outgoing"] = format_to_list(node["outgoing"])


def format_pipeline_tree_io_to_list(pipeline_tree):
    """
    :summary: format incoming and outgoing to list
    :param pipeline_tree:
    :return:
    """
    for act in list(pipeline_tree["activities"].values()):
        format_node_io_to_list(act, o=False)

    for gateway in list(pipeline_tree["gateways"].values()):
        format_node_io_to_list(gateway, o=False)

    format_node_io_to_list(pipeline_tree["end_event"], o=False)


def get_node_for_sequence(sid, tree, node_type):
    target_id = tree["flows"][sid][node_type]

    if target_id in tree["activities"]:
        return tree["activities"][target_id]
    elif target_id in tree["gateways"]:
        return tree["gateways"][target_id]
    elif target_id == tree["end_event"]["id"]:
        return tree["end_event"]
    elif target_id == tree["start_event"]["id"]:
        return tree["start_event"]

    raise ValueError("node(%s) not in data" % target_id)


def get_nodes_dict(data):
    """
    get all FlowNodes of a pipeline
    """
    data = deepcopy(data)
    start = data["start_event"]["id"]
    end = data["end_event"]["id"]

    nodes = {start: data["start_event"], end: data["end_event"]}

    nodes.update(data["activities"])
    nodes.update(data["gateways"])

    for node in list(nodes.values()):
        # format to list
        node["incoming"] = format_to_list(node["incoming"])
        node["outgoing"] = format_to_list(node["outgoing"])

        node["source"] = [data["flows"][incoming]["source"] for incoming in node["incoming"]]
        node["target"] = [data["flows"][outgoing]["target"] for outgoing in node["outgoing"]]

    return nodes
