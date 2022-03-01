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

from importlib import import_module

from pipeline.conf import settings


def get_pipeline_context(obj, obj_type, data_type="data", username=""):
    """
    @summary: pipeline context hook
    @param obj: PipelineTemplete or PipelineInstance object
    @param obj_type: template or instance
    @param data_type: data(for component parent_data.inputs) or context(for pipeline root context)
    @param username:
    @return:
    """
    context = {}
    if obj_type == "template":
        context_path = settings.PIPELINE_TEMPLATE_CONTEXT
    elif obj_type == "instance":
        context_path = settings.PIPELINE_INSTANCE_CONTEXT
    else:
        return context
    if context_path:
        mod, func = context_path.rsplit(".", 1)
        mod = import_module(mod)
        func = getattr(mod, func)
        context = func(obj, data_type, username)
    if not isinstance(context, dict):
        context = {"data": context}
    return context
