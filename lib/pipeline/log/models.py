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
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class LogEntryManager(models.Manager):
    def link_history(self, node_id, history_id):
        self.filter(node_id=node_id, history_id=-1).update(history_id=history_id)

    def plain_log_for_node(self, node_id, history_id):
        entries = self.order_by("id").filter(node_id=node_id, history_id=history_id)
        plain_entries = []
        for entry in entries:
            plain_entries.append(
                "[%s %s] %s, exception: %s"
                % (entry.logged_at.strftime("%Y-%m-%d %H:%M:%S"), entry.level_name, entry.message, entry.exception)
            )
        return "\n".join(plain_entries)

    def delete_expired_log(self, interval):
        expired_date = timezone.now() + timezone.timedelta(days=(-interval))
        to_be_deleted = self.filter(logged_at__lt=expired_date)
        count = to_be_deleted.count()
        to_be_deleted.delete()
        return count


class LogEntry(models.Model):
    id = models.BigAutoField(_("ID"), primary_key=True)
    logger_name = models.SlugField(_("logger 名称"), max_length=128)
    level_name = models.SlugField(_("日志等级"), max_length=32)
    message = models.TextField(_("日志内容"), null=True)
    exception = models.TextField(_("异常信息"), null=True)
    logged_at = models.DateTimeField(_("输出时间"), auto_now_add=True, db_index=True)

    node_id = models.CharField(_("节点 ID"), max_length=32, db_index=True)
    history_id = models.IntegerField(_("节点执行历史 ID"), default=-1)

    objects = LogEntryManager()
