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

from pipeline.eri import models


@admin.register(models.Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "parent_id",
        "ack_num",
        "need_ack",
        "asleep",
        "suspended",
        "frozen",
        "dead",
        "root_pipeline_id",
        "current_node_id",
    ]
    search_fields = ["root_pipeline_id__exact", "current_node_id__exact", "suspended_by__exact"]


@admin.register(models.Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ["id", "node_id", "detail"]
    search_fields = ["node_id__exact"]


@admin.register(models.State)
class StateAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "node_id",
        "root_id",
        "parent_id",
        "name",
        "version",
        "loop",
        "created_time",
        "started_time",
        "archived_time",
    ]
    search_fields = ["node_id__exact", "root_id__exact", "parent_id__exact"]


@admin.register(models.Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ["id", "type", "process_id", "node_id", "finished", "expired", "version", "schedule_times"]
    search_fields = ["node_id__exact"]


@admin.register(models.Data)
class DataAdmin(admin.ModelAdmin):
    list_display = ["id", "node_id", "inputs", "outputs"]
    search_fields = ["node_id__exact"]


@admin.register(models.ExecutionData)
class ExecutionDataAdmin(admin.ModelAdmin):
    list_display = ["id", "node_id", "inputs", "outputs"]
    search_fields = ["node_id__exact"]


@admin.register(models.CallbackData)
class CallbackDataAdmin(admin.ModelAdmin):
    list_display = ["id", "node_id", "version", "data"]
    search_fields = ["id__exact"]


@admin.register(models.ContextValue)
class ContextValueAdmin(admin.ModelAdmin):
    list_display = ["id", "pipeline_id", "key", "type", "serializer", "value"]
    search_fields = ["pipeline_id__exact"]


@admin.register(models.ContextOutputs)
class ContextOutputsAdmin(admin.ModelAdmin):
    list_display = ["id", "pipeline_id", "outputs"]
    search_fields = ["pipeline_id__exact"]


@admin.register(models.ExecutionHistory)
class ExecutionHistoryAdmin(admin.ModelAdmin):
    list_display = ["id", "node_id", "loop", "started_time", "archived_time"]
    search_fields = ["node_id__exact"]


@admin.register(models.LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ["id", "node_id", "version", "level_name", "message", "logged_at"]
    search_fields = ["node_id__exact"]
