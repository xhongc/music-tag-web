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
import pipeline.models


class Migration(migrations.Migration):

    dependencies = [
        ("pipeline", "0005_pipelineinstance_tree_info"),
    ]

    operations = [
        migrations.CreateModel(
            name="TreeInfo",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("data", pipeline.models.CompressJSONField(null=True, blank=True)),
            ],
        ),
        migrations.AlterField(
            model_name="pipelineinstance",
            name="tree_info",
            field=models.ForeignKey(
                related_name="tree_info",
                verbose_name="\u63d0\u524d\u8ba1\u7b97\u597d\u7684\u4e00\u4e9b\u6d41\u7a0b\u7ed3\u6784\u6570\u636e",
                to="pipeline.TreeInfo",
                null=True,
                on_delete=models.SET_NULL,
            ),
        ),
    ]
