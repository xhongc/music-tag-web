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

import contextlib
import logging
import traceback

from django.db import transaction

from pipeline.django_signal_valve import valve
from pipeline.engine.core import context
from pipeline.engine import exceptions, signals, states
from pipeline.engine.core.data import delete_parent_data, get_schedule_parent_data, set_schedule_data
from pipeline.engine.models import Data, MultiCallbackData, PipelineProcess, ScheduleService, Status

logger = logging.getLogger("pipeline_engine")
celery_logger = logging.getLogger("celery")


@contextlib.contextmanager
def schedule_exception_handler(process_id, schedule_id):
    try:
        yield
    except Exception as e:
        activity_id = schedule_id[: ScheduleService.SCHEDULE_ID_SPLIT_DIVISION]
        version = schedule_id[ScheduleService.SCHEDULE_ID_SPLIT_DIVISION :]
        if Status.objects.filter(id=activity_id, version=version).exists():
            logger.error(traceback.format_exc())
            process = PipelineProcess.objects.get(id=process_id)
            process.exit_gracefully(e)
        else:
            logger.warning("schedule({} - {}) forced exit.".format(activity_id, version))

        delete_parent_data(schedule_id)


@contextlib.contextmanager
def auto_release_schedule_lock(schedule_id):
    yield
    # release schedule lock before exit schedule
    ScheduleService.objects.filter(id=schedule_id, is_scheduling=True).update(is_scheduling=False)
    logger.warning("schedule({}) unlock success.".format(schedule_id))


