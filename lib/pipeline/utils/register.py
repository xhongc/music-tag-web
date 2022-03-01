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
import pkgutil
import os
import sys
from importlib import import_module


logger = logging.getLogger("root")


def find_all_modules(module_dir, sub_dir=None):
    modules = []
    for _, name, is_pkg in pkgutil.iter_modules([module_dir]):
        if name.startswith("_"):
            continue
        module = name if sub_dir is None else "{}.{}".format(sub_dir, name)
        if is_pkg:
            modules += find_all_modules(os.path.join(module_dir, name), module)
        else:
            modules.append(module)
    return modules


def autodiscover_items(module):
    """
    Given a path to discover, auto register all items
    """
    # Workaround for a Python 3.2 bug with pkgutil.iter_modules
    module_dir = module.__path__[0]
    sys.path_importer_cache.pop(module_dir, None)
    modules = find_all_modules(module_dir)
    for name in modules:
        module_path = "{}.{}".format(module.__name__, name)
        try:
            __import__(module_path)
        except Exception as e:
            logger.error(f"[!] module({module_path}) import failed with err: {e}")


def autodiscover_collections(path):
    """
    Auto-discover INSTALLED_APPS modules and fail silently when
    not present. This forces an import on them to register any admin bits they
    may want.
    """
    from django.apps import apps

    for app_config in apps.get_app_configs():
        # Attempt to import the app's module.
        try:

            _module = import_module("%s.%s" % (app_config.name, path))
            autodiscover_items(_module)
        except ImportError as e:
            if not str(e) == "No module named %s" % path:
                pass
