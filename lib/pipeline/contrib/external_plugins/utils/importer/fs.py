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
import os
import traceback

from pipeline.contrib.external_plugins.utils.importer.base import AutoInstallRequirementsImporter

logger = logging.getLogger("root")


class FSModuleImporter(AutoInstallRequirementsImporter):
    def __init__(self, name, modules, path, use_cache=True):
        super(FSModuleImporter, self).__init__(name=name, modules=modules)

        self.path = path if path.endswith("/") else "%s/" % path
        self.use_cache = use_cache
        self.file_cache = {}

    def is_package(self, fullname):
        return os.path.exists(self._file_path(fullname, is_pkg=True))

    def get_code(self, fullname):
        return compile(self.get_source(fullname), self.get_file(fullname), "exec")

    def get_source(self, fullname):
        source_code = self._fetch_file_content(self._file_path(fullname, is_pkg=self.is_package(fullname)))

        if source_code is None:
            raise ImportError("Can not find {module} in {path}".format(module=fullname, path=self.path))

        return source_code

    def get_path(self, fullname):
        return [self._file_path(fullname, is_pkg=True).rpartition("/")[0]]

    def get_file(self, fullname):
        return self._file_path(fullname, is_pkg=self.is_package(fullname))

    def _file_path(self, fullname, is_pkg=False):
        base_path = "{path}{file_path}".format(path=self.path, file_path=fullname.replace(".", "/"))
        file_path = "%s/__init__.py" % base_path if is_pkg else "%s.py" % base_path
        return file_path

    def _fetch_file_content(self, file_path):
        logger.info("Try to fetch file {file_path}".format(file_path=file_path))

        if self.use_cache and file_path in self.file_cache:
            logger.info("Use content in cache for file: {file_path}".format(file_path=file_path))
            return self.file_cache[file_path]

        file_content = self._get_file_content(file_path)

        if self.use_cache:
            self.file_cache[file_path] = file_content

        return file_content

    def _get_file_content(self, file_path):
        try:
            with open(file_path) as f:
                file_content = f.read()
        except IOError:
            logger.info(
                "Error occurred when read {file_path} content: {trace}".format(
                    file_path=file_path, trace=traceback.format_exc()
                )
            )
            file_content = None

        return file_content
