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
import pipeline.contrib.external_plugins.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="FileSystemSource",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=128, unique=True, verbose_name="\u5305\u6e90\u540d")),
                (
                    "from_config",
                    models.BooleanField(
                        default=False,
                        verbose_name="\u662f\u5426\u662f\u4ece\u914d\u7f6e\u6587\u4ef6\u4e2d\u8bfb\u53d6\u7684",
                    ),
                ),
                (
                    "packages",
                    pipeline.contrib.external_plugins.models.fields.JSONTextField(
                        verbose_name="\u6a21\u5757\u914d\u7f6e"
                    ),
                ),
                ("path", models.TextField(verbose_name="\u6587\u4ef6\u7cfb\u7edf\u8def\u5f84")),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="GitRepoSource",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=128, unique=True, verbose_name="\u5305\u6e90\u540d")),
                (
                    "from_config",
                    models.BooleanField(
                        default=False,
                        verbose_name="\u662f\u5426\u662f\u4ece\u914d\u7f6e\u6587\u4ef6\u4e2d\u8bfb\u53d6\u7684",
                    ),
                ),
                (
                    "packages",
                    pipeline.contrib.external_plugins.models.fields.JSONTextField(
                        verbose_name="\u6a21\u5757\u914d\u7f6e"
                    ),
                ),
                ("repo_raw_address", models.TextField(verbose_name="\u6587\u4ef6\u6258\u7ba1\u4ed3\u5e93\u94fe\u63a5")),
                ("branch", models.CharField(max_length=128, verbose_name="\u5206\u652f\u540d")),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="S3Source",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=128, unique=True, verbose_name="\u5305\u6e90\u540d")),
                (
                    "from_config",
                    models.BooleanField(
                        default=False,
                        verbose_name="\u662f\u5426\u662f\u4ece\u914d\u7f6e\u6587\u4ef6\u4e2d\u8bfb\u53d6\u7684",
                    ),
                ),
                (
                    "packages",
                    pipeline.contrib.external_plugins.models.fields.JSONTextField(
                        verbose_name="\u6a21\u5757\u914d\u7f6e"
                    ),
                ),
                ("service_address", models.TextField(verbose_name="\u5bf9\u8c61\u5b58\u50a8\u670d\u52a1\u5730\u5740")),
                ("bucket", models.TextField(verbose_name="bucket \u540d")),
                ("access_key", models.TextField(verbose_name="access key")),
                ("secret_key", models.TextField(verbose_name="secret key")),
            ],
            options={"abstract": False},
        ),
    ]
