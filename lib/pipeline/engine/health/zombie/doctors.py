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
import abc
import logging

from django.utils import timezone

from pipeline.core.pipeline import Pipeline
from pipeline.engine import signals, states
from pipeline.engine.models import ProcessCeleryTask, ScheduleService, Status
from pipeline.utils import uniqid

logger = logging.getLogger("celery")


class ZombieProcDoctor(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def confirm(self, proc):
        raise NotImplementedError()

    @abc.abstractmethod
    def cure(self, proc):
        raise NotImplementedError()


class RunningNodeZombieDoctor(ZombieProcDoctor):
    def __init__(self, max_stuck_time: float, detect_wait_callback_proc: bool = False):
        """
        :param max_stuck_time: 最大卡住时间
        :param detect_wait_callback_proc: 是否检测等待回调的进程
        """
        self.max_stuck_time = max_stuck_time
        self.detect_wait_callback_proc = detect_wait_callback_proc

    def confirm(self, proc):

        # do not process none current node
        if not proc.current_node_id:
            logger.warning("Process({}) with current_node({}), skip".format(proc.id, proc.current_node_id))
            return False

        # do not process node status not exist
        try:
            status = Status.objects.get(id=proc.current_node_id)
        except Status.DoesNotExist:
            logger.warning("Process({})'s current_node({}) not exist, skip".format(proc.id, proc.current_node_id))
            return False

        # do not process legacy status data
        if not status.state_refresh_at:
            logger.warning(
                "Process({})'s current_node({}) state_fresh_at({}) is invalid, skip".format(
                    proc.id, proc.current_node_id, status.state_refresh_at
                )
            )
            return False

        # only process RUNNING node
        if status.state != states.RUNNING:
            return False

        try:
            schedule = ScheduleService.objects.schedule_for(status.id, status.version)
        except ScheduleService.DoesNotExist:
            pass
        else:
            if schedule.wait_callback and not self.detect_wait_callback_proc:
                return False

        stuck_time = (timezone.now() - status.state_refresh_at).total_seconds()
        if float(stuck_time) > float(self.max_stuck_time):
            logger.info(
                "Process({}) with current_node({}) stuck_time({}) exceed max_stuck_time({}), "
                "mark as zombie".format(proc.id, proc.current_node_id, stuck_time, self.max_stuck_time)
            )
            return True

        return False

    def cure(self, proc):

        current_node_id = proc.current_node_id

        # try to transit current node to FAILURE
        try:
            result = Status.objects.raw_fail(
                node_id=current_node_id,
                ex_data="This node had been failed because the process diagnode as zombie process",
            )
        except Exception:
            logger.exception(
                "An error occurred when transit node({}) for zombie process({}).".format(current_node_id, proc.id)
            )
        else:
            if not result.result:
                logger.error(
                    "can't not transit node({}) for zombie process({}), message: {}".format(
                        current_node_id, proc.id, result.message
                    )
                )
            else:
                status = result.extra
                status.version = uniqid.uniqid()
                status.save()
                ProcessCeleryTask.objects.revoke(proc.id, kill=True)

                # adjust pipeline state
                proc.adjust_status()
                proc.is_sleep = True
                proc.save()
                logger.info(
                    "Zombie process({}) with node({}) had been cured by {}".format(
                        proc.id, current_node_id, self.__class__.__name__
                    )
                )
        try:
            signals.activity_failed.send(
                sender=Pipeline, pipeline_id=proc.root_pipeline_id, pipeline_activity_id=current_node_id
            )
        except Exception as e:
            logger.exception(
                "An error({}) occurred when send activity_failed signals node({}) "
                "for zombie process({}).".format(e, current_node_id, proc.id)
            )
