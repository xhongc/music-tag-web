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

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("component_framework", "0004_auto_20180413_1800"),
    ]

    operations = [
        migrations.AddField(
            model_name="componentmodel",
            name="version",
            field=models.CharField(default=b"legacy", max_length=64, verbose_name="\u7ec4\u4ef6\u7248\u672c"),
        ),
        migrations.AlterField(
            model_name="componentmodel",
            name="code",
            field=models.CharField(max_length=255, verbose_name="\u7ec4\u4ef6\u7f16\u7801"),
        ),
    ]
