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

from typing import Optional

from bamboo_engine.eri import Service as ServiceInterface
from bamboo_engine.eri import Schedule, ExecutionData, CallbackData, ScheduleType

from pipeline.core.flow.activity import Service
from pipeline.core.data.base import DataObject
from pipeline.eri.log import get_logger


class ServiceWrapper(ServiceInterface):
    def __init__(self, service: Service):
        self.service = service

    def pre_execute(self, data: ExecutionData, root_pipeline_data: ExecutionData):
        """
        execute 执行前执行的逻辑

        :param data: 节点执行数据
        :type data: ExecutionData
        :param root_pipeline_data: 根流程执行数据
        :type root_pipeline_data: ExecutionData
        """
        pre_execute = getattr(self.service, "pre_execute", None)
        if callable(pre_execute):
            return pre_execute(DataObject(inputs=data.inputs, outputs=data.outputs))

    def execute(self, data: ExecutionData, root_pipeline_data: ExecutionData) -> bool:
        """
        execute 逻辑

        :param data: 节点执行数据
        :type data: ExecutionData
        :param root_pipeline_data: 根流程执行数据
        :type root_pipeline_data: ExecutionData
        :return: 是否执行成功
        :rtype: bool
        """
        data_obj = DataObject(inputs=data.inputs, outputs=data.outputs)
        parent_data_obj = DataObject(inputs=root_pipeline_data.inputs, outputs=root_pipeline_data.outputs)

        try:
            execute_res = self.service.execute(data_obj, parent_data_obj)
        finally:
            # sync data object modification to execution data
            data.inputs = data_obj.inputs
            data.outputs = data_obj.outputs

        if execute_res is None:
            execute_res = True

        return execute_res

    def schedule(
        self,
        schedule: Schedule,
        data: ExecutionData,
        root_pipeline_data: ExecutionData,
        callback_data: Optional[CallbackData] = None,
    ) -> bool:
        """
        schedule 逻辑

        :param schedule: Schedule 对象
        :type schedule: Schedule
        :param data: 节点执行数据
        :type data: ExecutionData
        :param root_pipeline_data: 根流程执行数据
        :type root_pipeline_data: ExecutionData
        :param callback_data: 回调数据, defaults to None
        :type callback_data: Optional[CallbackData], optional
        :return: [description]
        :rtype: bool
        """
        data_obj = DataObject(inputs=data.inputs, outputs=data.outputs)
        parent_data_obj = DataObject(inputs=root_pipeline_data.inputs, outputs=root_pipeline_data.outputs)

        try:
            schedule_res = self.service.schedule(
                data_obj, parent_data_obj, callback_data.data if callback_data else None
            )
        except Exception as e:
            raise e
        finally:
            # sync data object modification to execution data
            data.inputs = data_obj.inputs
            data.outputs = data_obj.outputs

        if schedule_res is None:
            schedule_res = True

        return schedule_res

    def need_schedule(self) -> bool:
        """
        服务是否需要调度

        :return: 是否需要调度
        :rtype: bool
        """
        return self.service.need_schedule()

    def schedule_type(self) -> Optional[ScheduleType]:
        """
        服务调度类型

        :return: 调度类型
        :rtype: Optional[ScheduleType]
        """
        if not self.service.need_schedule():
            return None

        if self.service.interval:
            return ScheduleType.POLL

        if not self.service.multi_callback_enabled():
            return ScheduleType.CALLBACK

        return ScheduleType.MULTIPLE_CALLBACK

    def is_schedule_done(self) -> bool:
        """
        调度是否完成

        :return: 调度是否完成
        :rtype: bool
        """
        return self.service.is_schedule_finished()

    def schedule_after(
        self, schedule: Optional[Schedule], data: ExecutionData, root_pipeline_data: ExecutionData
    ) -> int:
        """
        计算下一次调度间隔

        :param schedule: 调度对象，未进行调度时传入为空
        :type schedule: Optional[Schedule]
        :param data: 节点执行数据
        :type data: ExecutionData
        :param root_pipeline_data: 根流程执行数据
        :type root_pipeline_data: ExecutionData
        :return: 调度间隔，单位为秒
        :rtype: int
        """
        if self.service.interval is None:
            return -1

        if schedule is None:
            return self.service.interval.next()

        # count will add in next, so minus 1 at here
        self.service.interval.count = schedule.times - 1

        return self.service.interval.next()

    def setup_runtime_attributes(self, **attrs):
        """
        装载运行时属性

        :param attrs: 运行时属性
        :type attrs: Dict[str, Any]
        """

        attrs["logger"] = get_logger(node_id=attrs["id"], loop=attrs["loop"], version=attrs["version"])
        self.service.setup_runtime_attrs(**attrs)
