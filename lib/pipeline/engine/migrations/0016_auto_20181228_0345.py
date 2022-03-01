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
        ("engine", "0015_datasnapshot"),
    ]

    operations = [
        migrations.AddField(
            model_name="history",
            name="loop",
            field=models.IntegerField(default=1, verbose_name="\u5faa\u73af\u6b21\u6570"),
        ),
        migrations.AddField(
            model_name="history",
            name="skip",
            field=models.BooleanField(default=False, verbose_name="\u662f\u5426\u8df3\u8fc7"),
        ),
    ]
