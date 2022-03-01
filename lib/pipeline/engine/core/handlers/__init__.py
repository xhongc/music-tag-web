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

from .conditional_parallel import ConditionalParallelGatewayHandler
from .converge_gateway import ConvergeGatewayHandler
from .empty_start_event import EmptyStartEventHandler
from .endevent import EmptyEndEventHandler, ExecutableEndEventHandler
from .exclusive_gateway import ExclusiveGatewayHandler
from .parallel_gateway import ParallelGatewayHandler
from .service_activity import ServiceActivityHandler
from .subprocess import SubprocessHandler


class HandlersFactory(object):
    _handlers = {
        EmptyStartEventHandler.element_cls(): EmptyStartEventHandler(),
        EmptyEndEventHandler.element_cls(): EmptyEndEventHandler(),
        ServiceActivityHandler.element_cls(): ServiceActivityHandler(),
        SubprocessHandler.element_cls(): SubprocessHandler(),
        ExclusiveGatewayHandler.element_cls(): ExclusiveGatewayHandler(),
        ParallelGatewayHandler.element_cls(): ParallelGatewayHandler(),
        ConditionalParallelGatewayHandler.element_cls(): ConditionalParallelGatewayHandler(),
        ConvergeGatewayHandler.element_cls(): ConvergeGatewayHandler(),
        ExecutableEndEventHandler.element_cls(): ExecutableEndEventHandler(),
    }

    _cluster_roots = [ExecutableEndEventHandler.element_cls()]

    @classmethod
    def find_cluster_root_cls(cls, element):
        for root in cls._cluster_roots:
            if issubclass(type(element), root):
                return root

        return type(element)

    @classmethod
    def handlers_for(cls, element):
        handler = cls._handlers.get(cls.find_cluster_root_cls(element))
        if not handler:
            raise KeyError("handler for element({element}) not found.".format(element=element))

        return handler
