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

from abc import abstractmethod


class FlowElementHandler(object):
    class HandleResult(object):
        def __init__(self, next_node, should_return, should_sleep, after_sleep_call=None, args=[], kwargs={}):
            self.next_node = next_node
            self.should_return = should_return
            self.should_sleep = should_sleep
            self.after_sleep_call = after_sleep_call
            self.args = args
            self.kwargs = kwargs

    @staticmethod
    @abstractmethod
    def element_cls():
        raise NotImplementedError()

    @abstractmethod
    def handle(self, process, element, status):
        raise NotImplementedError()

    def __call__(self, *args, **kwargs):
        return self.handle(*args, **kwargs)
