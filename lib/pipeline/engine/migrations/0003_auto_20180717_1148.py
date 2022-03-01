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
        ("engine", "0002_auto_20180109_1825"),
    ]

    operations = [
        migrations.CreateModel(
            name="FunctionSwitch",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("name", models.CharField(max_length=32, verbose_name="\u529f\u80fd\u540d\u79f0")),
                ("description", models.TextField(default=b"", verbose_name="\u529f\u80fd\u63cf\u8ff0")),
                ("is_active", models.BooleanField(default=False, verbose_name="\u662f\u5426\u6fc0\u6d3b")),
            ],
        ),
        migrations.AddField(
            model_name="pipelineprocess",
            name="is_froze",
            field=models.BooleanField(default=False, verbose_name="\u8be5 process \u662f\u5426\u88ab\u51bb\u7ed3"),
        ),
        migrations.AddField(
            model_name="scheduleservice",
            name="celery_id",
            field=models.CharField(default=b"", max_length=36, verbose_name="celery \u4efb\u52a1ID"),
        ),
        migrations.AddField(
            model_name="scheduleservice",
            name="celery_info_lock",
            field=models.IntegerField(default=0, verbose_name="celery \u4fe1\u606f\u66f4\u65b0\u9501"),
        ),
        migrations.AddField(
            model_name="scheduleservice",
            name="is_frozen",
            field=models.BooleanField(default=False, verbose_name="\u662f\u5426\u88ab\u51bb\u7ed3"),
        ),
        migrations.AddField(
            model_name="scheduleservice",
            name="is_scheduling",
            field=models.BooleanField(default=False, verbose_name="\u662f\u5426\u6b63\u5728\u88ab\u8c03\u5ea6"),
        ),
        migrations.AddField(
            model_name="scheduleservice",
            name="schedule_date",
            field=models.DateTimeField(
                null=True, verbose_name="\u4e0b\u4e00\u6b21\u88ab\u8c03\u5ea6\u7684\u65f6\u95f4"
            ),
        ),
    ]
