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
from abc import abstractmethod
from copy import deepcopy

from django.db import IntegrityError, models
from django.utils.translation import ugettext_lazy as _

from pipeline.component_framework.library import ComponentLibrary
from pipeline.contrib.external_plugins import exceptions
from pipeline.contrib.external_plugins.models.fields import JSONTextField

GIT = "git"
S3 = "s3"
FILE_SYSTEM = "fs"
logger = logging.getLogger("root")
source_cls_factory = {}


def package_source(cls):
    source_cls_factory[cls.type()] = cls
    return cls


class SourceManager(models.Manager):
    def create_source(self, name, packages, from_config, **kwargs):
        create_kwargs = deepcopy(kwargs)
        create_kwargs.update({"name": name, "packages": packages, "from_config": from_config})
        return self.create(**create_kwargs)

    def remove_source(self, source_id):
        source = self.get(id=source_id)

        if source.from_config:
            raise exceptions.InvalidOperationException("Can not remove source create from config")

        source.delete()

    def update_source_from_config(self, configs):

        sources_from_config = self.filter(from_config=True).all()
        existing_source_names = {source.name for source in sources_from_config}
        source_name_in_config = {config["name"] for config in configs}

        invalid_source_names = existing_source_names - source_name_in_config

        # remove invalid source
        self.filter(name__in=invalid_source_names).delete()

        # update and create source
        for config in configs:
            defaults = deepcopy(config["details"])
            defaults["packages"] = config["packages"]

            try:
                self.update_or_create(name=config["name"], from_config=True, defaults=defaults)
            except IntegrityError:
                raise exceptions.InvalidOperationException(
                    'There is a external source named "{source_name}" but not create from config, '
                    "can not do source update operation".format(source_name=config["name"])
                )


class ExternalPackageSource(models.Model):
    name = models.CharField(_("包源名"), max_length=128, unique=True)
    from_config = models.BooleanField(_("是否是从配置文件中读取的"), default=False)
    packages = JSONTextField(_("模块配置"))

    objects = SourceManager()

    class Meta:
        abstract = True

    @staticmethod
    @abstractmethod
    def type():
        raise NotImplementedError()

    @abstractmethod
    def importer(self):
        raise NotImplementedError()

    @abstractmethod
    def details(self):
        raise NotImplementedError()

    @property
    def imported_plugins(self):
        plugins = []
        try:
            importer = self.importer()
        except ValueError as e:
            logger.exception("ExternalPackageSource[name={}] call importer error: {}".format(self.name, e))
            return plugins
        for component in ComponentLibrary.component_list():
            component_importer = getattr(sys.modules[component.__module__], "__loader__", None)
            if isinstance(component_importer, type(importer)) and component_importer.name == self.name:
                plugins.append(
                    {
                        "code": component.code,
                        "name": component.name,
                        "group_name": component.group_name,
                        "class_name": component.__name__,
                        "module": component.__module__,
                    }
                )
        return plugins

    @property
    def modules(self):
        modules = []

        for package_info in list(self.packages.values()):
            modules.extend(package_info["modules"])

        return modules

    @staticmethod
    def update_package_source_from_config(source_configs):
        classified_config = {source_type: [] for source_type in list(source_cls_factory.keys())}

        for config in deepcopy(source_configs):
            classified_config.setdefault(config.pop("type"), []).append(config)

        for source_type, configs in list(classified_config.items()):
            try:
                source_model_cls = source_cls_factory[source_type]
            except KeyError:
                raise KeyError("Unsupported external source type: %s" % source_type)
            source_model_cls.objects.update_source_from_config(configs=configs)

    @staticmethod
    def package_source_types():
        return list(source_cls_factory.keys())
