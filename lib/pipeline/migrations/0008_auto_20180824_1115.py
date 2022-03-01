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


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pipeline", "0007_templaterelationship"),
        ("pipeline", "0007_templateversion"),
    ]

    operations = [
        migrations.RenameField(model_name="templateversion", old_name="snapshot_id", new_name="snapshot",),
        migrations.RemoveField(model_name="templateversion", name="template_id",),
        migrations.AddField(
            model_name="templateversion",
            name="template",
            field=models.ForeignKey(
                default="", verbose_name="\u6a21\u677f ID", to="pipeline.PipelineTemplate", on_delete=models.CASCADE
            ),
            preserve_default=False,
        ),
    ]
