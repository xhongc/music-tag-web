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

import logging

from pipeline.utils.uniqid import node_uniqid, line_uniqid
from pipeline.core.constants import PE
from pipeline.exceptions import NodeNotExistException

logger = logging.getLogger("root")

BRANCH_SELECT_GATEWAYS = {PE.ExclusiveGateway, PE.ConditionalParallelGateway}


def recursive_replace_id(pipeline_data):
    pipeline_data[PE.id] = node_uniqid()
    replace_all_id(pipeline_data)
    activities = pipeline_data[PE.activities]
    for act_id, act in list(activities.items()):
        if act[PE.type] == PE.SubProcess:
            recursive_replace_id(act[PE.pipeline])
            act[PE.pipeline][PE.id] = act_id


def replace_all_id(pipeline_data):
    flows = pipeline_data[PE.flows]
    node_map = {}
    flow_map = {}

    # step.1 replace nodes id

    # replace events id
    start_event_id = node_uniqid()
    end_event_id = node_uniqid()
    node_map[pipeline_data[PE.start_event][PE.id]] = start_event_id
    node_map[pipeline_data[PE.end_event][PE.id]] = end_event_id

    start_event_id_maps = _replace_event_id(flows, pipeline_data[PE.start_event], start_event_id)
    end_event_id_maps = _replace_event_id(flows, pipeline_data[PE.end_event], end_event_id)

    # replace activities id
    activity_id_maps = {}
    activities = pipeline_data[PE.activities]
    keys = list(activities.keys())
    for old_id in keys:
        substituted_id = node_uniqid()
        node_map[old_id] = substituted_id
        _replace_activity_id(flows, activities, old_id, substituted_id)
        activity_id_maps[old_id] = substituted_id

    # replace gateways id
    gateway_id_maps = {}
    gateways = pipeline_data[PE.gateways]
    keys = list(gateways.keys())
    for old_id in keys:
        substituted_id = node_uniqid()
        node_map[old_id] = substituted_id
        _replace_gateway_id(flows, gateways, old_id, substituted_id)
        gateway_id_maps[old_id] = substituted_id

    # step.2 replace flows id
    flow_id_maps = {}
    keys = list(flows.keys())
    for old_id in keys:
        substituted_id = line_uniqid()
        flow_map[old_id] = substituted_id
        _replace_flow_id(flows, old_id, substituted_id, pipeline_data)
        flow_id_maps[old_id] = substituted_id

    # step.3 replace id in data
    _replace_id_in_data(pipeline_data, node_map)

    # step.4 try to replace front end data
    _replace_front_end_data_id(pipeline_data, node_map, flow_map)

    return {
        PE.start_event: start_event_id_maps,
        PE.end_event: end_event_id_maps,
        PE.activities: activity_id_maps,
        PE.gateways: gateway_id_maps,
        PE.flows: flow_id_maps,
        PE.subprocess_detail: {},
    }


def _replace_id_in_data(pipeline_data, node_map):
    for _, var_info in list(pipeline_data.get(PE.data, {}).get(PE.inputs, {}).items()):
        if PE.source_act in var_info:
            if isinstance(var_info[PE.source_act], str):
                var_info[PE.source_act] = node_map[var_info[PE.source_act]]
            else:
                for source_info in var_info[PE.source_act]:
                    source_info[PE.source_act] = node_map[var_info[PE.source_act]]


def _replace_front_end_data_id(pipeline_data, node_map, flow_map):
    if "line" in pipeline_data:
        for line in pipeline_data["line"]:
            line[PE.id] = flow_map[line[PE.id]]
            line[PE.source][PE.id] = node_map[line[PE.source][PE.id]]
            line[PE.target][PE.id] = node_map[line[PE.target][PE.id]]
    if "location" in pipeline_data:
        for location in pipeline_data["location"]:
            location[PE.id] = node_map[location[PE.id]]
    if "constants" in pipeline_data:
        for key, constant in list(pipeline_data[PE.constants].items()):
            source_info = constant.get("source_info", None)
            if source_info:
                replaced_constant = {}
                for source_step, source_keys in list(source_info.items()):
                    try:
                        replaced_constant[node_map[source_step]] = source_keys
                    except KeyError as e:
                        message = "replace pipeline template id error: %s" % e
                        logger.exception(message)
                        raise NodeNotExistException(message)
                    constant["source_info"] = replaced_constant


