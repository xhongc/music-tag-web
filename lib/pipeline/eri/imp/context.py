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

import json
from typing import Dict, List, Set

from django.db import transaction

from bamboo_engine import metrics
from bamboo_engine.eri import ContextValue, ContextValueType

from pipeline.eri.models import ContextValue as DBContextValue
from pipeline.eri.models import ContextOutputs
from pipeline.eri.imp.serializer import SerializerMixin


class ContextMixin(SerializerMixin):
    @metrics.setup_histogram(metrics.ENGINE_RUNTIME_CONTEXT_VALUE_READ_TIME)
    def get_context_values(self, pipeline_id: str, keys: set) -> List[ContextValue]:
        """
        获取某个流程上下文中的 keys 所指定的键对应变量的值

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        :param keys: 变量键
        :type keys: set
        :return: 变量值信息
        :rtype: List[ContextValue]
        """
        qs = DBContextValue.objects.filter(pipeline_id=pipeline_id, key__in=keys).only(
            "key", "type", "serializer", "value", "code"
        )

        return [
            ContextValue(
                key=cv_model.key,
                type=ContextValueType(cv_model.type),
                value=self._deserialize(cv_model.value, cv_model.serializer),
                code=cv_model.code or None,
            )
            for cv_model in qs
        ]

    @metrics.setup_histogram(metrics.ENGINE_RUNTIME_CONTEXT_REF_READ_TIME)
    def get_context_key_references(self, pipeline_id: str, keys: set) -> set:
        """
        获取某个流程上下文中 keys 所指定的变量直接和间接引用的其他所有变量的键

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        :param keys: 变量 key 列表
        :type keys: set
        :return: keys 所指定的变量直接和简介引用的其他所有变量的键
        :rtype: set
        """
        qs = DBContextValue.objects.filter(pipeline_id=pipeline_id, key__in=keys).only("references")

        references = []
        for cv_model in qs:
            references.extend(json.loads(cv_model.references))

        return set(references)

    @metrics.setup_histogram(metrics.ENGINE_RUNTIME_CONTEXT_VALUE_UPSERT_TIME)
    @transaction.atomic
    def upsert_plain_context_values(self, pipeline_id: str, update: Dict[str, ContextValue]):
        """
        更新或创建新的普通上下文数据

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        :param update: 更新数据
        :type update: Dict[str, ContextValue]
        """
        exist_keys = DBContextValue.objects.filter(pipeline_id=pipeline_id).values_list("key", flat=True)
        update_keys = set(update.keys()).intersection(exist_keys)

        # update
        for k in update_keys:
            context_value = update[k]
            value, serializer = self._serialize(context_value.value)

            DBContextValue.objects.filter(pipeline_id=pipeline_id, key=k).update(
                type=ContextValueType.PLAIN.value, value=value, serializer=serializer, code="", references="[]",
            )

        # insert
        insert_keys = set(update.keys()).difference(exist_keys)
        context_value_models = []
        for k in insert_keys:
            context_value = update[k]
            value, serializer = self._serialize(context_value.value)

            context_value_models.append(
                DBContextValue(
                    pipeline_id=pipeline_id,
                    key=context_value.key,
                    type=ContextValueType.PLAIN.value,
                    serializer=serializer,
                    value=value,
                    code="",
                    references="[]",
                )
            )

        DBContextValue.objects.bulk_create(context_value_models, batch_size=500)

    @metrics.setup_histogram(metrics.ENGINE_RUNTIME_CONTEXT_VALUE_READ_TIME)
    def get_context(self, pipeline_id: str) -> List[ContextValue]:
        """
        获取某个流程的所有上下文数据

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        :return: [description]
        :rtype: List[ContextValue]
        """
        qs = DBContextValue.objects.filter(pipeline_id=pipeline_id).only("key", "type", "serializer", "value", "code")

        return [
            ContextValue(
                key=cv_model.key,
                type=ContextValueType(cv_model.type),
                value=self._deserialize(cv_model.value, cv_model.serializer),
                code=cv_model.code or None,
            )
            for cv_model in qs
        ]

    def get_context_outputs(self, pipeline_id: str) -> Set[str]:
        """
        获取流程上下文需要输出的数据

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        :return: 输出数据 key
        :rtype: Set[str]
        """
        co_model = ContextOutputs.objects.get(pipeline_id=pipeline_id)
        return set(json.loads(co_model.outputs))
