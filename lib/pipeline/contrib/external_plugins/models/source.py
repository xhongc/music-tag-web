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

from django.db import models
from django.utils.translation import ugettext_lazy as _

from pipeline.conf import settings
from pipeline.contrib.external_plugins.models.base import FILE_SYSTEM, GIT, S3, ExternalPackageSource, package_source
from pipeline.contrib.external_plugins.utils.importer import FSModuleImporter, GitRepoModuleImporter, S3ModuleImporter


@package_source
class GitRepoSource(ExternalPackageSource):
    repo_raw_address = models.TextField(_("文件托管仓库链接"))
    branch = models.CharField(_("分支名"), max_length=128)

    @staticmethod
    def type():
        return GIT

    def importer(self):
        return GitRepoModuleImporter(
            name=self.name,
            repo_raw_url=self.repo_raw_address,
            branch=self.branch,
            modules=list(self.packages.keys()),
            proxy=settings.EXTERNAL_PLUGINS_SOURCE_PROXY,
            secure_only=settings.EXTERNAL_PLUGINS_SOURCE_SECURE_RESTRICT,
        )

    def details(self):
        return {"repo_raw_address": self.repo_raw_address, "branch": self.branch}


@package_source
class S3Source(ExternalPackageSource):
    service_address = models.TextField(_("对象存储服务地址"))
    bucket = models.TextField(_("bucket 名"))
    source_dir = models.TextField(_("源目录名"), default="")
    access_key = models.TextField(_("access key"))
    secret_key = models.TextField(_("secret key"))

    @staticmethod
    def type():
        return S3

    def importer(self):
        return S3ModuleImporter(
            name=self.name,
            modules=list(self.packages.keys()),
            service_address=self.service_address,
            bucket=self.bucket,
            source_dir=self.source_dir,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure_only=settings.EXTERNAL_PLUGINS_SOURCE_SECURE_RESTRICT,
        )

    def details(self):
        return {
            "service_address": self.service_address,
            "bucket": self.bucket,
            "source_dir": self.source_dir,
            "access_key": self.access_key,
            "secret_key": self.secret_key,
        }


@package_source
class FileSystemSource(ExternalPackageSource):
    path = models.TextField(_("文件系统路径"))

    @staticmethod
    def type():
        return FILE_SYSTEM

    def importer(self):
        return FSModuleImporter(name=self.name, modules=list(self.packages.keys()), path=self.path)

    def details(self):
        return {"path": self.path}
