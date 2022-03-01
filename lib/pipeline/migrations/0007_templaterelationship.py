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
            name="TemplateRelationship",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("ancestor_template_id", models.CharField(max_length=32, verbose_name="\u6839\u6a21\u677fID")),
                (
                    "descendant_template_id",
                    models.CharField(max_length=32, verbose_name="\u5b50\u6d41\u7a0b\u6a21\u677fID"),
                ),
                ("refer_sum", models.IntegerField(verbose_name="\u5f15\u7528\u6b21\u6570")),
            ],
        ),
    ]
