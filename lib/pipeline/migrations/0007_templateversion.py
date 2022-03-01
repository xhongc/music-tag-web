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
        ("pipeline", "0006_auto_20180814_1622"),
    ]

    operations = [
        migrations.CreateModel(
            name="TemplateVersion",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                (
                    "md5",
                    models.CharField(
                        max_length=32, db_index=True, verbose_name="\u5feb\u7167\u5b57\u7b26\u4e32\u7684md5"
                    ),
                ),
                ("date", models.DateTimeField(auto_now_add=True, verbose_name="\u6dfb\u52a0\u65e5\u671f")),
                (
                    "snapshot_id",
                    models.ForeignKey(
                        verbose_name="\u6a21\u677f\u6570\u636e ID", to="pipeline.Snapshot", on_delete=models.CASCADE
                    ),
                ),
                (
                    "template_id",
                    models.ForeignKey(
                        to="pipeline.PipelineTemplate",
                        to_field="template_id",
                        verbose_name="\u6a21\u677f ID",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
        ),
    ]
