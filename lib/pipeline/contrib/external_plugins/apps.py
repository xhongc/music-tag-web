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
import traceback

from django.apps import AppConfig
from django.conf import settings
from django.db.utils import ProgrammingError

from pipeline.utils import env

logger = logging.getLogger("root")

DJANGO_MANAGE_CMD = "manage.py"
DEFAULT_TRIGGERS = {"runserver", "celery", "worker", "uwsgi", "shell", "update_component_models"}


class ExternalPluginsConfig(AppConfig):
    name = "pipeline.contrib.external_plugins"
    label = "pipeline_external_plugins"
    verbose_name = "PipelineExternalPlugins"

    def ready(self):
        from pipeline.contrib.external_plugins import loader  # noqa
        from pipeline.contrib.external_plugins.models import ExternalPackageSource  # noqa

        # load external components when start command in trigger list
        if self.should_load_external_module():
            try:
                logger.info("Start to update package source from config file...")
                ExternalPackageSource.update_package_source_from_config(
                    getattr(settings, "COMPONENTS_PACKAGE_SOURCES", {})
                )
            except ProgrammingError:
                logger.warning(
                    "update package source failed, maybe first migration? "
                    "exception: {traceback}".format(traceback=traceback.format_exc())
                )
                # first migrate
                return

            logger.info("Start to load external modules...")

            loader.load_external_modules()

    @staticmethod
    def should_load_external_module():
        django_command = env.get_django_command()
        if django_command is None:
            print("app is not start with django manage command, current argv: {argv}".format(argv=sys.argv))
            return True

        triggers = getattr(settings, "EXTERNAL_COMPONENTS_LOAD_TRIGGER", DEFAULT_TRIGGERS)
        print("should_load_external_module: {}".format(django_command in triggers))
        return django_command in triggers
