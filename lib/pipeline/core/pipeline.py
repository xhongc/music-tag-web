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

from queue import Queue

from pipeline.core.flow.activity import Activity
from pipeline.core.flow.gateway import Gateway
from pipeline.exceptions import PipelineException


class PipelineSpec(object):
    def __init__(self, start_event, end_event, flows, activities, gateways, data, context):
        objects = {start_event.id: start_event, end_event.id: end_event}
        for act in activities:
            objects[act.id] = act
        for gw in gateways:
            objects[gw.id] = gw

        self.start_event = start_event
        self.end_event = end_event
        self.flows = flows
        self.activities = activities
        self.gateways = gateways
        self.data = data
        self.objects = objects
        self.context = context

    def prune(self, keep_from, keep_to):
        if keep_from != self.start_event.id:
            self.start_event.outgoing = None

        if keep_to != self.end_event.id:
            self.end_event.incoming = None

        self.activities = []
        self.gateways = []
        self.flows = []

        keep_from_node = self.objects[keep_from]
        keep_to_node = self.objects[keep_to]

        keep_from_node.incoming = None
        keep_to_node.outgoing = None

        to_be_process = Queue()
        to_be_process.put(keep_from_node)

        new_objects = {}
        keep_to_incoming_flows = []

        while not to_be_process.empty():
            node = to_be_process.get()

            if issubclass(node.__class__, Activity):
                self.activities.append(node)
            elif issubclass(node.__class__, Gateway):
                self.gateways.append(node)

            new_objects[node.id] = node

            if node.id == keep_to_node.id:
                continue

            for out in node.outgoing:

                self.flows.append(out)

                if out.target.id not in new_objects:
                    next_node = out.target
                    if next_node.id == keep_to_node.id:
                        keep_to_incoming_flows.append(out)
                    to_be_process.put(next_node)

        keep_to_node.incoming.flows = keep_to_incoming_flows
        keep_to_node.incoming.flow_dict = {}
        for flow in keep_to_incoming_flows:
            keep_to_node.incoming.flow_dict[flow.id] = flow

        self.objects = new_objects


class PipelineShell(object):
    def __init__(self, id, data):
        self.id = id
        self.data = data

    def shell(self):
        return PipelineShell(id=self.id, data=self.data)


class Pipeline(object):
    def __init__(self, id, pipeline_spec, parent=None):
        self.id = id
        self.spec = pipeline_spec
        self.parent = parent

    @property
    def data(self):
        return self.spec.data

    @property
    def context(self):
        return self.spec.context

    @property
    def start_event(self):
        return self.spec.start_event

    @property
    def end_event(self):
        return self.spec.end_event

    @property
    def all_nodes(self):
        return self.spec.objects

    def data_for_node(self, node):
        node = self.spec.objects.get(node.id)
        if not node:
            raise PipelineException("Can not find node %s in this pipeline." % node.id)
        return node.data

    def node(self, id):
        return self.spec.objects.get(id)

    def prune(self, keep_from, keep_to):
        self.spec.prune(keep_from=keep_from, keep_to=keep_to)

    def shell(self):
        return PipelineShell(id=self.id, data=self.data)
