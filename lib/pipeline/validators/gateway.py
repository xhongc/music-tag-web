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

import queue

from django.utils.translation import ugettext_lazy as _

from pipeline import exceptions
from pipeline.core.constants import PE
from pipeline.engine.utils import Stack
from pipeline.validators.utils import get_node_for_sequence, get_nodes_dict

STREAM = "stream"
P_STREAM = "p_stream"
P = "p"
MAIN_STREAM = "main"

PARALLEL_GATEWAYS = {PE.ParallelGateway, PE.ConditionalParallelGateway}


def not_in_parallel_gateway(gateway_stack, start_from=None):
    """
    check whether there is parallel gateway in stack from specific gateway
    :param gateway_stack:
    :param start_from:
    :return:
    """
    start = 0
    if start_from:
        id_stack = [g[PE.id] for g in gateway_stack]
        start = id_stack.index(start_from)

    for i in range(start, len(gateway_stack)):
        gateway = gateway_stack[i]
        if gateway[PE.type] in PARALLEL_GATEWAYS:
            return False
    return True


def matched_in_prev_blocks(gid, current_start, block_nodes):
    """
    check whether gateway with gid is matched in previous block
    :param gid:
    :param current_start:
    :param block_nodes:
    :return:
    """
    prev_nodes = set()
    for prev_start, nodes in list(block_nodes.items()):
        if prev_start == current_start:
            continue
        prev_nodes.update(nodes)

    return gid in prev_nodes


def match_converge(
    converges,
    gateways,
    cur_index,
    end_event_id,
    block_start,
    block_nodes,
    converged,
    dist_from_start,
    converge_in_len,
    stack=None,
):
    """
    find converge for parallel and exclusive in blocks, and check sanity of gateway
    :param converges:
    :param gateways:
    :param cur_index:
    :param end_event_id:
    :param block_start:
    :param block_nodes:
    :param converged:
    :param dist_from_start:
    :param stack:
    :param converge_in_len:
    :return:
    """

    if stack is None:
        stack = Stack()

    if cur_index not in gateways:
        return None, False

    # return if this node is already matched
    if gateways[cur_index]["match"]:
        return gateways[cur_index]["match"], gateways[cur_index]["share_converge"]

    current_gateway = gateways[cur_index]
    target = gateways[cur_index][PE.target]
    stack.push(gateways[cur_index])
    stack_id_set = {g[PE.id] for g in stack}

    # find closest converge recursively
    for i in range(len(target)):

        # do not process prev blocks nodes
        if matched_in_prev_blocks(target[i], block_start, block_nodes):
            target[i] = None
            continue

        block_nodes[block_start].add(target[i])

        # do not find self's converge node again
        while target[i] in gateways and target[i] != current_gateway[PE.id]:

            if target[i] in stack_id_set:
                # return to previous gateway

                if not_in_parallel_gateway(stack, start_from=target[i]):
                    # do not trace back
                    target[i] = None
                    break
                else:
                    raise exceptions.ConvergeMatchError(cur_index, _("并行网关中的分支网关必须将所有分支汇聚到一个汇聚网关"))

            converge_id, shared = match_converge(
                converges=converges,
                gateways=gateways,
                cur_index=target[i],
                end_event_id=end_event_id,
                block_start=block_start,
                block_nodes=block_nodes,
                stack=stack,
                converged=converged,
                dist_from_start=dist_from_start,
                converge_in_len=converge_in_len,
            )
            if converge_id:
                target[i] = converge_id

                if not shared:
                    # try to get next node fo converge which is not shared
                    target[i] = converges[converge_id][PE.target][0]

            else:
                # can't find corresponding converge gateway, which means this gateway will reach end event directly
                target[i] = end_event_id

        if target[i] in converges and dist_from_start[target[i]] < dist_from_start[cur_index]:
            # do not match previous converge
            target[i] = None

    stack.pop()

    is_exg = current_gateway[PE.type] == PE.ExclusiveGateway
    converge_id = None
    shared = False
    cur_to_converge = len(target)
    converge_end = False

    # gateway match validation
    for i in range(len(target)):

        # mark first converge
        if target[i] in converges and not converge_id:
            converge_id = target[i]

        # same converge node
        elif target[i] in converges and converge_id == target[i]:
            pass

        # exclusive gateway point to end
        elif is_exg and target[i] == end_event_id:
            if not_in_parallel_gateway(stack):
                converge_end = True
            else:
                raise exceptions.ConvergeMatchError(cur_index, _("并行网关中的分支网关必须将所有分支汇聚到一个汇聚网关"))

        # exclusive gateway point back to self
        elif is_exg and target[i] == current_gateway[PE.id]:
            # not converge behavior
            cur_to_converge -= 1
            pass

        # exclusive gateway converge at different converge gateway
        elif is_exg and target[i] in converges and converge_id != target[i]:
            raise exceptions.ConvergeMatchError(cur_index, _("分支网关的所有分支第一个遇到的汇聚网关必须是同一个"))

        # meet previous node
        elif is_exg and target[i] is None:
            # not converge behavior
            cur_to_converge -= 1
            pass

        # invalid cases
        else:
            raise exceptions.ConvergeMatchError(cur_index, _("非法网关，请检查其分支是否符合规则"))

    if is_exg:
        if converge_id in converges:
            # this converge is shared by multiple gateway
            # only compare to the number of positive incoming
            shared = converge_in_len[converge_id] > cur_to_converge or converge_id in converged
    else:
        # for parallel gateway

        converge_incoming = len(converges[converge_id][PE.incoming])
        gateway_outgoing = len(target)

        if converge_incoming > gateway_outgoing:
            for gateway_id in converged.get(converge_id, []):
                # find another parallel gateway
                if gateways[gateway_id][PE.type] in PARALLEL_GATEWAYS:
                    raise exceptions.ConvergeMatchError(converge_id, _("汇聚网关只能汇聚来自同一个并行网关的分支"))

            shared = True

        elif converge_incoming < gateway_outgoing:
            raise exceptions.ConvergeMatchError(converge_id, _("汇聚网关没有汇聚其对应的并行网关的所有分支"))

    current_gateway["match"] = converge_id
    current_gateway["share_converge"] = shared
    current_gateway["converge_end"] = converge_end

    converged.setdefault(converge_id, []).append(current_gateway[PE.id])
    block_nodes[block_start].add(current_gateway[PE.id])

    return converge_id, shared


