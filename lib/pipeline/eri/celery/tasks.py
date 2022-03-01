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
from typing import Optional

from celery import task

from bamboo_engine import states
from bamboo_engine.engine import Engine

from pipeline.eri.runtime import BambooDjangoRuntime


@task(ignore_result=True)
def execute(process_id: int, node_id: str, root_pipeline_id: str = None, parent_pipeline_id: str = None):
    runtime = BambooDjangoRuntime()
    Engine(runtime).execute(
        process_id=process_id, node_id=node_id, root_pipeline_id=root_pipeline_id, parent_pipeline_id=parent_pipeline_id
    )


@task(ignore_result=True)
def schedule(process_id: int, node_id: str, schedule_id: str, callback_data_id: Optional[int]):
    runtime = BambooDjangoRuntime()
    Engine(runtime).schedule(
        process_id=process_id, node_id=node_id, schedule_id=schedule_id, callback_data_id=callback_data_id
    )


@task(ignore_result=True)
def timeout_check(self, process_id: int, node_id: str, version: str):
    runtime = BambooDjangoRuntime()
    state = runtime.get_state(node_id=node_id)
    if state.name == states.RUNNING and state.version == version:
        Engine(runtime).forced_fail_activity(node_id=node_id, ex_data="timeout kill")
