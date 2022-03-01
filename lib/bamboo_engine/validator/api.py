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

from bamboo_engine.eri import NodeType
from bamboo_engine import exceptions

from . import rules
from .connection import (
    validate_graph_connection,
    validate_graph_without_circle,
)
from .gateway import validate_gateways, validate_stream
from .utils import format_pipeline_tree_io_to_list


def validate_and_process_pipeline(pipeline: dict, cycle_tolerate=False):
    for subproc in [act for act in pipeline["activities"].values() if act["type"] == NodeType.SubProcess.value]:
        validate_and_process_pipeline(subproc["pipeline"], cycle_tolerate)

    format_pipeline_tree_io_to_list(pipeline)
    # 1. connection validation
    validate_graph_connection(pipeline)

    # do not tolerate circle in flow
    if not cycle_tolerate:
        no_cycle = validate_graph_without_circle(pipeline)
        if not no_cycle["result"]:
            raise exceptions.TreeInvalidException(no_cycle["message"])

    # 2. gateway validation
    validate_gateways(pipeline)

    # 3. stream validation
    validate_stream(pipeline)


def add_sink_type(node_type: str):
    rules.FLOW_NODES_WITHOUT_STARTEVENT.append(node_type)
    rules.NODE_RULES[node_type] = rules.SINK_RULE
