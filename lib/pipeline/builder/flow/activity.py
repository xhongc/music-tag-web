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

from pipeline.builder.flow.base import *  # noqa
from pipeline.utils.collections import FancyDict

__all__ = ["ServiceActivity", "SubProcess"]


class ServiceActivity(Element):
    def __init__(
        self,
        component_code=None,
        failure_handler=None,
        error_ignorable=False,
        timeout=None,
        skippable=True,
        retryable=True,
        *args,
        **kwargs
    ):
        self.component = FancyDict({"code": component_code, "inputs": FancyDict({})})
        self.failure_handler = (
            "{module}.{name}".format(module=failure_handler.__module__, name=failure_handler.__name__)
            if failure_handler
            else None
        )
        self.error_ignorable = error_ignorable
        self.timeout = timeout
        self.skippable = skippable
        self.retryable = retryable
        super(ServiceActivity, self).__init__(*args, **kwargs)

    def type(self):
        return PE.ServiceActivity

    def component_dict(self):
        return {
            "code": self.component.code,
            "inputs": {key: var.to_dict() for key, var in list(self.component.inputs.items())},
        }


class SubProcess(Element):
    def __init__(
        self,
        start=None,
        data=None,
        params=None,
        global_outputs=None,
        replace_id=False,
        template_id=None,
        *args,
        **kwargs
    ):
        self.start = start
        self.data = data
        self.params = params or {}
        self.replace_id = replace_id
        self.global_outputs = FancyDict(global_outputs or {})
        self.template_id = template_id
        super(SubProcess, self).__init__(*args, **kwargs)

    def type(self):
        return PE.SubProcess
