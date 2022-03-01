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
import pipeline.django_signal_valve.models


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Signal",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("module_path", models.TextField(verbose_name="\u4fe1\u53f7\u6a21\u5757\u540d")),
                ("name", models.CharField(max_length=64, verbose_name="\u4fe1\u53f7\u5c5e\u6027\u540d")),
                ("kwargs", pipeline.django_signal_valve.models.IOField(verbose_name="\u4fe1\u53f7\u53c2\u6570")),
            ],
        ),
    ]
