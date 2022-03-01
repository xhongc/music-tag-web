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

from pipeline.constants import PIPELINE_DEFAULT_PRIORITY
from pipeline.engine import api
from pipeline.log.models import LogEntry

STATE_MAP = {
    "CREATED": "RUNNING",
    "READY": "RUNNING",
    "RUNNING": "RUNNING",
    "BLOCKED": "BLOCKED",
    "SUSPENDED": "SUSPENDED",
    "FINISHED": "FINISHED",
    "FAILED": "FAILED",
    "REVOKED": "REVOKED",
}


def run_pipeline(pipeline_instance, instance_id=None, check_workers=True, priority=PIPELINE_DEFAULT_PRIORITY, queue=""):
    return api.start_pipeline(pipeline_instance, check_workers=check_workers, priority=priority, queue=queue)


def pause_pipeline(pipeline_id):
    return api.pause_pipeline(pipeline_id)


def revoke_pipeline(pipeline_id):
    return api.revoke_pipeline(pipeline_id)


def resume_pipeline(pipeline_id):
    return api.resume_pipeline(pipeline_id)


def pause_activity(act_id):
    return api.pause_node_appointment(act_id)


def resume_activity(act_id):
    return api.resume_node_appointment(act_id)


def retry_activity(act_id, inputs=None):
    return api.retry_node(act_id, inputs=inputs)


def skip_activity(act_id):
    return api.skip_node(act_id)


def pause_subprocess(subprocess_id):
    return api.pause_subprocess(subprocess_id)


def skip_exclusive_gateway(gateway_id, flow_id):
    return api.skip_exclusive_gateway(gateway_id, flow_id)


def skip_conditional_parallel_gateway(gateway_id, flow_ids, converge_gateway_id):
    return api.skip_conditional_parallel_gateway(gateway_id, flow_ids, converge_gateway_id)


def forced_fail(node_id, ex_data=""):
    return api.forced_fail(node_id, ex_data=ex_data)


def get_inputs(act_id):
    return api.get_inputs(act_id)


def get_outputs(act_id):
    return api.get_outputs(act_id)


def get_activity_histories(act_id):
    histories = api.get_activity_histories(act_id)
    for item in histories:
        item["started_time"] = _better_time_or_none(item["started_time"])
        item["finished_time"] = _better_time_or_none(item.pop("archived_time"))
    return histories


def callback(act_id, data=None):
    return api.activity_callback(act_id, data)


def get_state(node_id):
    tree = api.get_status_tree(node_id, max_depth=100)

    res = _map(tree)

    # collect all atom
    descendants = {}
    _collect_descendants(tree, descendants)
    res["children"] = descendants

    # return
    return res


def _get_node_state(tree):
    status = []

    # return state when meet leaf
    if not tree.get("children", []):
        return STATE_MAP[tree["state"]]

    # iterate children and get child state recursively
    for identifier_code, child_tree in list(tree["children"].items()):
        status.append(_get_node_state(child_tree))

    # summary parent state
    return STATE_MAP[_get_parent_state_from_children_state(tree["state"], status)]


def _get_parent_state_from_children_state(parent_state, children_state_list):
    """
    @summary: 根据子任务状态计算父任务状态
    @param parent_state:
    @param children_state_list:
    @return:
    """
    children_state_set = set(children_state_list)
    if parent_state == "BLOCKED":
        if "RUNNING" in children_state_set:
            parent_state = "RUNNING"
        if "FAILED" in children_state_set:
            parent_state = "FAILED"
    return parent_state


def _collect_descendants(tree, descendants):
    # iterate children for tree
    for identifier_code, child_tree in list(tree["children"].items()):
        child_status = _map(child_tree)
        descendants[identifier_code] = child_status

        # collect children
        if child_tree["children"]:
            _collect_descendants(child_tree, descendants)


def _better_time_or_none(time):
    return time.strftime("%Y-%m-%d %H:%M:%S") if time else time


def _map(tree):
    tree.setdefault("children", {})
    return {
        "id": tree["id"],
        "state": _get_node_state(tree),
        "start_time": _better_time_or_none(tree["started_time"]),
        "finish_time": _better_time_or_none(tree["archived_time"]),
        "loop": tree["loop"],
        "retry": tree["retry"],
        "skip": tree["skip"],
    }


def get_plain_log_for_node(node_id, history_id):
    return LogEntry.objects.plain_log_for_node(node_id=node_id, history_id=history_id)
