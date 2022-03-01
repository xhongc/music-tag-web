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

from pipeline.core.data.library import VariableLibrary


class VariableModel(models.Model):
    """
    注册的变量
    """

    code = models.CharField(_("变量编码"), max_length=255, unique=True)
    status = models.BooleanField(_("变量是否可用"), default=True)

    class Meta:
        verbose_name = _("Variable变量")
        verbose_name_plural = _("Variable变量")

    def __unicode__(self):
        return self.code

    def get_class(self):
        return VariableLibrary.get_var_class(self.code)

    @property
    def name(self):
        return self.get_class().name

    @property
    def form(self):
        return self.get_class().form

    @property
    def type(self):
        return self.get_class().type

    @property
    def tag(self):
        return self.get_class().tag

    @property
    def meta_tag(self):
        return getattr(self.get_class(), "meta_tag")
