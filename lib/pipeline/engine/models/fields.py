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

import pickle
import traceback
import zlib

from django.db import models

from pipeline.utils.utils import convert_bytes_to_str
from . import nr_pickle


class IOField(models.BinaryField):
    def __init__(self, compress_level=6, *args, **kwargs):
        super(IOField, self).__init__(*args, **kwargs)
        self.compress_level = compress_level

    def get_prep_value(self, value):
        value = super(IOField, self).get_prep_value(value)
        try:
            serialized = zlib.compress(pickle.dumps(value), self.compress_level)
        except RecursionError:
            serialized = zlib.compress(nr_pickle.dumps(value), self.compress_level)
        return serialized

    def to_python(self, value):
        try:
            value = super(IOField, self).to_python(value)
            return pickle.loads(zlib.decompress(value))
        except UnicodeDecodeError:
            # py2 pickle data process
            return convert_bytes_to_str(pickle.loads(zlib.decompress(value), encoding="bytes"))
        except Exception:
            return "IOField to_python raise error: {}".format(traceback.format_exc())

    def from_db_value(self, value, expression, connection, context=None):
        return self.to_python(value)
