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

from django.dispatch import receiver

from pipeline.core.flow.event import EndEvent
from pipeline.core.flow.signals import post_new_end_event_register
from pipeline.validators import rules


@receiver(post_new_end_event_register, sender=EndEvent)
def post_new_end_event_register_handler(sender, node_type, node_cls, **kwargs):
    rules.NODE_RULES[node_type] = rules.SINK_RULE
    rules.FLOW_NODES_WITHOUT_STARTEVENT.append(node_type)
