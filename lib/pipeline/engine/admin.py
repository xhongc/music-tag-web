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
from django.utils.translation import ugettext_lazy as _

from pipeline.engine import models
from pipeline.engine.conf.function_switch import FREEZE_ENGINE
from pipeline.engine.core import api
from pipeline.service import task_service


@admin.register(models.PipelineModel)
class PipelineModelAdmin(admin.ModelAdmin):
    list_display = ["id", "process"]
    search_fields = ["id__exact", "process__id__exact"]
    raw_id_fields = ["process"]


@admin.register(models.PipelineProcess)
class PipelineProcessAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "root_pipeline_id",
        "current_node_id",
        "destination_id",
        "parent_id",
        "need_ack",
        "ack_num",
        "is_alive",
        "is_sleep",
        "is_frozen",
    ]
    search_fields = ["id__exact", "root_pipeline_id__exact", "current_node_id__exact"]
    list_filter = ["is_alive", "is_sleep"]
    raw_id_fields = ["snapshot"]


def force_fail_node(modeladmin, request, queryset):
    for item in queryset:
        task_service.forced_fail(item.id)


@admin.register(models.Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "state",
        "retry",
        "skip",
        "loop",
        "created_time",
        "started_time",
        "archived_time",
    ]
    search_fields = ["=id"]
    actions = [force_fail_node]


@admin.register(models.ScheduleService)
class ScheduleServiceAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "activity_id",
        "process_id",
        "schedule_times",
        "wait_callback",
        "is_finished",
    ]
    search_fields = ["id__exact"]
    list_filter = ["wait_callback", "is_finished"]


@admin.register(models.ProcessCeleryTask)
class ProcessCeleryTaskAdmin(admin.ModelAdmin):
    list_display = ["id", "process_id", "celery_task_id"]
    search_fields = ["id__exact", "process_id__exact"]


@admin.register(models.Data)
class DataAdmin(admin.ModelAdmin):
    list_display = ["id", "inputs", "outputs", "ex_data"]
    search_fields = ["id__exact"]


@admin.register(models.HistoryData)
class HistoryDataAdmin(admin.ModelAdmin):
    list_display = ["id", "inputs", "outputs", "ex_data"]
    search_fields = ["id__exact"]


@admin.register(models.History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ["identifier", "started_time", "archived_time"]
    search_fields = ["identifier__exact"]
    raw_id_fields = ["data"]


@admin.register(models.ScheduleCeleryTask)
class ScheduleCeleryTaskAdmin(admin.ModelAdmin):
    list_display = ["schedule_id", "celery_task_id"]
    search_fields = ["schedule_id__exact"]


@admin.register(models.NodeCeleryTask)
class NodeCeleryTaskAdmin(admin.ModelAdmin):
    list_display = ["node_id", "celery_task_id"]
    search_fields = ["node_id__exact"]


on = True
off = False

switch_hook = {FREEZE_ENGINE: {on: api.freeze, off: api.unfreeze}}


def turn_on_function(modeladmin, request, queryset):
    for item in queryset:
        if not item.is_active:
            switch_hook[item.name][on]()


def turn_off_function(modeladmin, request, queryset):
    for item in queryset:
        if item.is_active:
            switch_hook[item.name][off]()


turn_on_function.short_description = _("打开所选的功能")
turn_off_function.short_description = _("关闭所选的功能")


@admin.register(models.FunctionSwitch)
class FunctionAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "is_active"]
    search_fields = ["name", "description"]
    actions = [turn_on_function, turn_off_function]

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super(FunctionAdmin, self).get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def get_readonly_fields(self, request, obj=None):
        if obj:  # obj is not None, so this is an edit
            return [
                "name",
                "is_active",
            ]  # Return a list or tuple of readonly fields' names
        else:  # This is an addition
            return []


def resend_task(modeladmin, request, queryset):
    for item in queryset:
        item.resend()


@admin.register(models.SendFailedCeleryTask)
class SendFailedCeleryTaskAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "kwargs",
        "type",
        "extra_kwargs",
        "exec_trace",
        "created_at",
    ]
    search_fields = ["id__exact", "name"]
    actions = [resend_task]
