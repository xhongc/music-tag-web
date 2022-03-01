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


# 流程上下文相关逻辑封装模块


import logging
from weakref import WeakValueDictionary
from typing import List, Dict, Any

from bamboo_engine.eri import (
    ContextValue,
    EngineRuntimeInterface,
    Variable,
    ContextValueType,
)
from .template.template import Template
from .utils.string import deformat_var_key

logger = logging.getLogger("bamboo_engine")


class PlainVariable(Variable):
    """
    普通变量
    """

    def __init__(self, key: str, value: Any):
        self.key = key
        self.value = value

    def get(self):
        return self.value


class SpliceVariable(Variable):
    """
    模板类型变量，会尝试在流程上下文中解析变量中定义的模板
    """

    def __init__(self, key: str, value: Any, pool: WeakValueDictionary):
        self.key = key
        self.value = value
        self.pool = pool
        self.refs = [k for k in Template(value).get_reference()]

    def get(self):
        context = {}
        for r in self.refs:
            if r not in self.pool:
                continue

            var = self.pool[r]
            if issubclass(var.__class__, Variable):
                var = var.get()
            context[deformat_var_key(r)] = var

        return Template(self.value).render(context=context)


def _raw_key(key: str) -> str:
    return key


class Context:
    """
    流程执行上下文，封装引擎在执行流程的过程中对上下文进行的操作和逻辑
    """

    def __init__(
        self,
        runtime: EngineRuntimeInterface,
        values: List[ContextValue],
        additional_data: dict,
    ):
        """

        :param runtime: 引擎运行时实例
        :type runtime: EngineRuntimeInterface
        :param values: 上下文数据列表
        :type values: List[ContextValue]
        :param additional_data: 额外数据字典
        :type additional_data: dict
        """
        self.values = values
        self.runtime = runtime
        self.pool = WeakValueDictionary()
        self.variables = {}
        self.additional_data = additional_data

        # 将上下文数据转换成变量，变量内封装了自身解析的逻辑，且实现了 Variable 接口
        for v in self.values:
            if v.type is ContextValueType.PLAIN:
                self.variables[v.key] = PlainVariable(key=v.key, value=v.value)
            elif v.type is ContextValueType.SPLICE:
                self.variables[v.key] = SpliceVariable(key=v.key, value=v.value, pool=self.pool)
            elif v.type is ContextValueType.COMPUTE:
                self.variables[v.key] = self.runtime.get_compute_variable(
                    code=v.code,
                    key=v.key,
                    value=SpliceVariable(key=v.key, value=v.value, pool=self.pool),
                    additional_data=self.additional_data,
                )

        for k, var in self.variables.items():
            self.pool[k] = var

    def hydrate(self, deformat=False, mute_error=False) -> Dict[str, Any]:
        """
        将当前上下文中的数据清洗成 Dict[str, Any] 类型的朴素数据，过程中会进行变量引用的分析和替换

        :param deformat: 是否将返回字典中的 key 值从 ${%s} 替换为 %s
        :type deformat: bool, optional
        :return: 上下文数据朴素值字典
        :rtype: Dict[str, Any]
        """
        key_formatter = deformat_var_key if deformat else _raw_key
        hydrated = {}

        for key, var in self.pool.items():
            try:
                hydrated[key_formatter(key)] = var.get()
            except Exception as e:
                if not mute_error:
                    raise e
                logger.exception("%s get error." % key)
                hydrated[key_formatter(key)] = str(e)

        return hydrated

    def extract_outputs(
        self,
        pipeline_id: str,
        data_outputs: Dict[str, str],
        execution_data_outputs: Dict[str, Any],
    ):
        """
        将某个节点的输出提取到流程上下文中

        :param pipeline_id: 上下文对应的流程/子流程 ID
        :type pipeline_id: str
        :param data_outputs: 节点输出键映射
        :type data_outputs: Dict[str, str]
        :param execution_data_outputs: 节点执行数据输出
        :type execution_data_outputs: Dict[str, Any]
        """
        update = {}
        for origin_key, target_key in data_outputs.items():
            if origin_key not in execution_data_outputs:
                continue

            update[target_key] = ContextValue(
                key=target_key,
                type=ContextValueType.PLAIN,
                value=execution_data_outputs[origin_key],
            )

        self.runtime.upsert_plain_context_values(pipeline_id=pipeline_id, update=update)
