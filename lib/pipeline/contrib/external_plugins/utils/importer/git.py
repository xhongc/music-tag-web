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
import urllib.parse

import requests

from pipeline.contrib.external_plugins.utils.importer.base import AutoInstallRequirementsImporter

logger = logging.getLogger("root")


class GitRepoModuleImporter(AutoInstallRequirementsImporter):
    def __init__(self, name, modules, repo_raw_url, branch, use_cache=True, secure_only=True, proxy=None):
        super(GitRepoModuleImporter, self).__init__(name=name, modules=modules)

        if secure_only and not repo_raw_url.startswith("https"):
            raise ValueError("Only accept https when secure_only is True.")
        elif not secure_only:
            logger.warning("Using not secure protocol is extremely dangerous!!")

        self.repo_raw_url = repo_raw_url if repo_raw_url.endswith("/") else "%s/" % repo_raw_url
        self.branch = branch
        self.use_cache = use_cache
        self.file_cache = {}
        self.proxy = proxy or {}

    def is_package(self, fullname):
        return self._fetch_repo_file(self._file_url(fullname, is_pkg=True)) is not None

    def get_code(self, fullname):
        return compile(self.get_source(fullname), self.get_file(fullname), "exec")

    def get_source(self, fullname):
        source_code = self._fetch_repo_file(self._file_url(fullname, is_pkg=self.is_package(fullname)))

        if source_code is None:
            raise ImportError(
                "Can not find {module} in {repo}{branch}".format(
                    module=fullname, repo=self.repo_raw_url, branch=self.branch
                )
            )
        return source_code

    def get_path(self, fullname):
        return [self._file_url(fullname, is_pkg=True).rpartition("/")[0]]

    def get_file(self, fullname):
        return self._file_url(fullname, is_pkg=self.is_package(fullname))

    def _file_url(self, fullname, is_pkg=False):
        base_url = "%s/" % urllib.parse.urljoin(self.repo_raw_url, self.branch)
        path = fullname.replace(".", "/")
        file_name = "%s/__init__.py" % path if is_pkg else "%s.py" % path
        return urllib.parse.urljoin(base_url, file_name)

    def _fetch_repo_file(self, file_url):
        logger.info("Try to fetch git file: {file_url}".format(file_url=file_url))

        if self.use_cache and file_url in self.file_cache:
            logger.info("Use content in cache for git file: {file_url}".format(file_url=file_url))
            return self.file_cache[file_url]

        resp = requests.get(file_url, timeout=10, proxies=self.proxy)

        file_content = resp.content if resp.ok else None

        if self.use_cache:
            self.file_cache[file_url] = file_content
            logger.info("Content cached for git file: {file_url}".format(file_url=file_url))

        return file_content
