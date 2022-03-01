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


def setup(level=None):
    from pipeline.logging import pipeline_logger as logger
    from pipeline.log.handlers import EngineLogHandler

    if level in set(logging._levelToName.values()):
        logger.setLevel(level)

    logging._acquireLock()
    try:
        for hdl in logger.handlers:
            if isinstance(hdl, EngineLogHandler):
                break
        else:
            hdl = EngineLogHandler()
            hdl.setLevel(logger.level)
            logger.addHandler(hdl)
    finally:
        logging._releaseLock()


default_app_config = "pipeline.log.apps.LogConfig"
