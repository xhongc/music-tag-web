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


import logging
import ujson as json
from copy import deepcopy

from celery import task
from bamboo_engine import api as bamboo_engine_api

from pipeline.component_framework.constants import LEGACY_PLUGINS_VERSION
from pipeline.contrib.statistics.models import (
    ComponentExecuteData,
    InstanceInPipeline,
)
from pipeline.contrib.statistics.utils import count_pipeline_tree_nodes
from pipeline.core.constants import PE
from pipeline.engine import api as pipeline_api
from pipeline.engine import states
from pipeline.engine.exceptions import InvalidOperationException
from pipeline.engine.utils import calculate_elapsed_time
from pipeline.models import PipelineInstance
from pipeline.eri.runtime import BambooDjangoRuntime

logger = logging.getLogger("celery")


def recursive_collect_components(activities, status_tree, instance_id, stack=None, engine_ver=1):
    """
    @summary 递归流程树，获取所有执行成功/失败的插件
    @param activities: 当前流程树的任务节点信息
    @param status_tree: 当前流程树的任务节点状态
    @param instance_id: 根流程的示例 instance_id
    @param stack: 子流程堆栈
    """
    if stack is None:
        stack = []
        is_sub = False
    else:
        is_sub = True
    component_list = []
    for act_id, act in activities.items():
        # 只有执行了才会查询到 status，兼容中途撤销的任务
        if act_id in status_tree:
            exec_act = status_tree[act_id]
            # 属于标准插件节点
            if act[PE.type] == PE.ServiceActivity:
                if exec_act["state"] in states.ARCHIVED_STATES:
                    create_kwargs = {
                        "component_code": act["component"]["code"],
                        "instance_id": instance_id,
                        "is_sub": is_sub,
                        "node_id": act_id,
                        "subprocess_stack": json.dumps(stack),
                        "started_time": exec_act["started_time"],
                        "archived_time": exec_act["archived_time"],
                        "elapsed_time": exec_act.get(
                            "elapsed_time", calculate_elapsed_time(exec_act["started_time"], exec_act["archived_time"])
                        ),
                        "is_skip": exec_act["skip"],
                        "is_retry": False,
                        "status": exec_act["state"] == "FINISHED",
                        "version": act["component"].get("version", LEGACY_PLUGINS_VERSION),
                    }
                    component_list.append(ComponentExecuteData(**create_kwargs))
                    if exec_act["retry"] > 0:
                        # 需要通过执行历史获得
                        if engine_ver == 1:
                            history_list = pipeline_api.get_activity_histories(act_id)
                        else:
                            history_list_result = bamboo_engine_api.get_node_short_histories(
                                runtime=BambooDjangoRuntime(), node_id=act_id
                            )
                            history_list = history_list_result.data if history_list_result.result else []

                        for history in history_list:
                            create_kwargs.update(
                                {
                                    "started_time": history["started_time"],
                                    "archived_time": history["archived_time"],
                                    "elapsed_time": history.get(
                                        "elapsed_time",
                                        calculate_elapsed_time(history["started_time"], history["archived_time"]),
                                    ),
                                    "is_retry": True,
                                    "is_skip": False,
                                    "status": False,
                                }
                            )
                            component_list.append(ComponentExecuteData(**create_kwargs))
            # 子流程的执行堆栈（子流程的执行过程）
            elif act[PE.type] == PE.SubProcess:
                # 递归子流程树
                sub_activities = act[PE.pipeline][PE.activities]
                # 防止stack共用
                copied_stack = deepcopy(stack)
                copied_stack.insert(0, act_id)
                component_list += recursive_collect_components(
                    sub_activities, exec_act["children"], instance_id, copied_stack
                )
    return component_list


@task
def pipeline_post_save_statistics_task(instance_id):
    instance = PipelineInstance.objects.get(instance_id=instance_id)
    # 统计流程标准插件个数，子流程个数，网关个数
    try:
        atom_total, subprocess_total, gateways_total = count_pipeline_tree_nodes(instance.execution_data)
        InstanceInPipeline.objects.update_or_create(
            instance_id=instance_id,
            defaults={
                "atom_total": atom_total,
                "subprocess_total": subprocess_total,
                "gateways_total": gateways_total,
            },
        )
    except Exception as e:
        logger.error(
            (
                "pipeline_post_save_handler save InstanceInPipeline[instance_id={instance_id}] " "raise error: {error}"
            ).format(instance_id=instance_id, error=e)
        )


@task
def pipeline_archive_statistics_task(instance_id):
    instance = PipelineInstance.objects.get(instance_id=instance_id)
    engine_ver = 1
    # 获得任务实例的执行树
    try:
        status_tree = pipeline_api.get_status_tree(instance_id, 99)
    except InvalidOperationException:
        engine_ver = 2
        status_tree_result = bamboo_engine_api.get_pipeline_states(
            runtime=BambooDjangoRuntime(), root_id=instance_id, flat_children=False
        )
        if not status_tree_result.result:
            logger.error(
                "pipeline_archive_statistics_task bamboo_engine_api.get_pipeline_states fail: {}".format(
                    status_tree_result.result.exc_trace
                )
            )
            return
        status_tree = status_tree_result.data[instance_id]

    # 删除原有标准插件数据
    ComponentExecuteData.objects.filter(instance_id=instance_id).delete()
    # 获得任务实例的执行数据
    data = instance.execution_data
    try:
        component_list = recursive_collect_components(
            activities=data[PE.activities],
            status_tree=status_tree["children"],
            instance_id=instance_id,
            engine_ver=engine_ver,
        )
        ComponentExecuteData.objects.bulk_create(component_list)
    except Exception:
        logger.exception(
            ("pipeline_post_save_handler save ComponentExecuteData[instance_id={instance_id}] raise error").format(
                instance_id=instance_id
            )
        )
