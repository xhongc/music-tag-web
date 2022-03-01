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

from django.conf import settings

# pipeline template context module, to use this, you need
#   1) config PIPELINE_TEMPLATE_CONTEXT in your django settings, such as
#       PIPELINE_TEMPLATE_CONTEXT = 'home_application.utils.get_template_context'
#   2) define get_template_context function in your app, which show accept one arg, such as
#         def get_template_context(obj):
#             context = {
#                 'biz_cc_id': '1',
#                 'biz_cc_name': 'test1',
#             }
#             if obj is not None:
#                 context.update({'template': '1'})
#             return context

PIPELINE_TEMPLATE_CONTEXT = getattr(settings, "PIPELINE_TEMPLATE_CONTEXT", "")
PIPELINE_INSTANCE_CONTEXT = getattr(settings, "PIPELINE_INSTANCE_CONTEXT", "")

PIPELINE_ENGINE_ADAPTER_API = getattr(
    settings, "PIPELINE_ENGINE_ADAPTER_API", "pipeline.service.pipeline_engine_adapter.adapter_api",
)

PIPELINE_DATA_BACKEND = getattr(
    settings, "PIPELINE_DATA_BACKEND", "pipeline.engine.core.data.mysql_backend.MySQLDataBackend",
)
PIPELINE_DATA_CANDIDATE_BACKEND = getattr(settings, "PIPELINE_DATA_CANDIDATE_BACKEND", None)
PIPELINE_DATA_BACKEND_AUTO_EXPIRE = getattr(settings, "PIPELINE_DATA_BACKEND_AUTO_EXPIRE", False)
PIPELINE_DATA_BACKEND_AUTO_EXPIRE_SECONDS = int(
    getattr(settings, "PIPELINE_DATA_BACKEND_AUTO_EXPIRE_SECONDS", 60 * 60 * 24)
)

PIPELINE_END_HANDLER = getattr(
    settings, "PIPELINE_END_HANDLER", "pipeline.engine.signals.handlers.pipeline_end_handler",
)
PIPELINE_WORKER_STATUS_CACHE_EXPIRES = getattr(settings, "PIPELINE_WORKER_STATUS_CACHE_EXPIRES", 30)
PIPELINE_RERUN_MAX_TIMES = getattr(settings, "PIPELINE_RERUN_MAX_TIMES", 0)
PIPELINE_RERUN_INDEX_OFFSET = getattr(settings, "PIPELINE_RERUN_INDEX_OFFSET", -1)

COMPONENT_AUTO_DISCOVER_PATH = [
    "components.collections",
]

COMPONENT_AUTO_DISCOVER_PATH += getattr(settings, "COMPONENT_PATH", [])

AUTO_UPDATE_COMPONENT_MODELS = getattr(settings, "AUTO_UPDATE_COMPONENT_MODELS", True)

VARIABLE_AUTO_DISCOVER_PATH = [
    "variables.collections",
]

VARIABLE_AUTO_DISCOVER_PATH += getattr(settings, "VARIABLE_PATH", [])

AUTO_UPDATE_VARIABLE_MODELS = getattr(settings, "AUTO_UPDATE_VARIABLE_MODELS", True)

PIPELINE_PARSER_CLASS = getattr(settings, "PIPELINE_PARSER_CLASS", "pipeline.parser.pipeline_parser.PipelineParser")

ENABLE_EXAMPLE_COMPONENTS = getattr(settings, "ENABLE_EXAMPLE_COMPONENTS", True)

UUID_DIGIT_STARTS_SENSITIVE = getattr(settings, "UUID_DIGIT_STARTS_SENSITIVE", False)

PIPELINE_LOG_LEVEL = getattr(settings, "PIPELINE_LOG_LEVEL", "INFO")

# 远程插件包源默认配置
EXTERNAL_PLUGINS_SOURCE_PROXY = getattr(settings, "EXTERNAL_PLUGINS_SOURCE_PROXY", None)
EXTERNAL_PLUGINS_SOURCE_SECURE_RESTRICT = getattr(settings, "EXTERNAL_PLUGINS_SOURCE_SECURE_RESTRICT", True)

# 僵尸进程扫描配置
ENGINE_ZOMBIE_PROCESS_DOCTORS = getattr(settings, "ENGINE_ZOMBIE_PROCESS_DOCTORS", None)
ENGINE_ZOMBIE_PROCESS_HEAL_CRON = getattr(settings, "ENGINE_ZOMBIE_PROCESS_HEAL_CRON", {"minute": "*/10"})

# 过期任务运行时清理配置
EXPIRED_TASK_CLEAN = getattr(settings, "EXPIRED_TASK_CLEAN", False)
EXPIRED_TASK_CLEAN_CRON = getattr(settings, "EXPIRED_TASK_CLEAN_CRON", {"minute": "37", "hour": "*"})
EXPIRED_TASK_CLEAN_NUM_LIMIT = getattr(settings, "EXPIRED_TASK_CLEAN_NUM_LIMIT", 100)
TASK_EXPIRED_MONTH = getattr(settings, "TASK_EXPIRED_MONTH", 6)

# MAKO sandbox config
MAKO_SANDBOX_SHIELD_WORDS = getattr(settings, "MAKO_SANDBOX_SHIELD_WORDS", [])
MAKO_SANDBOX_IMPORT_MODULES = getattr(settings, "MAKO_SANDBOX_IMPORT_MODULES", {})
MAKO_SAFETY_CHECK = getattr(settings, "MAKO_SAFETY_CHECK", True)

# 开发者自定义插件和变量异常类
PLUGIN_SPECIFIC_EXCEPTIONS = getattr(settings, "PLUGIN_SPECIFIC_EXCEPTIONS", ())
VARIABLE_SPECIFIC_EXCEPTIONS = getattr(settings, "VARIABLE_SPECIFIC_EXCEPTIONS", ())
