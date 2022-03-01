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

from django.core.exceptions import AppRegistryNotReady

from pipeline.engine.core import context


class EngineLogHandler(logging.Handler):
    def emit(self, record):
        try:
            from . import models
        except AppRegistryNotReady:
            return

        models.LogEntry.objects.create(
            logger_name=record.name,
            level_name=record.levelname,
            message=self.format(record),
            exception=record.exc_text,
            node_id=record._id,
        )


class EngineContextLogHandler(logging.Handler):
    def emit(self, record):
        try:
            from . import models
        except AppRegistryNotReady:
            return

        node_id = context.get_node_id()
        if not node_id:
            return

        models.LogEntry.objects.create(
            logger_name=record.name,
            level_name=record.levelname,
            message=self.format(record),
            exception=record.exc_text,
            node_id=node_id,
        )
