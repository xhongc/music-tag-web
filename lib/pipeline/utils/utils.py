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

ITERATED = 1
NEW = 0
ITERATING = -1


def has_circle(graph):
    # init marks
    marks = {}
    for node in graph:
        # marks as not iterated
        marks[node] = NEW

    # dfs every node
    for cur_node in graph:
        trace = [cur_node]
        for node in graph[cur_node]:
            if marks[node] == ITERATED:
                continue
            trace.append(node)
            # return immediately when circle be detected
            if _has_circle(graph, node, marks, trace):
                return True, trace
            trace.pop()
        # mark as iterated
        marks[cur_node] = ITERATED

    return False, []


def _has_circle(graph, cur_node, marks, trace):
    # detect circle when iterate to a node which been marked as -1
    if marks[cur_node] == ITERATING:
        return True
    # mark as iterating
    marks[cur_node] = ITERATING
    # dfs
    for node in graph[cur_node]:
        # return immediately when circle be detected
        trace.append(node)
        if _has_circle(graph, node, marks, trace):
            return True
        trace.pop()
    # mark as iterated
    marks[cur_node] = ITERATED

    return False


def convert_bytes_to_str(obj):

    converted = set()

    def _convert(obj, converted):
        if isinstance(obj, dict):
            new_dict = obj.__class__()

            for attr, value in obj.items():

                if isinstance(attr, bytes):
                    attr = attr.decode("utf-8")

                value = _convert(value, converted)

                new_dict[attr] = value

            obj = new_dict

        if isinstance(obj, list):
            new_list = obj.__class__()

            for item in obj:
                new_list.append(_convert(item, converted))

            obj = new_list

        elif isinstance(obj, bytes):

            try:
                obj = obj.decode("utf-8")
            except Exception:
                pass

        elif hasattr(obj, "__dict__"):

            if id(obj) in converted:
                return obj
            else:
                converted.add(id(obj))

            new__dict__ = {}

            for attr, value in obj.__dict__.items():

                if isinstance(attr, bytes):
                    attr = attr.decode("utf-8")

                new__dict__[attr] = _convert(value, converted)

            obj.__dict__ = new__dict__

        return obj

    return _convert(obj, converted)
