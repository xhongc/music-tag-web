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

from django.db.models import F

from bamboo_engine import metrics
from bamboo_engine.eri import Schedule, ScheduleType

from pipeline.eri.models import Schedule as DBSchedule


class ScheduleMixin:
    @metrics.setup_histogram(metrics.ENGINE_RUNTIME_SCHEDULE_WRITE_TIME)
    def set_schedule(self, process_id: int, node_id: str, version: str, schedule_type: ScheduleType) -> Schedule:
        """
        设置 schedule 对象

        :param process_id: 进程 ID
        :type process_id: int
        :param node_id: 节点 ID
        :type node_id: str
        :param version: 执行版本
        :type version: str
        :param schedule_type: 调度类型
        :type schedule_type: ScheduleType
        :return: 调度对象实例
        :rtype: Schedule
        """
        schedule_model = DBSchedule.objects.create(
            process_id=process_id, node_id=node_id, type=schedule_type.value, version=version
        )
        return Schedule(
            id=schedule_model.id,
            type=schedule_type,
            process_id=schedule_model.process_id,
            node_id=schedule_model.node_id,
            finished=schedule_model.finished,
            expired=schedule_model.expired,
            version=schedule_model.version,
            times=schedule_model.schedule_times,
        )

    @metrics.setup_histogram(metrics.ENGINE_RUNTIME_SCHEDULE_READ_TIME)
    def get_schedule(self, schedule_id: str) -> Schedule:
        """
        获取 Schedule 对象

        :param schedule_id: 调度实例 ID
        :type schedule_id: str
        :return: Schedule 对象实例
        :rtype: Schedule
        """
        schedule_model = DBSchedule.objects.get(id=schedule_id)

        return Schedule(
            id=schedule_model.id,
            type=ScheduleType(schedule_model.type),
            process_id=schedule_model.process_id,
            node_id=schedule_model.node_id,
            finished=schedule_model.finished,
            expired=schedule_model.expired,
            version=schedule_model.version,
            times=schedule_model.schedule_times,
        )

    def get_schedule_with_node_and_version(self, node_id: str, version: str) -> Schedule:
        """
        通过节点 ID 和执行版本来获取 Scheudle 对象

        :param node_id: 节点 ID
        :type node_id: str
        :param version: 执行版本
        :type version: str
        :return: Schedule 对象
        :rtype: Schedule
        """
        schedule_model = DBSchedule.objects.get(node_id=node_id, version=version)

        return Schedule(
            id=schedule_model.id,
            type=ScheduleType(schedule_model.type),
            process_id=schedule_model.process_id,
            node_id=schedule_model.node_id,
            finished=schedule_model.finished,
            expired=schedule_model.expired,
            version=schedule_model.version,
            times=schedule_model.schedule_times,
        )

    def apply_schedule_lock(self, schedule_id: str) -> bool:
        """
        获取 Schedule 对象的调度锁，返回是否成功获取锁

        :param schedule_id: 调度实例 ID
        :type schedule_id: str
        :return: 是否成功获取锁
        :rtype: bool
        """
        return DBSchedule.objects.filter(id=schedule_id, scheduling=False).update(scheduling=True) == 1

    def release_schedule_lock(self, schedule_id: int):
        """
        释放指定 Schedule 的调度锁

        :param schedule_id: Schedule ID
        :type schedule_id: int
        """
        DBSchedule.objects.filter(id=schedule_id, scheduling=True).update(scheduling=False)

    def expire_schedule(self, schedule_id: int):
        """
        将某个 Schedule 对象标记为已过期

        :param schedule_id: 调度实例 ID
        :type schedule_id: int
        """
        DBSchedule.objects.filter(id=schedule_id).update(expired=True)

    def finish_schedule(self, schedule_id: int):
        """
        将某个 Schedule 对象标记为已完成

        :param schedule_id: 调度实例 ID
        :type schedule_id: int
        """
        DBSchedule.objects.filter(id=schedule_id).update(finished=True)

    def add_schedule_times(self, schedule_id: int):
        """
        将某个 Schedule 对象的调度次数 +1

        :param schedule_id: 调度实例 ID
        :type schedule_id: int
        """
        DBSchedule.objects.filter(id=schedule_id).update(schedule_times=F("schedule_times") + 1)
