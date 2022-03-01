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

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ComponentExecuteData",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("tag_code", models.CharField(max_length=255, verbose_name="\u7ec4\u4ef6\u7f16\u7801")),
                ("instance_id", models.CharField(max_length=32, verbose_name="\u5b9e\u4f8bID")),
                ("node_id", models.CharField(max_length=32, verbose_name="\u8282\u70b9ID")),
                (
                    "is_sub",
                    models.BooleanField(default=False, verbose_name="\u662f\u5426\u5b50\u6d41\u7a0b\u5f15\u7528"),
                ),
                (
                    "subprocess_stack",
                    models.TextField(
                        default=b"[]",
                        help_text="JSON \u683c\u5f0f\u7684\u5217\u8868",
                        verbose_name="\u5b50\u6d41\u7a0b\u5806\u6808",
                    ),
                ),
                ("begin_time", models.DateTimeField(verbose_name="\u539f\u5b50\u6267\u884c\u5f00\u59cb\u65f6\u95f4")),
                (
                    "end_time",
                    models.DateTimeField(
                        null=True, verbose_name="\u539f\u5b50\u6267\u884c\u7ed3\u675f\u65f6\u95f4", blank=True
                    ),
                ),
                (
                    "elapse_time",
                    models.IntegerField(null=True, verbose_name="\u539f\u5b50\u6267\u884c\u8017\u65f6(s)", blank=True),
                ),
                ("status", models.BooleanField(default=False, verbose_name="\u662f\u5426\u6267\u884c\u6210\u529f")),
                ("is_skip", models.BooleanField(default=False, verbose_name="\u662f\u5426\u8df3\u8fc7")),
            ],
            options={
                "ordering": ["-id"],
                "verbose_name": "Pipeline\u539f\u5b50\u6267\u884c\u6570\u636e",
                "verbose_name_plural": "Pipeline\u539f\u5b50\u6267\u884c\u6570\u636e",
            },
        ),
        migrations.CreateModel(
            name="ComponentInTemplate",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("component_code", models.CharField(max_length=255, verbose_name="\u7ec4\u4ef6\u7f16\u7801")),
                ("template_id", models.CharField(max_length=32, verbose_name="\u6a21\u677fID")),
                ("node_id", models.CharField(max_length=32, verbose_name="\u8282\u70b9ID")),
                (
                    "is_sub",
                    models.BooleanField(default=False, verbose_name="\u662f\u5426\u5b50\u6d41\u7a0b\u5f15\u7528"),
                ),
                (
                    "subprocess_stack",
                    models.TextField(
                        default=b"[]",
                        help_text="JSON \u683c\u5f0f\u7684\u5217\u8868",
                        verbose_name="\u5b50\u6d41\u7a0b\u5806\u6808",
                    ),
                ),
            ],
            options={
                "verbose_name": "Pipeline\u539f\u5b50\u5f15\u7528\u6570\u636e",
                "verbose_name_plural": "Pipeline\u539f\u5b50\u5f15\u7528\u6570\u636e",
            },
        ),
    ]
