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

from django.db.models.signals import post_save
from django.dispatch import receiver

from pipeline.component_framework.constants import LEGACY_PLUGINS_VERSION
from pipeline.contrib.statistics.models import (
    ComponentInTemplate,
    TemplateInPipeline,
)
from pipeline.contrib.statistics.tasks import pipeline_post_save_statistics_task, pipeline_archive_statistics_task
from pipeline.contrib.statistics.utils import count_pipeline_tree_nodes
from pipeline.core.constants import PE
from pipeline.models import PipelineInstance, PipelineTemplate
from pipeline.signals import post_pipeline_finish, post_pipeline_revoke

logger = logging.getLogger("root")


@receiver(post_save, sender=PipelineTemplate)
def template_post_save_handler(sender, instance, created, **kwargs):
    """
    模板执行保存处理
    :param sender:
    :param instance: 任务实例 Instance.Object对象
    :param created: 是否是创建（可为更新）
    :param kwargs: 参数序列
    :return:
    """
    template = instance
    template_id = template.template_id
    # 删除原先该项模板数据（无论是更新还是创建，都需要重新创建统计数据）
    ComponentInTemplate.objects.filter(template_id=template_id).delete()
    data = template.data
    component_list = []
    # 任务节点引用标准插件统计（包含间接通过子流程引用）
    for act_id, act in data[PE.activities].items():
        # 标准插件节点直接引用
        if act["type"] == PE.ServiceActivity:
            component = ComponentInTemplate(
                component_code=act["component"]["code"],
                template_id=template_id,
                node_id=act_id,
                version=act["component"].get("version", LEGACY_PLUGINS_VERSION),
            )
            component_list.append(component)
        # 子流程节点间接引用
        else:
            components = ComponentInTemplate.objects.filter(template_id=act["template_id"]).values(
                "subprocess_stack", "component_code", "node_id", "version"
            )
            for component_sub in components:
                # 子流程的执行堆栈（子流程的执行过程）
                stack = json.loads(component_sub["subprocess_stack"])
                # 添加节点id
                stack.insert(0, act_id)
                component = ComponentInTemplate(
                    component_code=component_sub["component_code"],
                    template_id=template_id,
                    node_id=component_sub["node_id"],
                    is_sub=True,
                    subprocess_stack=json.dumps(stack),
                    version=component_sub["version"],
                )
                component_list.append(component)
    ComponentInTemplate.objects.bulk_create(component_list)

    # 统计流程标准插件个数，子流程个数，网关个数
    atom_total, subprocess_total, gateways_total = count_pipeline_tree_nodes(template.data)
    TemplateInPipeline.objects.update_or_create(
        template_id=template_id,
        defaults={"atom_total": atom_total, "subprocess_total": subprocess_total, "gateways_total": gateways_total},
    )


@receiver(post_save, sender=PipelineInstance)
def pipeline_post_save_handler(sender, instance, created, **kwargs):
    try:
        if created:
            pipeline_post_save_statistics_task.delay(instance_id=instance.instance_id)
    except Exception:
        logger.exception("pipeline_post_save_handler[instance_id={}] send message error".format(instance.id))


@receiver(post_pipeline_finish, sender=PipelineInstance)
def pipeline_post_finish_handler(sender, instance_id, **kwargs):
    try:
        pipeline_archive_statistics_task.delay(instance_id=instance_id)
    except Exception:
        logger.exception("pipeline_post_finish_handler[instance_id={}] send message error".format(instance_id))


@receiver(post_pipeline_revoke, sender=PipelineInstance)
def pipeline_post_revoke_handler(sender, instance_id, **kwargs):
    try:
        pipeline_archive_statistics_task.delay(instance_id=instance_id)
    except Exception:
        logger.exception("pipeline_post_revoke_handler[instance_id={}] send message error".format(instance_id))
