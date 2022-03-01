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

from bamboo_engine.utils.string import unique_id

from .flow.data import Data, Params
from .flow.event import ExecutableEndEvent


__all__ = ["build_tree"]

__skeleton = {
    "id": None,
    "start_event": None,
    "end_event": None,
    "activities": {},
    "gateways": {},
    "flows": {},
    "data": {"inputs": {}, "outputs": []},
}

__node_type = {
    "ServiceActivity": "activities",
    "SubProcess": "activities",
    "EmptyEndEvent": "end_event",
    "EmptyStartEvent": "start_event",
    "ParallelGateway": "gateways",
    "ConditionalParallelGateway": "gateways",
    "ExclusiveGateway": "gateways",
    "ConvergeGateway": "gateways",
}

__start_elem = {"EmptyStartEvent"}

__end_elem = {"EmptyEndEvent"}

__multiple_incoming_type = {
    "ServiceActivity",
    "ConvergeGateway",
    "EmptyEndEvent",
    "ParallelGateway",
    "ConditionalParallelGateway",
    "ExclusiveGateway",
    "SubProcess",
}

__incoming = "__incoming"


def build_tree(start_elem, id=None, data=None):
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
    tree["id"] = id or unique_id("p")
    user_data = data.to_dict() if isinstance(data, Data) else data
    tree["data"] = user_data or tree["data"]
    return tree


def __update(tree, elem):
    node_type = __node_type[elem.type()]
    node = tree[node_type] if node_type == "end_event" else tree[node_type][elem.id]
    node["incoming"] = tree[__incoming][elem.id]


def __grow(tree, elem):
    if elem.type() in __start_elem:
        outgoing = unique_id("f")
        tree["start_event"] = {
            "incoming": "",
            "outgoing": outgoing,
            "type": elem.type(),
            "id": elem.id,
            "name": elem.name,
        }

        next_elem = elem.outgoing[0]
        __grow_flow(tree, outgoing, elem, next_elem)

    elif elem.type() in __end_elem or isinstance(elem, ExecutableEndEvent):
        tree["end_event"] = {
            "incoming": tree[__incoming][elem.id],
            "outgoing": "",
            "type": elem.type(),
            "id": elem.id,
            "name": elem.name,
        }

    elif elem.type() == "ServiceActivity":
        outgoing = unique_id("f")

        tree["activities"][elem.id] = {
            "incoming": tree[__incoming][elem.id],
            "outgoing": outgoing,
            "type": elem.type(),
            "id": elem.id,
            "name": elem.name,
            "error_ignorable": elem.error_ignorable,
            "timeout": elem.timeout,
            "skippable": elem.skippable,
            "retryable": elem.retryable,
            "component": elem.component_dict(),
            "optional": False,
        }

        next_elem = elem.outgoing[0]
        __grow_flow(tree, outgoing, elem, next_elem)

    elif elem.type() == "SubProcess":
        outgoing = unique_id("f")

        subprocess_param = elem.params.to_dict() if isinstance(elem.params, Params) else elem.params

        subprocess = {
            "id": elem.id,
            "incoming": tree[__incoming][elem.id],
            "name": elem.name,
            "outgoing": outgoing,
            "type": elem.type(),
            "params": subprocess_param,
        }

        subprocess["pipeline"] = build_tree(start_elem=elem.start, id=elem.id, data=elem.data)

        tree["activities"][elem.id] = subprocess

        next_elem = elem.outgoing[0]
        __grow_flow(tree, outgoing, elem, next_elem)

    elif elem.type() == "ParallelGateway":
        outgoing = [unique_id("f") for _ in range(len(elem.outgoing))]

        tree["gateways"][elem.id] = {
            "id": elem.id,
            "incoming": tree[__incoming][elem.id],
            "outgoing": outgoing,
            "type": elem.type(),
            "name": elem.name,
        }

        for i, next_elem in enumerate(elem.outgoing):
            __grow_flow(tree, outgoing[i], elem, next_elem)

    elif elem.type() in {"ExclusiveGateway", "ConditionalParallelGateway"}:
        outgoing = [unique_id("f") for _ in range(len(elem.outgoing))]

        tree["gateways"][elem.id] = {
            "id": elem.id,
            "incoming": tree[__incoming][elem.id],
            "outgoing": outgoing,
            "type": elem.type(),
            "name": elem.name,
            "conditions": elem.link_conditions_with(outgoing),
        }

        for i, next_elem in enumerate(elem.outgoing):
            __grow_flow(tree, outgoing[i], elem, next_elem)

    elif elem.type() == "ConvergeGateway":
        outgoing = unique_id("f")

        tree["gateways"][elem.id] = {
            "id": elem.id,
            "incoming": tree[__incoming][elem.id],
            "outgoing": outgoing,
            "type": elem.type(),
            "name": elem.name,
        }

        next_elem = elem.outgoing[0]
        __grow_flow(tree, outgoing, elem, next_elem)

    else:
        raise Exception()


def __grow_flow(tree, outgoing, elem, next_element):
    tree["flows"][outgoing] = {
        "is_default": False,
        "source": elem.id,
        "target": next_element.id,
        "id": outgoing,
    }
    if next_element.type() in __multiple_incoming_type:
        tree[__incoming].setdefault(next_element.id, []).append(outgoing)
    else:
        tree[__incoming][next_element.id] = outgoing
