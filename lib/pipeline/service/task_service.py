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

import importlib

from pipeline.conf import settings
from pipeline.constants import PIPELINE_DEFAULT_PRIORITY

adapter_api = importlib.import_module(settings.PIPELINE_ENGINE_ADAPTER_API)


def run_pipeline(pipeline, instance_id=None, check_workers=True, priority=PIPELINE_DEFAULT_PRIORITY, queue=""):
    return adapter_api.run_pipeline(pipeline, instance_id, check_workers=check_workers, priority=priority, queue=queue)


def pause_pipeline(pipeline_id):
    return adapter_api.pause_pipeline(pipeline_id)


def revoke_pipeline(pipeline_id):
    return adapter_api.revoke_pipeline(pipeline_id)


def resume_pipeline(pipeline_id):
    return adapter_api.resume_pipeline(pipeline_id)


def pause_activity(act_id):
    return adapter_api.pause_activity(act_id)


def resume_activity(act_id):
    return adapter_api.resume_activity(act_id)


def retry_activity(act_id, inputs=None):
    return adapter_api.retry_activity(act_id, inputs=inputs)


def skip_activity(act_id):
    return adapter_api.skip_activity(act_id)


def skip_exclusive_gateway(gateway_id, flow_id):
    return adapter_api.skip_exclusive_gateway(gateway_id, flow_id)


def skip_conditional_parallel_gateway(gateway_id, flow_ids, converge_gateway_id):
    return adapter_api.skip_conditional_parallel_gateway(gateway_id, flow_ids, converge_gateway_id)


def forced_fail(act_id, ex_data=""):
    return adapter_api.forced_fail(act_id, ex_data)


def get_state(node_id):
    return adapter_api.get_state(node_id)


def get_topo_tree(pipeline_id):
    return adapter_api.get_topo_tree(pipeline_id)


def get_inputs(act_id):
    return adapter_api.get_inputs(act_id)


def get_outputs(act_id):
    return adapter_api.get_outputs(act_id)


def get_activity_histories(act_id):
    return adapter_api.get_activity_histories(act_id)


def callback(act_id, data=None):
    return adapter_api.callback(act_id, data)


def get_plain_log_for_node(node_id, history_id=-1):
    return adapter_api.get_plain_log_for_node(node_id, history_id)
