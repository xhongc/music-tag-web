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

import importlib
import logging
import traceback

from pipeline.contrib.external_plugins.models import source_cls_factory
from pipeline.contrib.external_plugins.utils.importer import importer_context

logger = logging.getLogger("root")


def load_external_modules():
    for source_type, source_model_cls in list(source_cls_factory.items()):
        # get all external source
        sources = source_model_cls.objects.all()

        # get importer for source
        for source in sources:
            _import_modules_in_source(source)


def _import_modules_in_source(source):
    try:
        importer = source.importer()

        with importer_context(importer):
            for mod in source.modules:
                importlib.import_module(mod)
    except Exception:
        logger.error("An error occurred when loading {{{}}}: {}".format(source.name, traceback.format_exc()))
