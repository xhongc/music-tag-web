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

from typing import List

from bamboo_engine.eri import ExecutableEvent

from pipeline.core.flow.event import ExecutableEndEvent


class ExecutableEndEventWrapper(ExecutableEvent):
    def __init__(self, end_event: ExecutableEndEvent):
        self.end_event = end_event

    def execute(self, pipeline_stack: List[str], root_pipeline_id: str):
        """
        execute 逻辑

        :param pipeline_stack: 流程栈
        :type pipeline_stack: List[str]
        :param root_pipeline_id: 根流程 ID
        :type root_pipeline_id: str
        """
        in_subprocess = len(pipeline_stack) > 1
        current_pipeline_id = pipeline_stack[-1]

        return self.end_event.execute(in_subprocess, root_pipeline_id, current_pipeline_id)
