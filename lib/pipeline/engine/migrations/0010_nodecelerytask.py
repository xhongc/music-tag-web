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
        ("engine", "0010_auto_20180830_1203"),
    ]

    operations = [
        migrations.CreateModel(
            name="NodeCeleryTask",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                (
                    "node_id",
                    models.CharField(unique=True, max_length=32, verbose_name="\u8282\u70b9 ID", db_index=True),
                ),
                ("celery_task_id", models.CharField(default=b"", max_length=40, verbose_name="celery \u4efb\u52a1 ID")),
            ],
        ),
    ]
