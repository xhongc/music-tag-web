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

import copy
import queue

from pipeline.builder.flow.data import Data, Params
from pipeline.builder.flow.event import ExecutableEndEvent
from pipeline.core.constants import PE
from pipeline.parser.utils import replace_all_id
from pipeline.utils.uniqid import uniqid

__all__ = ["build_tree"]

__skeleton = {
    PE.id: None,
    PE.start_event: None,
    PE.end_event: None,
    PE.activities: {},
    PE.gateways: {},
    PE.flows: {},
    PE.data: {PE.inputs: {}, PE.outputs: {}},
}

__node_type = {
    PE.ServiceActivity: PE.activities,
    PE.SubProcess: PE.activities,
    PE.EmptyEndEvent: PE.end_event,
    PE.EmptyStartEvent: PE.start_event,
    PE.ParallelGateway: PE.gateways,
    PE.ConditionalParallelGateway: PE.gateways,
    PE.ExclusiveGateway: PE.gateways,
    PE.ConvergeGateway: PE.gateways,
}

__start_elem = {PE.EmptyStartEvent}

__end_elem = {PE.EmptyEndEvent}

__multiple_incoming_type = {
    PE.ServiceActivity,
    PE.ConvergeGateway,
    PE.EmptyEndEvent,
    PE.ParallelGateway,
    PE.ConditionalParallelGateway,
    PE.ExclusiveGateway,
    PE.SubProcess,
}

__incoming = "__incoming"


def build_tree(start_elem, id=None, data=None, replace_id=False):
    tree = copy.deepcopy(__skeleton)
    elem_queue = queue.Queue()
    processed_elem = set()

    tree[__incoming] = {}
    elem_queue.put(start_elem)

    while not elem_queue.empty():
        # get elem
        elem = elem_queue.get()

        # update node when we meet again
        if elem.id in processed_elem:
            __update(tree, elem)
            continue

        # add to queue
        for e in elem.outgoing:
            elem_queue.put(e)

        # mark as processed
        processed_elem.add(elem.id)

        # tree grow
        __grow(tree, elem)

    del tree[__incoming]
    tree[PE.id] = id or uniqid()
    user_data = data.to_dict() if isinstance(data, Data) else data
    tree[PE.data] = user_data or tree[PE.data]
    if replace_id:
        replace_all_id(tree)
    return tree


def __update(tree, elem):
    node_type = __node_type[elem.type()]
    node = tree[node_type] if node_type == PE.end_event else tree[node_type][elem.id]
    node[PE.incoming] = tree[__incoming][elem.id]


def __grow(tree, elem):
    if elem.type() in __start_elem:
        outgoing = uniqid()
        tree[PE.start_event] = {
            PE.incoming: "",
            PE.outgoing: outgoing,
            PE.type: elem.type(),
            PE.id: elem.id,
            PE.name: elem.name,
        }

        next_elem = elem.outgoing[0]
        __grow_flow(tree, outgoing, elem, next_elem)

    elif elem.type() in __end_elem or isinstance(elem, ExecutableEndEvent):
        tree[PE.end_event] = {
            PE.incoming: tree[__incoming][elem.id],
            PE.outgoing: "",
            PE.type: elem.type(),
            PE.id: elem.id,
            PE.name: elem.name,
        }

    elif elem.type() == PE.ServiceActivity:
        outgoing = uniqid()

        tree[PE.activities][elem.id] = {
            PE.incoming: tree[__incoming][elem.id],
            PE.outgoing: outgoing,
            PE.type: elem.type(),
            PE.id: elem.id,
            PE.name: elem.name,
            PE.error_ignorable: elem.error_ignorable,
            PE.timeout: elem.timeout,
            PE.skippable: elem.skippable,
            PE.retryable: elem.retryable,
            PE.component: elem.component_dict(),
            PE.optional: False,
            PE.failure_handler: elem.failure_handler,
        }

        next_elem = elem.outgoing[0]
        __grow_flow(tree, outgoing, elem, next_elem)

    elif elem.type() == PE.SubProcess:
        outgoing = uniqid()

        subprocess_param = elem.params.to_dict() if isinstance(elem.params, Params) else elem.params

        subprocess = {
            PE.id: elem.id,
            PE.incoming: tree[__incoming][elem.id],
            PE.name: elem.name,
            PE.outgoing: outgoing,
            PE.type: elem.type(),
            PE.params: subprocess_param,
        }

        if elem.template_id:
            subprocess[PE.template_id] = elem.template_id
        else:
            subprocess[PE.pipeline] = build_tree(
                start_elem=elem.start, id=elem.id, data=elem.data, replace_id=elem.replace_id
            )

        tree[PE.activities][elem.id] = subprocess

        next_elem = elem.outgoing[0]
        __grow_flow(tree, outgoing, elem, next_elem)

    elif elem.type() == PE.ParallelGateway:
        outgoing = [uniqid() for _ in range(len(elem.outgoing))]

        tree[PE.gateways][elem.id] = {
            PE.id: elem.id,
            PE.incoming: tree[__incoming][elem.id],
            PE.outgoing: outgoing,
            PE.type: elem.type(),
            PE.name: elem.name,
        }

        for i, next_elem in enumerate(elem.outgoing):
            __grow_flow(tree, outgoing[i], elem, next_elem)

    elif elem.type() in {PE.ExclusiveGateway, PE.ConditionalParallelGateway}:
        outgoing = [uniqid() for _ in range(len(elem.outgoing))]

        tree[PE.gateways][elem.id] = {
            PE.id: elem.id,
            PE.incoming: tree[__incoming][elem.id],
            PE.outgoing: outgoing,
            PE.type: elem.type(),
            PE.name: elem.name,
            PE.conditions: elem.link_conditions_with(outgoing),
        }

        for i, next_elem in enumerate(elem.outgoing):
            __grow_flow(tree, outgoing[i], elem, next_elem)

    elif elem.type() == PE.ConvergeGateway:
        outgoing = uniqid()

        tree[PE.gateways][elem.id] = {
            PE.id: elem.id,
            PE.incoming: tree[__incoming][elem.id],
            PE.outgoing: outgoing,
            PE.type: elem.type(),
            PE.name: elem.name,
        }

        next_elem = elem.outgoing[0]
        __grow_flow(tree, outgoing, elem, next_elem)

    else:
        raise Exception()


def __grow_flow(tree, outgoing, elem, next_element):
    tree[PE.flows][outgoing] = {PE.is_default: False, PE.source: elem.id, PE.target: next_element.id, PE.id: outgoing}
    if next_element.type() in __multiple_incoming_type:
        tree[__incoming].setdefault(next_element.id, []).append(outgoing)
    else:
        tree[__incoming][next_element.id] = outgoing
