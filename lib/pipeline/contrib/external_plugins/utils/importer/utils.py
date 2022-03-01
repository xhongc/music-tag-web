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
from contextlib import contextmanager

logger = logging.getLogger("root")


@contextmanager
def importer_context(importer):
    _setup_importer(importer)
    try:
        yield
    except Exception as e:
        raise e
    finally:
        _remove_importer(importer)


def _setup_importer(importer):
    logger.info("========== setup importer: %s" % importer)
    sys.meta_path.insert(0, importer)


def _remove_importer(importer):
    for hooked_importer in sys.meta_path:
        if hooked_importer is importer:
            logger.info("========== remove importer: %s" % importer)
            sys.meta_path.remove(hooked_importer)
            return
