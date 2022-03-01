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


class ComponentInTemplate(models.Model):
    component_code = models.CharField(_("组件编码"), max_length=255)
    template_id = models.CharField(_("模板ID"), max_length=32)
    node_id = models.CharField(_("节点ID"), max_length=32)
    is_sub = models.BooleanField(_("是否子流程引用"), default=False)
    subprocess_stack = models.TextField(_("子流程堆栈"), default="[]", help_text=_("JSON 格式的列表"))
    version = models.CharField(_("插件版本"), max_length=255, default="legacy")

    class Meta:
        verbose_name = _("Pipeline标准插件被引用数据")
        verbose_name_plural = _("Pipeline标准插件被引用数据")

    def __unicode__(self):
        return "{}_{}".format(self.component_code, self.template_id)


class ComponentExecuteData(models.Model):
    component_code = models.CharField(_("组件编码"), max_length=255, db_index=True)
    instance_id = models.CharField(_("实例ID"), max_length=32, db_index=True)
    node_id = models.CharField(_("节点ID"), max_length=32)
    is_sub = models.BooleanField(_("是否子流程引用"), default=False)
    subprocess_stack = models.TextField(_("子流程堆栈"), default="[]", help_text=_("JSON 格式的列表"))
    started_time = models.DateTimeField(_("标准插件执行开始时间"))
    archived_time = models.DateTimeField(_("标准插件执行结束时间"), null=True, blank=True)
    elapsed_time = models.IntegerField(_("标准插件执行耗时(s)"), null=True, blank=True)
    status = models.BooleanField(_("是否执行成功"), default=False)
    is_skip = models.BooleanField(_("是否跳过"), default=False)
    is_retry = models.BooleanField(_("是否重试记录"), default=False)
    version = models.CharField(_("插件版本"), max_length=255, default="legacy")

    class Meta:
        verbose_name = _("Pipeline标准插件执行数据")
        verbose_name_plural = _("Pipeline标准插件执行数据")
        ordering = ["-id"]

    def __unicode__(self):
        return "{}_{}".format(self.component_code, self.instance_id)


class TemplateInPipeline(models.Model):
    template_id = models.CharField(_("模板ID"), max_length=255, db_index=True)
    atom_total = models.IntegerField(_("标准插件总数"))
    subprocess_total = models.IntegerField(_("子流程总数"))
    gateways_total = models.IntegerField(_("网关总数"))

    class Meta:
        verbose_name = _("Pipeline模板引用数据")
        verbose_name_plural = _("Pipeline模板引用数据")

    def __unicode__(self):
        return "{}_{}_{}_{}".format(self.template_id, self.atom_total, self.subprocess_total, self.gateways_total)


class InstanceInPipeline(models.Model):
    instance_id = models.CharField(_("实例ID"), max_length=255, db_index=True)
    atom_total = models.IntegerField(_("标准插件总数"))
    subprocess_total = models.IntegerField(_("子流程总数"))
    gateways_total = models.IntegerField(_("网关总数"))

    class Meta:
        verbose_name = _("Pipeline实例引用数据")
        verbose_name_plural = _("Pipeline实例引用数据")

    def __unicode__(self):
        return "{}_{}_{}_{}".format(self.instance_id, self.atom_total, self.subprocess_total, self.gateways_total)
