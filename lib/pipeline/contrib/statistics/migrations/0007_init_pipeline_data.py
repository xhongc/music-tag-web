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

from django.db import migrations

from pipeline.models import PipelineInstance, PipelineTemplate
from pipeline.contrib.statistics.models import InstanceInPipeline, TemplateInPipeline


def load_data(apps, schema_editor):
    # 清空数据
    TemplateInPipeline.objects.all().delete()
    InstanceInPipeline.objects.all().delete()
    template_list = PipelineTemplate.objects.filter(is_deleted=False)
    template_data = []
    for template in template_list:
        template_id = template.template_id
        try:
            result = statistics_total(template.data)
            data = TemplateInPipeline(
                template_id=template_id,
                atom_total=result["atom_total"],
                subprocess_total=result["subprocess_total"],
                gateways_total=result["gateways_total"],
            )
            template_data.append(data)
        except Exception:
            pass
    TemplateInPipeline.objects.bulk_create(template_data)

    instance_list = PipelineInstance.objects.filter(is_deleted=False)
    instance_data = []
    for instance in instance_list:
        instance_id = instance.instance_id
        try:
            result = statistics_total(instance.execution_data)
            data = InstanceInPipeline(
                instance_id=instance_id,
                atom_total=result["atom_total"],
                subprocess_total=result["subprocess_total"],
                gateways_total=result["gateways_total"],
            )
            instance_data.append(data)
        except Exception:
            pass
    InstanceInPipeline.objects.bulk_create(instance_data)


def statistics_total(pipeline_tree):
    atom_total = 0
    subprocess_total = 0
    tree_activities = pipeline_tree["activities"]
    # 获取网关数量
    gateways_total = len(pipeline_tree["gateways"])

    # 遍历activities节点
    for activity in tree_activities:
        activity_type = tree_activities[activity]["type"]
        if activity_type == "ServiceActivity":
            atom_total += 1
        elif activity_type == "SubProcess":
            subprocess_total += 1
    return {"atom_total": atom_total, "subprocess_total": subprocess_total, "gateways_total": gateways_total}


class Migration(migrations.Migration):
    dependencies = [("statistics", "0006_auto_20181115_1208")]
    operations = [migrations.RunPython(load_data)]
