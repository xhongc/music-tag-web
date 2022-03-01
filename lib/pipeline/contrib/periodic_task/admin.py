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

from pipeline.contrib.periodic_task import models


@admin.register(models.PeriodicTask)
class PeriodicTaskAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "total_run_count", "last_run_at", "creator"]
    search_fields = ["id", "name"]
    raw_id_fields = ["template", "celery_task", "snapshot"]


@admin.register(models.PeriodicTaskHistory)
class PeriodicTaskHistoryAdmin(admin.ModelAdmin):
    list_display = ["id", "start_at", "ex_data", "start_success", "periodic_task"]
    search_fields = ["periodic_task__id"]
    raw_id_fields = ["periodic_task", "pipeline_instance"]
