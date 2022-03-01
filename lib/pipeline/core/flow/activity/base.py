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

from abc import ABCMeta

from pipeline.core.flow.base import FlowNode


def _empty_method(data, parent_data):
    return


class Activity(FlowNode, metaclass=ABCMeta):
    def __init__(self, id, name=None, data=None, failure_handler=None):
        super(Activity, self).__init__(id, name, data)
        self._failure_handler = failure_handler or _empty_method

    def next(self):
        return self.outgoing.unique_one().target

    def failure_handler(self, parent_data):
        return self._failure_handler(data=self.data, parent_data=parent_data)

    def skip(self):
        raise NotImplementedError()

    def prepare_rerun_data(self):
        raise NotImplementedError()
