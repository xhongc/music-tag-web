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

from bamboo_engine.eri import Service, ExecutableEvent, Variable

from pipeline.component_framework.library import ComponentLibrary
from pipeline.core.flow import FlowNodeClsFactory
from pipeline.core.data.library import VariableLibrary

from pipeline.eri.imp.service import ServiceWrapper
from pipeline.eri.imp.executable_event import ExecutableEndEventWrapper
from pipeline.eri.imp.variable import VariableWrapper


class PipelinePluginManagerMixin:
    def get_service(self, code: str, version: str) -> Service:
        """
        根据代号与版本获取特定服务对象实例

        :param code: 服务唯一代号
        :type code: str
        :param version: 服务版本
        :type version: str
        :return: 服务对象实例
        :rtype: Service
        """
        comp_cls = ComponentLibrary.get_component_class(code, version)
        service = comp_cls.bound_service()
        return ServiceWrapper(service)

    def get_executable_end_event(self, code: str) -> ExecutableEvent:
        """
        根据代号获取特定可执行结束事件实例

        :param code: 可执行结束事件唯一代号
        :type code: str
        :return: 可执行结束事件实例
        :rtype: ExecutableEvent:
        """
        event_cls = FlowNodeClsFactory.get_node_cls(code)
        event = event_cls(id=None)
        return ExecutableEndEventWrapper(event)

    def get_compute_variable(self, code: str, key: str, value: Variable, additional_data: dict) -> Variable:
        """
        根据代号获取变量实例

        :param code: 唯一代号
        :type code: str
        :param key: 变量 key
        :type key: str
        :param value: 变量配置
        :type value: Any
        :param additional_data: 额外数据字典
        :type additional_data: dict
        :return: 变量实例
        :rtype: Variable
        """
        var_cls = VariableLibrary.get_var_class(code=code)
        return VariableWrapper(original_value=value, var_cls=var_cls, additional_data=additional_data)
