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

from django.utils import timezone


class Stack(list):
    def top(self):
        return self[len(self) - 1]

    def push(self, item):
        self.append(item)


class ConstantDict(dict):
    """ConstantDict is a subclass of :class:`dict`, implementing __setitem__
    method to avoid item assignment::

    >>> d = ConstantDict({'key': 'value'})
    >>> d['key'] = 'value'
    Traceback (most recent call last):
        ...
    TypeError: 'ConstantDict' object does not support item assignment
    """

    def __setitem__(self, key, value):
        raise TypeError("'%s' object does not support item assignment" % self.__class__.__name__)


def calculate_elapsed_time(started_time, archived_time):
    """
    @summary: 计算节点耗时
    @param started_time: 执行开始时间
    @param archived_time: 执行结束时间
    @return:
    """
    if archived_time and started_time:
        elapsed_time = (archived_time - started_time).total_seconds()
    elif started_time:
        elapsed_time = (timezone.now() - started_time).total_seconds()
    else:
        elapsed_time = 0
    return round(elapsed_time)


class ActionResult(object):
    def __init__(self, result, message, extra=None):
        self.result = result
        self.message = message
        self.extra = extra
