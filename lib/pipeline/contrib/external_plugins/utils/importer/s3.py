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

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from pipeline.contrib.external_plugins.utils.importer.base import AutoInstallRequirementsImporter

logger = logging.getLogger("root")
CONFIG = Config(connect_timeout=10, read_timeout=10, retries={"max_attempts": 2})


class S3ModuleImporter(AutoInstallRequirementsImporter):
    def __init__(
        self,
        name,
        modules,
        service_address,
        bucket,
        access_key,
        secret_key,
        use_cache=True,
        secure_only=True,
        source_dir="",
    ):
        super(S3ModuleImporter, self).__init__(name=name, modules=modules)

        if secure_only and not service_address.startswith("https"):
            raise ValueError("Only accept https when secure_only is True.")
        elif not secure_only:
            logger.warning("Using not secure protocol is extremely dangerous!!")

        self.service_address = service_address if service_address.endswith("/") else "%s/" % service_address
        self.bucket = bucket
        self.source_dir = source_dir if source_dir == "" or source_dir.endswith("/") else "%s/" % source_dir
        self.use_cache = use_cache
        self.s3 = boto3.resource(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url=self.service_address,
            config=CONFIG,
        )
        self.obj_cache = {}

    def is_package(self, fullname):
        return self._fetch_obj_content(self._obj_key(fullname, is_pkg=True)) is not None

    def get_code(self, fullname):
        return compile(self.get_source(fullname), self.get_file(fullname), "exec")

    def get_source(self, fullname):
        source_code = self._fetch_obj_content(self._obj_key(fullname, is_pkg=self.is_package(fullname)))

        if source_code is None:
            raise ImportError(
                "Can not find {module} in {service_address}{bucket}/{source_dir}".format(
                    module=fullname,
                    service_address=self.service_address,
                    bucket=self.bucket,
                    source_dir=self.source_dir,
                )
            )

        return source_code

    def get_path(self, fullname):
        return [self.get_file(fullname).rpartition("/")[0]]

    def get_file(self, fullname):
        return "{service_address}{bucket}/{key}".format(
            service_address=self.service_address,
            bucket=self.bucket,
            key=self._obj_key(fullname, is_pkg=self.is_package(fullname)),
        )

    def _obj_key(self, fullname, is_pkg):
        base_key = self.source_dir + fullname.replace(".", "/")
        key = "%s/__init__.py" % base_key if is_pkg else "%s.py" % base_key
        return key

    def _fetch_obj_content(self, key):
        logger.info("Try to fetch object: {key}".format(key=key))

        if self.use_cache and key in self.obj_cache:
            logger.info("Use content in cache for s3 object: {key}".format(key=key))
            return self.obj_cache[key]

        obj_content = self._get_s3_obj_content(key)

        if self.use_cache:
            self.obj_cache[key] = obj_content

        return obj_content

    def _get_s3_obj_content(self, key):
        obj = self.s3.Object(bucket_name=self.bucket, key=key)

        try:
            resp = obj.get()
            obj_content = resp["Body"].read()
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                obj_content = None
            else:
                raise

        return obj_content
