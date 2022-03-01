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

from .models import ComponentExecuteData, ComponentInTemplate, InstanceInPipeline, TemplateInPipeline


@admin.register(ComponentInTemplate)
class ComponentInTemplateAdmin(admin.ModelAdmin):
    list_display = ("id", "component_code", "template_id", "node_id", "is_sub", "version")
    search_fields = (
        "template_id",
        "node_id",
    )
    list_filter = ("component_code", "is_sub")


@admin.register(ComponentExecuteData)
class ComponentExecuteDataAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "component_code",
        "instance_id",
        "node_id",
        "is_sub",
        "started_time",
        "archived_time",
        "elapsed_time",
        "status",
        "is_skip",
        "is_retry",
        "version",
    )
    search_fields = (
        "instance_id",
        "node_id",
    )
    list_filter = (
        "component_code",
        "is_sub",
        "status",
        "is_skip",
    )


@admin.register(TemplateInPipeline)
class TemplateInPipelineAdmin(admin.ModelAdmin):
    list_display = ("template_id", "atom_total", "subprocess_total", "gateways_total")

    search_fields = ("template_id",)
    list_filter = ("template_id", "atom_total", "subprocess_total", "gateways_total")


@admin.register(InstanceInPipeline)
class InstanceInPipelineAdmin(admin.ModelAdmin):
    list_display = ("instance_id", "atom_total", "subprocess_total", "gateways_total")

    search_fields = ("instance_id",)
    list_filter = ("instance_id", "atom_total", "subprocess_total", "gateways_total")
