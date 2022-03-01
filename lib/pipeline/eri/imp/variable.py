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

import inspect
from typing import Any, Type

from bamboo_engine.eri import Variable as VariableInterface
from pipeline.core.data.var import Variable


class VariableProxy:
    def __init__(self, original_value: Variable, var_cls: Type, pipeline_data: dict):
        self.get_value = getattr(var_cls, "get_value")
        self.original_value = original_value
        self.pipeline_data = pipeline_data
        for name, value in inspect.getmembers(var_cls):
            if not name.startswith("__") and not hasattr(self, name) and inspect.isfunction(value):
                setattr(self, name, value)

    def get(self) -> Any:
        self.value = self.original_value.get()
        return self.get_value(self)


class VariableWrapper(VariableInterface):
    def __init__(self, original_value: Variable, var_cls: Type, additional_data: dict):
        self.var = VariableProxy(original_value=original_value, var_cls=var_cls, pipeline_data=additional_data)

    def get(self) -> Any:
        return self.var.get()
