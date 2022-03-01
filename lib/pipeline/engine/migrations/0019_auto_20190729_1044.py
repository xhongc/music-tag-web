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
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("engine", "0018_auto_20190729_1041"),
    ]

    operations = [
        migrations.AlterField(
            model_name="history",
            name="data",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="engine.HistoryData"),
        ),
        migrations.AlterField(
            model_name="pipelineprocess",
            name="snapshot",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, to="engine.ProcessSnapshot"
            ),
        ),
    ]
