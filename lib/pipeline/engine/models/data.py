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

from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _

from pipeline.engine.models.fields import IOField


class DataSnapshotManager(models.Manager):
    def set_object(self, key, obj):
        # do not use update_or_create, prevent of deadlock
        with transaction.atomic():
            if self.get_object(key):
                self.filter(key=key).update(obj=obj)
            else:
                self.create(key=key, obj=obj)
        return True

    def get_object(self, key):
        try:
            return self.get(key=key).obj
        except DataSnapshot.DoesNotExist:
            return None

    def del_object(self, key):
        try:
            self.get(key=key).delete()
            return True
        except DataSnapshot.DoesNotExist:
            return False


class DataSnapshot(models.Model):
    key = models.CharField(_("对象唯一键"), max_length=255, primary_key=True)
    obj = IOField(verbose_name=_("对象存储字段"))

    objects = DataSnapshotManager()
