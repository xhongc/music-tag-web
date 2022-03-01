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
        ("pipeline", "0008_auto_20180824_1115"),
    ]

    operations = [
        migrations.RemoveField(model_name="templaterelationship", name="refer_sum",),
        migrations.AddField(
            model_name="templaterelationship",
            name="subprocess_node_id",
            field=models.CharField(default="", max_length=32, verbose_name="\u5b50\u6d41\u7a0b\u8282\u70b9 ID"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="templaterelationship",
            name="version",
            field=models.CharField(default="", max_length=32, verbose_name="\u5feb\u7167\u5b57\u7b26\u4e32\u7684md5"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="templaterelationship",
            name="ancestor_template_id",
            field=models.CharField(max_length=32, verbose_name="\u6839\u6a21\u677fID", db_index=True),
        ),
    ]
