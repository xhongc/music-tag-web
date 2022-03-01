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

from pipeline.component_framework.constants import LEGACY_PLUGINS_VERSION
from pipeline.component_framework.library import ComponentLibrary


class ComponentManager(models.Manager):
    def get_component_dict(self):
        """
        获得标准插件对应的dict类型
        :return:
        """
        components = self.filter(status=True)
        component_dict = {}
        for bundle in components:
            name = bundle.name.split("-")
            group_name = _(name[0])
            name = _(name[1])
            component_dict[bundle.code] = "{}-{}".format(group_name, name)
        return component_dict

    def get_component_dicts(self, other_component_list):
        """
        :param other_component_list: 结果集
        :param index: 结果集中指标字段
        :return:
        """
        components = self.filter(status=True).values("code", "version", "name")
        total = components.count()
        groups = []
        for comp in components:
            version = comp["version"]
            # 插件名国际化
            name = comp["name"].split("-")
            name = "{}-{}-{}".format(_(name[0]), _(name[1]), version)
            code = "{}-{}".format(comp["code"], comp["version"])
            value = 0
            for oth_com_tmp in other_component_list:
                if comp["code"] == oth_com_tmp[1] and comp["version"] == oth_com_tmp[2]:
                    value = oth_com_tmp[0]
            groups.append({"code": code, "name": name, "value": value})
        return total, groups


class ComponentModel(models.Model):
    """
    注册的组件
    """

    code = models.CharField(_("组件编码"), max_length=255, db_index=True)
    version = models.CharField(_("组件版本"), max_length=64, default=LEGACY_PLUGINS_VERSION, db_index=True)
    name = models.CharField(_("组件名称"), max_length=255)
    status = models.BooleanField(_("组件是否可用"), default=True)

    objects = ComponentManager()

    class Meta:
        verbose_name = _("组件 Component")
        verbose_name_plural = _("组件 Component")
        ordering = ["-id"]
        unique_together = (("code", "version"),)

    def __unicode__(self):
        return self.name

    @property
    def group_name(self):
        return ComponentLibrary.get_component_class(self.code, self.version).group_name

    @property
    def group_icon(self):
        return ComponentLibrary.get_component_class(self.code, self.version).group_icon
