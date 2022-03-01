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
        ("statistics", "0002_auto_20180817_1212"),
    ]

    operations = [
        migrations.RenameField(model_name="componentexecutedata", old_name="end_time", new_name="archived_time",),
        migrations.RenameField(model_name="componentexecutedata", old_name="elapse_time", new_name="elapsed_time",),
        migrations.RenameField(model_name="componentexecutedata", old_name="begin_time", new_name="started_time",),
        migrations.AddField(
            model_name="componentexecutedata",
            name="is_retry",
            field=models.BooleanField(default=False, verbose_name="\u662f\u5426\u91cd\u8bd5\u8bb0\u5f55"),
        ),
    ]
