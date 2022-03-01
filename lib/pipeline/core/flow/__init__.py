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

from .activity import SubProcess  # noqa
from .activity import AbstractIntervalGenerator  # noqa

from .activity import (  # noqa
    DefaultIntervalGenerator,
    LinearIntervalGenerator,
    NullIntervalGenerator,
    Service,
    ServiceActivity,
    SquareIntervalGenerator,
    StaticIntervalGenerator,
)
from .base import SequenceFlow  # noqa
from .event import (  # noqa
    EmptyEndEvent,
    EmptyStartEvent,
    EndEvent,
    ExecutableEndEvent,
    StartEvent,
)
from .gateway import (  # noqa
    Condition,
    ConditionalParallelGateway,
    ConvergeGateway,
    ExclusiveGateway,
    ParallelGateway,
)
from .signals import post_new_end_event_register


class FlowNodeClsFactory(object):
    nodes_cls = {
        ServiceActivity.__name__: ServiceActivity,
        SubProcess.__name__: SubProcess,
        EmptyEndEvent.__name__: EmptyEndEvent,
        EmptyStartEvent.__name__: EmptyStartEvent,
        ParallelGateway.__name__: ParallelGateway,
        ConditionalParallelGateway.__name__: ConditionalParallelGateway,
        ExclusiveGateway.__name__: ExclusiveGateway,
        ConvergeGateway.__name__: ConvergeGateway,
    }

    @classmethod
    def _nodes_types_filter(cls, cls_filter):
        types = []
        for node_type, node_cls in list(cls.nodes_cls.items()):
            if not cls_filter(node_cls):
                types.append(node_type)

        return types

    @classmethod
    def node_types_without_start_event(cls):
        return cls._nodes_types_filter(cls_filter=lambda node_cls: issubclass(node_cls, StartEvent))

    @classmethod
    def node_types_without_start_end_event(cls):
        return cls._nodes_types_filter(
            cls_filter=lambda node_cls: issubclass(node_cls, EndEvent) or issubclass(node_cls, StartEvent)
        )

    @classmethod
    def get_node_cls(cls, key):
        return cls.nodes_cls.get(key)

    @classmethod
    def register_node(cls, key, node_cls):
        if key in cls.nodes_cls:
            raise KeyError("node with key({key}) is already exist: {node}".format(key=key, node=cls.nodes_cls[key]))

        cls.nodes_cls[key] = node_cls

        if issubclass(node_cls, EndEvent):
            post_new_end_event_register.send(sender=EndEvent, node_type=key, node_cls=node_cls)
