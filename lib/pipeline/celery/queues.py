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


class ScalableQueues(object):
    _queues = {}

    @classmethod
    def queues(cls):
        return cls._queues

    @classmethod
    def add(cls, name, routing_key="", queue_arguments=None):
        queue_arguments = queue_arguments or {}
        cls._queues[name] = {"name": name, "routing_key": routing_key or name, "queue_arguments": queue_arguments}

    @classmethod
    def has_queue(cls, queue):
        return queue in cls._queues

    @classmethod
    def routing_key_for(cls, queue):
        return cls._queues[queue]["routing_key"]