def distance_from(origin, node, tree, marked, visited=None):
    """
    get max distance from origin to node
    :param origin:
    :param node:
    :param tree:
    :param marked:
    :param visited:
    :return:
    """
    if visited is None:
        visited = set()

    if node[PE.id] in marked:
        return marked[node[PE.id]]

    if node[PE.id] == origin[PE.id]:
        return 0

    if node[PE.id] in visited:
        # do not trace circle
        return None

    visited.add(node[PE.id])

    incoming_dist = []
    for incoming in node[PE.incoming]:
        prev_node = get_node_for_sequence(incoming, tree, PE.source)

        # get incoming node's distance recursively
        dist = distance_from(origin=origin, node=prev_node, tree=tree, marked=marked, visited=visited)

        # if this incoming do not trace back to current node
        if dist is not None:
            incoming_dist.append(dist + 1)

    if not incoming_dist:
        return None

    # get max distance
    res = max(incoming_dist)
    marked[node[PE.id]] = res
    return res


def validate_gateways(tree):
    """
    check sanity of gateways and find their converge gateway
    :param tree:
    :return:
    """
    converges = {}
    gateways = {}
    all = {}
    distances = {}
    converge_positive_in = {}
    process_order = []

    # data preparation
    for i, item in list(tree[PE.gateways].items()):
        node = {
            PE.incoming: item[PE.incoming] if isinstance(item[PE.incoming], list) else [item[PE.incoming]],
            PE.outgoing: item[PE.outgoing] if isinstance(item[PE.outgoing], list) else [item[PE.outgoing]],
            PE.type: item[PE.type],
            PE.target: [],
            PE.source: [],
            PE.id: item[PE.id],
            "match": None,
        }

        # find all first reach nodes(ConvergeGateway, ExclusiveGateway, ParallelGateway, EndEvent)
        # which is not ServiceActivity for each gateway
        for index in node[PE.outgoing]:
            index = tree[PE.flows][index][PE.target]
            while index in tree[PE.activities]:
                index = tree[PE.flows][tree[PE.activities][index][PE.outgoing]][PE.target]

            # append this node's id to current gateway's target list
            node[PE.target].append(index)

        # get current node's distance from start event
        if not distance_from(node=node, origin=tree[PE.start_event], tree=tree, marked=distances):
            raise exceptions.ConvergeMatchError(node[PE.id], _("无法获取该网关距离开始节点的距离"))

        if item[PE.type] == PE.ConvergeGateway:
            converges[i] = node
        else:
            process_order.append(i)
            gateways[i] = node

        all[i] = node

    # calculate positive incoming number for converge
    for nid, node in list(all.items()):
        for t in node[PE.target]:
            if t in converges and distances[t] > distances[nid]:
                converge_positive_in[t] = converge_positive_in.setdefault(t, 0) + 1

    process_order.sort(key=lambda gid: distances[gid])
    end_event_id = tree[PE.end_event][PE.id]
    converged = {}
    block_nodes = {}
    visited = set()

    # process in distance order
    for gw in process_order:
        if gw in visited or "match" in gw:
            continue
        visited.add(gw)

        block_nodes[gw] = set()

        match_converge(
            converges=converges,
            gateways=gateways,
            cur_index=gw,
            end_event_id=end_event_id,
            converged=converged,
            block_start=gw,
            block_nodes=block_nodes,
            dist_from_start=distances,
            converge_in_len=converge_positive_in,
        )

    # set converge gateway
    for i in gateways:
        if gateways[i]["match"]:
            tree[PE.gateways][i][PE.converge_gateway_id] = gateways[i]["match"]

    return converged


