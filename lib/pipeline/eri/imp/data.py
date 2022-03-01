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
from typing import Dict

from bamboo_engine import metrics, exceptions
from bamboo_engine.eri import Data, DataInput, ExecutionData, CallbackData

from pipeline.eri import codec
from pipeline.eri.models import Data as DBData
from pipeline.eri.models import ExecutionData as DBExecutionData
from pipeline.eri.models import CallbackData as DBCallbackData
from pipeline.eri.imp.serializer import SerializerMixin


class DataMixin(SerializerMixin):
    def _get_data_inputs(self, inputs: dict):
        return {k: DataInput(need_render=v["need_render"], value=v["value"]) for k, v in inputs.items()}

    @metrics.setup_histogram(metrics.ENGINE_RUNTIME_DATA_READ_TIME)
    def get_data(self, node_id: str) -> Data:
        """
        获取某个节点的数据对象

        :param node_id: 节点 ID
        :type node_id: str
        :return: 数据对象实例
        :rtype: Data
        """
        try:
            data_model = DBData.objects.get(node_id=node_id)
        except DBData.DoesNotExist:
            raise exceptions.NotFoundError
        return Data(
            inputs=self._get_data_inputs(codec.data_json_loads(data_model.inputs)),
            outputs=json.loads(data_model.outputs),
        )

    @metrics.setup_histogram(metrics.ENGINE_RUNTIME_DATA_INPUTS_READ_TIME)
    def get_data_inputs(self, node_id: str) -> Dict[str, DataInput]:
        """
        获取某个节点的输入数据

        :param node_id: 节点 ID
        :type node_id: str
        :return: 输入数据字典
        :rtype: dict
        """
        qs = DBData.objects.filter(node_id=node_id).only("inputs")

        if not qs:
            raise exceptions.NotFoundError

        return self._get_data_inputs(codec.data_json_loads(qs[0].inputs))

    @metrics.setup_histogram(metrics.ENGINE_RUNTIME_DATA_OUTPUTS_READ_TIME)
    def get_data_outputs(self, node_id: str) -> dict:
        """
        获取某个节点的输出数据

        :param node_id: 节点 ID
        :type node_id: str
        :return: 输入数据字典
        :rtype: dict
        """
        qs = DBData.objects.filter(node_id=node_id).only("outputs")

        if not qs:
            raise exceptions.NotFoundError

        return json.loads(qs[0].outputs)

    def set_data_inputs(self, node_id: str, data: Dict[str, DataInput]):
        """
        将节点数据对象的 inputs 设置为 data

        : param node_id: 节点 ID
        : type node_id: str
        : param data: 目标数据
        : type data: dict
        """
        inputs = codec.data_json_dumps({k: {"need_render": v.need_render, "value": v.value} for k, v in data.items()})
        if DBData.objects.filter(node_id=node_id).exists():
            DBData.objects.filter(node_id=node_id).update(inputs=inputs)
        else:
            DBData.objects.create(node_id=node_id, inputs=inputs, outputs="{}")

    @metrics.setup_histogram(metrics.ENGINE_RUNTIME_EXEC_DATA_READ_TIME)
    def get_execution_data(self, node_id: str) -> ExecutionData:
        """
        获取某个节点的执行数据

        : param node_id: 节点 ID
        : type node_id: str
        : return: 执行数据实例
        : rtype: ExecutionData
        """
        try:
            data_model = DBExecutionData.objects.get(node_id=node_id)
        except DBExecutionData.DoesNotExist:
            raise exceptions.NotFoundError
        return ExecutionData(
            inputs=self._deserialize(data_model.inputs, data_model.inputs_serializer),
            outputs=self._deserialize(data_model.outputs, data_model.outputs_serializer),
        )

    @metrics.setup_histogram(metrics.ENGINE_RUNTIME_EXEC_DATA_INPUTS_READ_TIME)
    def get_execution_data_inputs(self, node_id: str) -> dict:
        """
        获取某个节点的执行数据输入

        :param node_id: 节点 ID
        :type node_id: str
        :return: 执行数据输入
        :rtype: dict
        """
        qs = DBExecutionData.objects.filter(node_id=node_id).only("inputs_serializer", "inputs")

        if not qs:
            return {}

        return self._deserialize(qs[0].inputs, qs[0].inputs_serializer)

    @metrics.setup_histogram(metrics.ENGINE_RUNTIME_EXEC_DATA_OUTPUTS_READ_TIME)
    def get_execution_data_outputs(self, node_id: str) -> dict:
        """
        获取某个节点的执行数据输出

        :param node_id: 节点 ID
        :type node_id: str
        :return: 执行数据输出
        :rtype: dict
        """
        qs = DBExecutionData.objects.filter(node_id=node_id).only("outputs_serializer", "outputs")

        if not qs:
            return {}

        return self._deserialize(qs[0].outputs, qs[0].outputs_serializer)

    @metrics.setup_histogram(metrics.ENGINE_RUNTIME_EXEC_DATA_WRITE_TIME)
    def set_execution_data(self, node_id: str, data: ExecutionData):
        """
        设置某个节点的执行数据

        :param node_id: 节点 ID
        :type node_id: str
        :param data: 执行数据实例
        :type data: ExecutionData
        """
        inputs, inputs_serializer = self._serialize(data.inputs)
        outputs, outputs_serializer = self._serialize(data.outputs)
        if DBExecutionData.objects.filter(node_id=node_id).exists():
            DBExecutionData.objects.filter(node_id=node_id).update(
                inputs=inputs,
                inputs_serializer=inputs_serializer,
                outputs=outputs,
                outputs_serializer=outputs_serializer,
            )
        else:
            DBExecutionData.objects.create(
                node_id=node_id,
                inputs=inputs,
                inputs_serializer=inputs_serializer,
                outputs=outputs,
                outputs_serializer=outputs_serializer,
            )

    @metrics.setup_histogram(metrics.ENGINE_RUNTIME_EXEC_DATA_INPUTS_WRITE_TIME)
    def set_execution_data_inputs(self, node_id: str, inputs: dict):
        """
        设置某个节点的执行数据输入

        :param node_id: 节点 ID
        :type node_id: str
        :param outputs: 输出数据
        :type outputs: dict
        """
        inputs, inputs_serializer = self._serialize(inputs)
        if DBExecutionData.objects.filter(node_id=node_id).exists():
            DBExecutionData.objects.filter(node_id=node_id).update(inputs=inputs, inputs_serializer=inputs_serializer)
        else:
            DBExecutionData.objects.create(
                node_id=node_id,
                inputs=inputs,
                inputs_serializer=inputs_serializer,
                outputs="{}",
                outputs_serializer=self.JSON_SERIALIZER,
            )

    @metrics.setup_histogram(metrics.ENGINE_RUNTIME_EXEC_DATA_OUTPUTS_WRITE_TIME)
    def set_execution_data_outputs(self, node_id: str, outputs: dict):
        """
        设置某个节点的执行数据输出

        :param node_id: 节点 ID
        :type node_id: str
        :param outputs: 输出数据
        :type outputs: dict
        """
        outputs, outputs_serializer = self._serialize(outputs)
        if DBExecutionData.objects.filter(node_id=node_id).exists():
            DBExecutionData.objects.filter(node_id=node_id).update(
                outputs=outputs, outputs_serializer=outputs_serializer
            )
        else:
            DBExecutionData.objects.create(
                node_id=node_id,
                inputs="{}",
                inputs_serializer=self.JSON_SERIALIZER,
                outputs=outputs,
                outputs_serializer=outputs_serializer,
            )

    def set_callback_data(self, node_id: str, version: str, data: dict) -> int:
        """
        设置某个节点执行数据的回调数据

        :param node_id: 节点 ID
        :type node_id: str
        :param version: 节点执行版本
        :type version: str
        :param data: 回调数据
        :type data: dict
        :return: 回调数据 ID
        :rtype: int
        """
        return DBCallbackData.objects.create(node_id=node_id, version=version, data=json.dumps(data)).id

    @metrics.setup_histogram(metrics.ENGINE_RUNTIME_CALLBACK_DATA_READ_TIME)
    def get_callback_data(self, data_id: int) -> CallbackData:
        """
        获取回调数据

        :param data_id: Data ID
        :type data_id: int
        :return: 回调数据实例
        :rtype: CallbackData
        """
        data_model = DBCallbackData.objects.get(id=data_id)
        return CallbackData(
            id=data_model.id, node_id=data_model.node_id, version=data_model.version, data=json.loads(data_model.data)
        )
