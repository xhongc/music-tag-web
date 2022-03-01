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

from pipeline.core.constants import PE


def reverse_func(apps, schema_editor):
    pass


def forward_func(apps, schema_editor):
    PipelineTemplate = apps.get_model("pipeline", "PipelineTemplate")

    for template in PipelineTemplate.objects.all():
        if not template.is_deleted:
            acts = list(template.snapshot.data[PE.activities].values())
            template.has_subprocess = any([act for act in acts if act["type"] == PE.SubProcess])
            template.save()


class Migration(migrations.Migration):
    dependencies = [
        ("pipeline", "0017_pipelinetemplate_has_subprocess"),
    ]

    operations = [migrations.RunPython(forward_func, reverse_func)]
