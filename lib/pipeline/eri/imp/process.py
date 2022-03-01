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
from typing import List, Optional, Dict

from django.utils import timezone
from django.db.models import F

from bamboo_engine import metrics
from bamboo_engine.eri import ProcessInfo, SuspendedProcessInfo, DispatchProcess

from pipeline.eri.models import Process


class ProcessMixin:
    def beat(self, process_id: int):
        """
        进程心跳

        :param process_id: 进程 ID
        :type process_id: int
        """
        Process.objects.filter(id=process_id).update(last_heartbeat=timezone.now())

    def wake_up(self, process_id: int):
        """
        将当前进程标记为唤醒状态

        :param process_id: 进程 ID
        :type process_id: int
        """
        Process.objects.filter(id=process_id).update(asleep=False)

    def sleep(self, process_id: int):
        """
        将当前进程标记为睡眠状态

        :param process_id: 进程 ID
        :type process_id: int
        """
        Process.objects.filter(id=process_id).update(asleep=True)

    def suspend(self, process_id: int, by: str):
        """
        将当前进程标记为阻塞状态

        :param process_id: 进程 ID
        :type process_id: int
        :param by: 造成阻塞的节点信息
        :type by: str
        """
        Process.objects.filter(id=process_id).update(suspended=True, suspended_by=by)

    def resume(self, process_id: int):
        """
        将进程标记为非阻塞状态

        :param process_id: 进程 ID
        :type process_id: int
        """
        Process.objects.filter(id=process_id).update(suspended=False, suspended_by="")

    def batch_resume(self, process_id_list: List[int]):
        """
        批量将进程标记为非阻塞状态

        :param process_id_list: 进程 ID 列表
        :type process_id_list: List[int]
        """
        Process.objects.filter(id__in=process_id_list).update(suspended=False, suspended_by="")

    def die(self, process_id: int):
        """
        将当前进程标记为非存活状态

        :param process_id: 进程 ID
        :type process_id: int
        """
        Process.objects.filter(id=process_id).update(dead=True)

    @metrics.setup_histogram(metrics.ENGINE_RUNTIME_PROCESS_READ_TIME)
    def get_process_info(self, process_id: int) -> ProcessInfo:
        """
        获取某个进程的基本信息

        :param process_id: 进程 ID
        :type process_id: int
        :return: 进程基本信息
        :rtype: ProcessInfo
        """
        qs = Process.objects.filter(id=process_id).only(
            "id", "destination_id", "root_pipeline_id", "pipeline_stack", "parent_id"
        )

        if len(qs) != 1:
            raise Process.DoesNotExist("Process with id({}) does not exist".format(process_id))

        process = qs[0]
        return ProcessInfo(
            process_id=process.id,
            destination_id=process.destination_id,
            root_pipeline_id=process.root_pipeline_id,
            pipeline_stack=json.loads(process.pipeline_stack),
            parent_id=process.parent_id,
        )

    def kill(self, process_id: int):
        """
        强制结束某个进程正在进行的活动，并将其标志为睡眠状态

        :param process_id: 进程 ID
        :type process_id: int
        """
        Process.objects.filter(id=process_id).update(asleep=True)

    def get_suspended_process_info(self, suspended_by: str) -> List[SuspendedProcessInfo]:
        """
        获取由于 pipeline 暂停而被暂停执行的进程信息

        : param suspended_by: 进程 ID
        : type suspended_by: str
        : return: 暂停的进程信息
        : rtype: SuspendedProcessInfo
        """
        qs = Process.objects.filter(suspended_by=suspended_by).only(
            "id", "current_node_id", "root_pipeline_id", "pipeline_stack"
        )

        return [
            SuspendedProcessInfo(
                process_id=p.id,
                current_node=p.current_node_id,
                root_pipeline_id=p.root_pipeline_id,
                pipeline_stack=json.loads(p.pipeline_stack),
            )
            for p in qs
        ]

    def get_sleep_process_info_with_current_node_id(self, node_id: str) -> Optional[ProcessInfo]:
        """
        获取由于处于睡眠状态且当前节点 ID 为 node_id 的进程 ID

        : param node_id: 节点 ID
        : type node_id: str
        : return: 进程 ID
        : rtype: str
        """
        qs = Process.objects.filter(asleep=True, current_node_id=node_id).only(
            "id", "destination_id", "root_pipeline_id", "pipeline_stack", "parent_id"
        )

        if len(qs) == 0:
            return None

        if len(qs) != 1:
            raise ValueError("found multiple sleep process({}) with current_node_id({})".format(qs, node_id))

        return ProcessInfo(
            process_id=qs[0].id,
            destination_id=qs[0].destination_id,
            root_pipeline_id=qs[0].root_pipeline_id,
            pipeline_stack=json.loads(qs[0].pipeline_stack),
            parent_id=qs[0].parent_id,
        )

    def get_process_id_with_current_node_id(self, node_id: str) -> Optional[str]:
        """
        获取当前节点 ID 为 node_id 且存活的进程 ID

        : param node_id: 节点 ID
        : type node_id: str
        : return: 进程 ID
        : rtype: str
        """
        qs = Process.objects.filter(dead=False, current_node_id=node_id).only("id")

        if len(qs) == 0:
            return None

        if len(qs) != 1:
            raise ValueError("found multiple process({}) with current_node_id({})".format(qs, node_id))

        return qs[0].id

    def set_current_node(self, process_id: int, node_id: str):
        """
        将进程当前处理节点标记为 node

        :param process_id: 进程 ID
        :type process_id: int
        :param node_id: 节点 ID
        :type node_id: str
        """
        Process.objects.filter(id=process_id).update(current_node_id=node_id)

    def child_process_finish(self, parent_id: int, process_id: int) -> bool:
        """
        标记某个进程的子进程执行完成，并返回是否能够唤醒父进程继续执行的标志位

        :param parent_id: 父进程 ID
        :type parent_id: int
        :param process_id: 子进程 ID
        :type process_id: int
        :return: 是否能够唤醒父进程继续执行
        :rtype: bool
        """
        Process.objects.filter(id=process_id).update(dead=True)

        Process.objects.filter(id=parent_id).update(ack_num=F("ack_num") + 1)

        # compare(where) and set(update)
        row = Process.objects.filter(id=parent_id, ack_num=F("need_ack")).update(ack_num=0, need_ack=-1)

        return row != 0

    def is_frozen(self, process_id: int) -> bool:
        """
        检测当前进程是否需要被冻结

        :param process_id: 进程 ID
        :type process_id: int
        :return: 是否需要被冻结
        :rtype: bool
        """
        return Process.objects.filter(id=process_id, frozen=True).exists()

    def freeze(self, process_id: int):
        """
        冻结当前进程

        :param process_id: 进程 ID
        :type process_id: int
        """
        Process.objects.filter(id=process_id).update(frozen=True)

    def fork(
        self,
        parent_id: str,
        root_pipeline_id: str,
        pipeline_stack: List[str],
        from_to: Dict[str, str],
    ) -> List[DispatchProcess]:
        """
        根据当前进程 fork 出多个子进程

        :param parent_id: 父进程 ID
        :type parent_id: str
        :param root_pipeline_id: 根流程 ID
        :type root_pipeline_id: str
        :param pipeline_stack: 子流程栈
        :type pipeline_stack: List[str]
        :param from_to: 子进程的执行开始节点和目标节点
        :type from_to: Dict[str, str]
        :return: 待调度进程信息列表
        :rtype: List[DispatchProcess]
        """
        qs = Process.objects.filter(id=parent_id).only("priority", "queue")
        stack_json = json.dumps(pipeline_stack)

        if not qs:
            raise Process.DoesNotExist("Process with id({}) does not exist".format(parent_id))

        children = [
            Process(
                parent_id=parent_id,
                asleep=True,
                destination_id=destination,
                current_node_id=current_node,
                root_pipeline_id=root_pipeline_id,
                pipeline_stack=stack_json,
                priority=qs[0].priority,
                queue=qs[0].queue,
            )
            for current_node, destination in from_to.items()
        ]

        Process.objects.bulk_create(children, batch_size=500)

        qs = Process.objects.filter(parent_id=parent_id, dead=False).only("id", "current_node_id")

        children_count = len(qs)
        expect = len(from_to)
        if children_count != expect:
            raise ValueError(
                "process({}) fork failed, children count({}) does not match expect({})".format(
                    parent_id, children_count, expect
                )
            )

        return [DispatchProcess(process_id=p.id, node_id=p.current_node_id) for p in qs]

    def join(self, process_id: int, children_id: List[str]):
        """
        让父进程等待子进程

        :param process_id: 父进程 ID
        :type process_id: int
        :param children_id: 子进程 ID 列表
        :type children_id: List[str]
        """
        Process.objects.filter(id=process_id).update(ack_num=0, need_ack=len(children_id))

    def set_pipeline_stack(self, process_id: int, stack: List[str]):
        """
        设置进程的流程栈

        :param process_id: 进程 ID
        :type process_id: int
        :param stack: 流程栈
        :type stack: List[str]
        """
        Process.objects.filter(id=process_id).update(pipeline_stack=json.dumps(stack))

    def get_process_info_with_root_pipeline(self, pipeline_id: str) -> List[ProcessInfo]:
        """
        根据根流程 ID 获取一批进程的信息

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        :return: 进程基本信息
        :rtype: List[ProcessInfo]
        """
        qs = Process.objects.filter(root_pipeline_id=pipeline_id).only(
            "id", "destination_id", "root_pipeline_id", "pipeline_stack", "parent_id"
        )

        return [
            ProcessInfo(
                process_id=process.id,
                destination_id=process.destination_id,
                root_pipeline_id=process.root_pipeline_id,
                pipeline_stack=json.loads(process.pipeline_stack),
                parent_id=process.parent_id,
            )
            for process in qs
        ]
