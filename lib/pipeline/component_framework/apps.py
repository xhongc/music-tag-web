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
import sys

from django.apps import AppConfig
from django.db.utils import InternalError, OperationalError, ProgrammingError

from pipeline.conf import settings
from pipeline.component_framework import context
from pipeline.utils.register import autodiscover_collections

logger = logging.getLogger("root")

DJANGO_MANAGE_CMD = "manage.py"
INIT_PASS_TRIGGER = {"migrate"}


class ComponentFrameworkConfig(AppConfig):
    name = "pipeline.component_framework"
    verbose_name = "PipelineComponentFramework"

    def ready(self):
        """
        @summary: 注册公共部分和当前RUN_VER下的标准插件到数据库
        @return:
        """

        if sys.argv and sys.argv[0] == DJANGO_MANAGE_CMD:
            try:
                command = sys.argv[1]
            except IndexError:
                return
            else:
                if command in INIT_PASS_TRIGGER:
                    print("ignore components init for command: {}".format(sys.argv))
                    return

        for path in settings.COMPONENT_AUTO_DISCOVER_PATH:
            autodiscover_collections(path)

        if context.skip_update_comp_models():
            return

        from pipeline.component_framework.models import ComponentModel
        from pipeline.component_framework.library import ComponentLibrary

        try:
            print("update component models")
            ComponentModel.objects.all().update(status=False)
            for code in ComponentLibrary.codes():
                ComponentModel.objects.filter(code=code, version__in=ComponentLibrary.versions(code)).update(
                    status=True
                )
            print("update component models finish")
        except InternalError:
            # version field migration
            logger.exception("update component model fail")
        except (ProgrammingError, OperationalError):
            # first migrate
            logger.exception("update component model fail")
