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
        ("statistics", "0008_auto_20181116_1448"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="componentintemplate",
            options={
                "verbose_name": "Pipeline\u539f\u5b50\u88ab\u5f15\u7528\u6570\u636e",
                "verbose_name_plural": "Pipeline\u539f\u5b50\u88ab\u5f15\u7528\u6570\u636e",
            },
        ),
        migrations.AlterModelOptions(
            name="instanceinpipeline",
            options={
                "verbose_name": "Pipeline\u5b9e\u4f8b\u5f15\u7528\u6570\u636e",
                "verbose_name_plural": "Pipeline\u5b9e\u4f8b\u5f15\u7528\u6570\u636e",
            },
        ),
        migrations.AlterModelOptions(
            name="templateinpipeline",
            options={
                "verbose_name": "Pipeline\u6a21\u677f\u5f15\u7528\u6570\u636e",
                "verbose_name_plural": "Pipeline\u6a21\u677f\u5f15\u7528\u6570\u636e",
            },
        ),
    ]
