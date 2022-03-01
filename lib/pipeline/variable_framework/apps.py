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

import logging

from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError

from pipeline.conf import settings
from pipeline.utils.register import autodiscover_collections
from pipeline.variable_framework import context

logger = logging.getLogger("root")


class VariableFrameworkConfig(AppConfig):
    name = "pipeline.variable_framework"
    verbose_name = "PipelineVariableFramework"

    def ready(self):
        """
        @summary: 注册公共部分和RUN_VER下的变量到数据库
        @return:
        """
        from pipeline.variable_framework.signals.handlers import pre_variable_register_handler  # noqa

        for path in settings.VARIABLE_AUTO_DISCOVER_PATH:
            autodiscover_collections(path)

        if context.skip_update_var_models():
            return

        from pipeline.variable_framework.models import VariableModel
        from pipeline.core.data.library import VariableLibrary

        try:
            print("update variable models")
            VariableModel.objects.exclude(code__in=list(VariableLibrary.variables.keys())).update(status=False)
            print("update variable models finish")
        except (ProgrammingError, OperationalError) as e:
            # first migrate
            logger.exception(e)
