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
        ("statistics", "0009_auto_20181116_1627"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="componentexecutedata",
            options={
                "ordering": ["-id"],
                "verbose_name": "Pipeline\u6807\u51c6\u63d2\u4ef6\u6267\u884c\u6570\u636e",
                "verbose_name_plural": "Pipeline\u6807\u51c6\u63d2\u4ef6\u6267\u884c\u6570\u636e",
            },
        ),
        migrations.AlterModelOptions(
            name="componentintemplate",
            options={
                "verbose_name": "Pipeline\u6807\u51c6\u63d2\u4ef6\u88ab\u5f15\u7528\u6570\u636e",
                "verbose_name_plural": "Pipeline\u6807\u51c6\u63d2\u4ef6\u88ab\u5f15\u7528\u6570\u636e",
            },
        ),
        migrations.AlterField(
            model_name="componentexecutedata",
            name="archived_time",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="\u6807\u51c6\u63d2\u4ef6\u6267\u884c\u7ed3\u675f\u65f6\u95f4"
            ),
        ),
        migrations.AlterField(
            model_name="componentexecutedata",
            name="elapsed_time",
            field=models.IntegerField(
                blank=True, null=True, verbose_name="\u6807\u51c6\u63d2\u4ef6\u6267\u884c\u8017\u65f6(s)"
            ),
        ),
        migrations.AlterField(
            model_name="componentexecutedata",
            name="started_time",
            field=models.DateTimeField(verbose_name="\u6807\u51c6\u63d2\u4ef6\u6267\u884c\u5f00\u59cb\u65f6\u95f4"),
        ),
        migrations.AlterField(
            model_name="instanceinpipeline",
            name="atom_total",
            field=models.IntegerField(verbose_name="\u6807\u51c6\u63d2\u4ef6\u603b\u6570"),
        ),
        migrations.AlterField(
            model_name="templateinpipeline",
            name="atom_total",
            field=models.IntegerField(verbose_name="\u6807\u51c6\u63d2\u4ef6\u603b\u6570"),
        ),
    ]
