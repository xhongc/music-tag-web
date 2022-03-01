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
import pipeline.engine.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ("engine", "0011_auto_20180830_1205"),
    ]

    operations = [
        migrations.CreateModel(
            name="DataSnapshot",
            fields=[
                (
                    "key",
                    models.CharField(
                        max_length=255, serialize=False, verbose_name="\u5bf9\u8c61\u552f\u4e00\u952e", primary_key=True
                    ),
                ),
                ("obj", pipeline.engine.models.fields.IOField(verbose_name="\u5bf9\u8c61\u5b58\u50a8\u5b57\u6bb5")),
            ],
        ),
    ]
