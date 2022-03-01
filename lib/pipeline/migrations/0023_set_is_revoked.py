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

from __future__ import unicode_literals

from django.db import migrations

from pipeline.engine import states


def reverse_func(apps, schema_editor):
    pass


def forward_func(apps, schema_editor):
    PipelineInstance = apps.get_model("pipeline", "PipelineInstance")
    Status = apps.get_model("engine", "Status")

    revoked_status = Status.objects.filter(state=states.REVOKED).values("id", "archived_time")
    id_to_time = {status["id"]: status["archived_time"] for status in revoked_status}
    instances = PipelineInstance.objects.filter(instance_id__in=list(id_to_time.keys()))
    for inst in instances:
        inst.finish_time = id_to_time[inst.instance_id]
        inst.is_revoked = True
        inst.save()


class Migration(migrations.Migration):
    dependencies = [
        ("pipeline", "0022_pipelineinstance_is_revoked"),
    ]

    operations = [migrations.RunPython(forward_func, reverse_func)]