def schedule(process_id, schedule_id, data_id=None):
    """
    调度服务主函数
    :param process_id: 被调度的节点所属的 PipelineProcess
    :param schedule_id: 调度 ID
    :param data_id: 回调数据ID
    :return:
    """
    with schedule_exception_handler(process_id, schedule_id):
        # set up context
        context.set_node_id(schedule_id[: ScheduleService.SCHEDULE_ID_SPLIT_DIVISION])

        # schedule maybe destroyed by other schedule
        try:
            sched_service = ScheduleService.objects.get(id=schedule_id)
            # stop if schedule status finished
            if sched_service.is_finished:
                logger.warning("schedule already finished, give up, sched_id: {}".format(schedule_id))
                return
        except ScheduleService.DoesNotExist:
            logger.warning("schedule not exist, give up, sched_id: {}".format(schedule_id))
            return

        # check whether the node is in a state waiting for scheduling
        service_act = sched_service.service_act
        act_id = sched_service.activity_id
        version = sched_service.version

        if not Status.objects.filter(id=act_id, version=version, state=states.RUNNING).exists():
            # forced failed
            logger.warning(
                "schedule service failed, schedule({} - {}) node state is not running or version do not match.".format(
                    act_id, version
                )
            )
            sched_service.destroy()
            return

        # try update lock schedule
        is_updated = ScheduleService.objects.filter(id=schedule_id, is_scheduling=False).update(is_scheduling=True)

        # lock failed, other worker may locking
        if is_updated == 0:
            # only retry at multi calback enabled case
            if not sched_service.multi_callback_enabled:
                logger.warning(
                    "invalid schedule request, schedule({} - {}) node state is not multi callback enabled type.".format(
                        act_id, version
                    )
                )
                return

            # retry lock after seconds
            logger.warning("schedule service lock-{} failed, retry after seconds".format(schedule_id))
            valve.send(
                signals,
                "schedule_ready",
                sender=ScheduleService,
                process_id=process_id,
                schedule_id=schedule_id,
                data_id=data_id,
                countdown=2,
            )
            return

        celery_logger.info("[pipeline-trace] schedule node %s with version %s" % (act_id, version))
        with auto_release_schedule_lock(schedule_id):
            # get data
            parent_data = get_schedule_parent_data(sched_service.id)
            if parent_data is None:
                raise exceptions.DataRetrieveError(
                    "child process({}) retrieve parent_data error, sched_id: {}".format(process_id, schedule_id)
                )

            # get schedule data
            if sched_service.multi_callback_enabled and data_id:
                try:
                    callback_data = MultiCallbackData.objects.get(id=data_id)
                    schedule_data = callback_data.data
                except MultiCallbackData.DoesNotExist:
                    logger.warning(
                        "schedule get callback_data failed, give up schedule, sched_id: {}".format(schedule_id)
                    )
                    return
            else:
                schedule_data = sched_service.callback_data

            # schedule
            ex_data, success = None, False
            try:
                success = service_act.schedule(parent_data, schedule_data)
                if success is None:
                    success = True
            except Exception:
                if service_act.error_ignorable:
                    success = True
                    service_act.ignore_error()
                    service_act.finish_schedule()

                ex_data = traceback.format_exc()
                logging.error(ex_data)

            sched_service.schedule_times += 1
            set_schedule_data(sched_service.id, parent_data)

            # schedule failed
            if not success:
                if not Status.objects.transit(id=act_id, version=version, to_state=states.FAILED).result:
                    # forced failed
                    logger.warning(
                        "FAILED transit failed, schedule({} - {}) had been forced exit.".format(act_id, version)
                    )
                    sched_service.destroy()
                    return

                if service_act.timeout:
                    signals.service_activity_timeout_monitor_end.send(
                        sender=service_act.__class__, node_id=service_act.id, version=version
                    )
                    logger.info("node {} {} timeout monitor revoke".format(service_act.id, version))

                Data.objects.write_node_data(service_act, ex_data=ex_data)

                with transaction.atomic():
                    process = PipelineProcess.objects.select_for_update().get(id=sched_service.process_id)
                    if not process.is_alive:
                        logger.info("pipeline %s has been revoked, status adjust failed." % process.root_pipeline_id)
                        return

                    process.adjust_status()

                # send activity error signal
                try:
                    service_act.schedule_fail()
                except Exception:
                    logger.error("schedule_fail handler fail: %s" % traceback.format_exc())

                signals.service_schedule_fail.send(
                    sender=ScheduleService, activity_shell=service_act, schedule_service=sched_service, ex_data=ex_data
                )

                valve.send(
                    signals,
                    "activity_failed",
                    sender=process.root_pipeline,
                    pipeline_id=process.root_pipeline_id,
                    pipeline_activity_id=service_act.id,
                    subprocess_id_stack=process.subprocess_stack,
                )
                return

            # schedule execute finished or one time callback finished
            if service_act.is_schedule_done() or sched_service.is_one_time_callback():
                error_ignorable = not service_act.get_result_bit()
                if not Status.objects.transit(id=act_id, version=version, to_state=states.FINISHED).result:
                    # forced failed
                    logger.warning(
                        "FINISHED transit failed, schedule({} - {}) had been forced exit.".format(act_id, version)
                    )
                    sched_service.destroy()
                    return

                if service_act.timeout:
                    signals.service_activity_timeout_monitor_end.send(
                        sender=service_act.__class__, node_id=service_act.id, version=version
                    )
                    logger.info("node {} {} timeout monitor revoke".format(service_act.id, version))

                Data.objects.write_node_data(service_act)
                if error_ignorable:
                    s = Status.objects.get(id=act_id)
                    s.error_ignorable = True
                    s.save()

                # sync parent data
                process = PipelineProcess.objects.get(id=sched_service.process_id)
                if not process.is_alive:
                    logger.warning("schedule({} - {}) revoked.".format(act_id, version))
                    sched_service.destroy()
                    return

                process.top_pipeline.data.update_outputs(parent_data.get_outputs())
                # extract outputs
                process.top_pipeline.context.extract_output(service_act)
                process.save(save_snapshot=True)

                # clear temp data
                delete_parent_data(sched_service.id)
                # save schedule service
                sched_service.finish()

                signals.service_schedule_success.send(
                    sender=ScheduleService, activity_shell=service_act, schedule_service=sched_service
                )

                valve.send(
                    signals,
                    "wake_from_schedule",
                    sender=ScheduleService,
                    process_id=sched_service.process_id,
                    activity_id=sched_service.activity_id,
                )
            else:
                Data.objects.write_node_data(service_act)
                if sched_service.multi_callback_enabled:
                    sched_service.save()
                else:
                    sched_service.set_next_schedule()
