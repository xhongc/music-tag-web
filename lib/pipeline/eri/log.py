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
from logging import LogRecord, LoggerAdapter

from django.core.exceptions import AppRegistryNotReady
from bamboo_engine import local

logger = logging.getLogger("pipeline.eri.log")


def get_logger(node_id: str, loop: int, version: str):
    return LoggerAdapter(logger=logger, extra={"node_id": node_id, "loop": loop, "version": version})


class ERINodeLogHandler(logging.Handler):
    def emit(self, record: LogRecord):
        from pipeline.eri.models import LogEntry

        LogEntry.objects.create(
            node_id=record.node_id,
            loop=record.loop,
            version=record.version,
            logger_name=record.name,
            level_name=record.levelname,
            message=self.format(record),
        )


class EngineContextLogHandler(logging.Handler):
    def emit(self, record):
        try:
            from pipeline.eri.models import LogEntry
        except AppRegistryNotReady:
            return

        node_info = local.get_node_info()
        if not node_info:
            return

        LogEntry.objects.create(
            node_id=node_info.node_id,
            version=node_info.version,
            loop=node_info.loop,
            logger_name=record.name,
            level_name=record.levelname,
            message=self.format(record),
        )
