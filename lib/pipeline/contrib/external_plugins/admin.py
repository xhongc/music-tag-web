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

from django.contrib import admin

from pipeline.contrib.external_plugins.models import FileSystemSource, GitRepoSource, S3Source
from pipeline.contrib.external_plugins.models.forms import JsonFieldModelForm

# Register your models here.


@admin.register(GitRepoSource)
class GitRepoSourceAdmin(admin.ModelAdmin):
    form = JsonFieldModelForm
    list_display = ["name", "from_config", "repo_raw_address", "branch"]
    search_fields = ["name", "branch", "repo_raw_address"]


@admin.register(S3Source)
class S3SourceAdmin(admin.ModelAdmin):
    form = JsonFieldModelForm
    list_display = ["name", "from_config", "service_address", "bucket", "source_dir"]
    search_fields = ["name", "bucket", "service_address"]


@admin.register(FileSystemSource)
class FileSystemSourceAdmin(admin.ModelAdmin):
    form = JsonFieldModelForm
    list_display = ["name", "from_config", "path"]
    search_fields = ["name", "path"]
