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

import zlib
import pickle

from django.db import models
from django.utils.translation import ugettext_lazy as _


class IOField(models.BinaryField):
    def __init__(self, compress_level=6, *args, **kwargs):
        super(IOField, self).__init__(*args, **kwargs)
        self.compress_level = compress_level

    def get_prep_value(self, value):
        value = super(IOField, self).get_prep_value(value)
        return zlib.compress(pickle.dumps(value), self.compress_level)

    def to_python(self, value):
        value = super(IOField, self).to_python(value)
        return pickle.loads(zlib.decompress(value))

    def from_db_value(self, value, expression, connection, context=None):
        return self.to_python(value)


class SignalManager(models.Manager):
    def dump(self, module_path, signal_name, kwargs):
        self.create(module_path=module_path, name=signal_name, kwargs=kwargs)


class Signal(models.Model):
    module_path = models.TextField(_("信号模块名"))
    name = models.CharField(_("信号属性名"), max_length=64)
    kwargs = IOField(verbose_name=_("信号参数"))

    objects = SignalManager()