def _replace_flow_id(flows, flow_id, substituted_id, pipeline_data):
    flow = flows[flow_id]
    flow[PE.id] = substituted_id

    _replace_flow_in_node(flow[PE.source], pipeline_data, substituted_id, flow_id, PE.outgoing)
    _replace_flow_in_node(flow[PE.target], pipeline_data, substituted_id, flow_id, PE.incoming)

    flows.pop(flow_id)
    flows[substituted_id] = flow


def _replace_flow_in_node(node_id, pipeline_data, substituted_id, flow_id, field):
    if node_id in pipeline_data[PE.activities]:
        node = pipeline_data[PE.activities][node_id]
    elif node_id in pipeline_data[PE.gateways]:
        node = pipeline_data[PE.gateways][node_id]
        if node[PE.type] in BRANCH_SELECT_GATEWAYS and field == PE.outgoing:
            _replace_flow_in_exclusive_gateway_conditions(node, substituted_id, flow_id)
    elif node_id == pipeline_data[PE.start_event][PE.id]:
        node = pipeline_data[PE.start_event]
    elif node_id == pipeline_data[PE.end_event][PE.id]:
        node = pipeline_data[PE.end_event]
    sequence = node[field]
    if isinstance(sequence, list):
        i = sequence.index(flow_id)
        sequence.pop(i)
        sequence.insert(i, substituted_id)
    else:
        node[field] = substituted_id


def _replace_flow_in_exclusive_gateway_conditions(gateway, substituted_id, flow_id):
    conditions = gateway[PE.conditions]
    conditions[substituted_id] = conditions[flow_id]
    conditions.pop(flow_id)


def _replace_gateway_id(flows, gateways, gateway_id, substituted_id):
    try:
        gateway = gateways[gateway_id]
        gateway[PE.id] = substituted_id

        if gateway[PE.type] == PE.ConvergeGateway:
            flows[gateway[PE.outgoing]][PE.source] = substituted_id
            for flow_id in gateway[PE.incoming]:
                flows[flow_id][PE.target] = substituted_id
            # replace converge_gateway_id
            for g_id, gw in list(gateways.items()):
                if PE.converge_gateway_id in gw and gw[PE.converge_gateway_id] == gateway_id:
                    gw[PE.converge_gateway_id] = substituted_id
        else:
            incoming = gateway[PE.incoming]

            if isinstance(incoming, list):
                for flow_id in incoming:
                    flows[flow_id][PE.target] = substituted_id
            else:
                flows[gateway[PE.incoming]][PE.target] = substituted_id

            for flow_id in gateway[PE.outgoing]:
                flows[flow_id][PE.source] = substituted_id

        gateways.pop(gateway_id)
        gateways[substituted_id] = gateway
    except KeyError as e:
        message = "replace gateway id error: %s" % e
        logger.exception(message)
        raise NodeNotExistException(message)


def _replace_activity_id(flows, activities, act_id, substituted_id):
    try:
        activity = activities[act_id]
        activity[PE.id] = substituted_id

        incoming = activity[PE.incoming]

        if isinstance(incoming, list):
            for s in incoming:
                flows[s][PE.target] = substituted_id
        else:
            flows[activity[PE.incoming]][PE.target] = substituted_id

        flows[activity[PE.outgoing]][PE.source] = substituted_id

        activities.pop(act_id)
        activities[substituted_id] = activity
    except KeyError as e:
        message = "replace activity id error: %s" % e
        logger.exception(message)
        raise NodeNotExistException(message)


def _replace_event_id(flows, event, substituted_id):
    replace_maps = {}
    try:
        replace_maps[event[PE.id]] = substituted_id
        event[PE.id] = substituted_id
        if event[PE.incoming]:
            if isinstance(event[PE.incoming], list):
                for incoming in event[PE.incoming]:
                    flows[incoming][PE.target] = substituted_id
            else:
                flows[event[PE.incoming]][PE.target] = substituted_id
        else:
            flows[event[PE.outgoing]][PE.source] = substituted_id
    except KeyError as e:
        message = "replace event id error: %s" % e
        logger.exception(message)
        raise NodeNotExistException(message)

    return replace_maps
