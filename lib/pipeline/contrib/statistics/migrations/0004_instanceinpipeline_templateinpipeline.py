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
        ("statistics", "0003_auto_20180821_2015"),
    ]

    operations = [
        migrations.CreateModel(
            name="InstanceInPipeline",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("instance_id", models.IntegerField(null=True, verbose_name="\u5b9e\u4f8bID", blank=True)),
                ("atom_total", models.IntegerField(null=True, verbose_name="\u539f\u5b50\u603b\u6570", blank=True)),
                (
                    "subprocess_total",
                    models.IntegerField(null=True, verbose_name="\u5b50\u6d41\u7a0b\u603b\u6570", blank=True),
                ),
                ("gateways_total", models.IntegerField(null=True, verbose_name="\u7f51\u5173\u603b\u6570", blank=True)),
            ],
            options={
                "verbose_name": "\u5b9e\u4f8b\u4f7f\u7528\u6570\u636e",
                "verbose_name_plural": "\u5b9e\u4f8b\u4f7f\u7528\u6570\u636e",
            },
        ),
        migrations.CreateModel(
            name="TemplateInPipeline",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("template_id", models.IntegerField(null=True, verbose_name="\u6a21\u677fID", blank=True)),
                ("atom_total", models.IntegerField(null=True, verbose_name="\u539f\u5b50\u603b\u6570", blank=True)),
                (
                    "subprocess_total",
                    models.IntegerField(null=True, verbose_name="\u5b50\u6d41\u7a0b\u603b\u6570", blank=True),
                ),
                ("gateways_total", models.IntegerField(null=True, verbose_name="\u7f51\u5173\u603b\u6570", blank=True)),
            ],
            options={
                "verbose_name": "\u6a21\u677f\u4f7f\u7528\u6570\u636e",
                "verbose_name_plural": "\u6a21\u677f\u4f7f\u7528\u6570\u636e",
            },
        ),
    ]