def blend(source, target, custom_stream=None):
    """
    blend source and target streams
    :param source:
    :param target:
    :param custom_stream:
    :return:
    """

    if custom_stream:
        # use custom stream instead of source's stream
        if isinstance(custom_stream, set):
            for stream in custom_stream:
                target[STREAM].add(stream)
        else:
            target[STREAM].add(custom_stream)

        return

    if len(source[STREAM]) == 0:
        raise exceptions.InvalidOperationException("stream validation error, node(%s) stream is empty" % source[PE.id])

    # blend
    for s in source[STREAM]:
        target[STREAM].add(s)


def streams_for_parallel(p):
    streams = set()
    for i, target_id in enumerate(p[PE.target]):
        streams.add("{}_{}".format(p[PE.id], i))

    return streams


def flowing(where, to, parallel_converges):
    """
    mark target's stream from target
    :param where:
    :param to:
    :param parallel_converges:
    :return:
    """
    is_parallel = where[PE.type] in PARALLEL_GATEWAYS

    stream = None
    if is_parallel:
        # add parallel's stream to its converge
        parallel_converge = to[where[PE.converge_gateway_id]]
        blend(source=where, target=parallel_converge, custom_stream=stream)

        if len(parallel_converge[STREAM]) > 1:
            raise exceptions.StreamValidateError(node_id=parallel_converge)

    # flow to target
    for i, target_id in enumerate(where[PE.target]):
        target = to[target_id]
        fake = False

        # generate different stream
        if is_parallel:
            stream = "{}_{}".format(where[PE.id], i)

        if target_id in parallel_converges:

            is_valid_branch = where[STREAM].issubset(parallel_converges[target_id][P_STREAM])
            is_direct_connect = where.get(PE.converge_gateway_id) == target_id

            if is_valid_branch or is_direct_connect:
                # do not flow when branch of parallel converge to its converge gateway
                fake = True

        if not fake:
            blend(source=where, target=target, custom_stream=stream)

        # sanity check
        if len(target[STREAM]) != 1:
            raise exceptions.StreamValidateError(node_id=target_id)


def validate_stream(tree):
    """
    validate flow stream
    :param tree: pipeline tree
    :return:
    """
    # data preparation
    start_event_id = tree[PE.start_event][PE.id]
    end_event_id = tree[PE.end_event][PE.id]
    nodes = get_nodes_dict(tree)
    nodes[start_event_id][STREAM] = {MAIN_STREAM}
    nodes[end_event_id][STREAM] = {MAIN_STREAM}
    parallel_converges = {}
    visited = set({})

    for nid, node in list(nodes.items()):
        node.setdefault(STREAM, set())

        # set allow streams for parallel's converge
        if node[PE.type] in PARALLEL_GATEWAYS:
            parallel_converges[node[PE.converge_gateway_id]] = {P_STREAM: streams_for_parallel(node), P: nid}

    # build stream from start
    node_queue = queue.Queue()
    node_queue.put(nodes[start_event_id])
    while not node_queue.empty():

        # get node
        node = node_queue.get()

        if node[PE.id] in visited:
            # flow again to validate stream, but do not add target to queue
            flowing(where=node, to=nodes, parallel_converges=parallel_converges)
            continue

        # add to queue
        for target_id in node[PE.target]:
            node_queue.put(nodes[target_id])

        # mark as visited
        visited.add(node[PE.id])

        # flow
        flowing(where=node, to=nodes, parallel_converges=parallel_converges)

    # data clean
    for nid, n in list(nodes.items()):
        if len(n[STREAM]) != 1:
            raise exceptions.StreamValidateError(node_id=nid)

        # replace set to str
        n[STREAM] = n[STREAM].pop()

    # isolate node check
    for __, node in list(nodes.items()):
        if not node[STREAM]:
            raise exceptions.IsolateNodeError()

    return nodes
