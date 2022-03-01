# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging
import datetime
from dateutil.relativedelta import relativedelta
from celery import task
from celery.schedules import crontab
from celery.task import periodic_task
from django.db import transaction, connection

from pipeline.conf import default_settings
from pipeline.core.pipeline import Pipeline
from pipeline.engine import api, signals, states
from pipeline.engine.core import runtime, schedule
from pipeline.engine.health import zombie
from pipeline.engine.models import (
    NodeCeleryTask,
    NodeRelationship,
    PipelineProcess,
    ProcessCeleryTask,
    Status,
    ScheduleService,
    History,
)
from pipeline.models import PipelineInstance

logger = logging.getLogger("celery")


@task(ignore_result=True)
def process_unfreeze(process_id):
    process = PipelineProcess.objects.get(id=process_id)
    if not process.is_alive:
        logger.warning("process(%s) is not alive, mission cancel." % process_id)
        return

    runtime.run_loop(process)


@task(ignore_result=True)
def start(process_id):
    process = PipelineProcess.objects.get(id=process_id)
    if not process.is_alive:
        logger.warning("process(%s) is not alive, mission cancel." % process_id)
        return

    pipeline_id = process.root_pipeline.id
    # try to run
    action_result = Status.objects.transit(pipeline_id, states.RUNNING, is_pipeline=True, start=True)
    if not action_result.result:
        logger.warning("can not start pipeline({}), message: {}".format(pipeline_id, action_result.message))
        return

    NodeRelationship.objects.build_relationship(pipeline_id, pipeline_id)

    runtime.run_loop(process)


@task(ignore_result=True)
def dispatch(child_id):
    process = PipelineProcess.objects.get(id=child_id)
    if not process.is_alive:
        logger.info("process(%s) is not alive, mission cancel." % child_id)
        return

    runtime.run_loop(process)


@task(ignore_result=True)
def process_wake_up(process_id, current_node_id=None, call_from_child=False):
    process = PipelineProcess.objects.get(id=process_id)
    if not process.is_alive:
        logger.warning("process(%s) is not alive, mission cancel." % process_id)
        return

    pipeline_id = process.root_pipeline.id
    if not call_from_child:
        # success_when_unchanged to deal with parallel wake up
        action_result = Status.objects.transit(
            pipeline_id, to_state=states.RUNNING, is_pipeline=True, unchanged_pass=True
        )
        if not action_result.result:
            # BLOCKED is a tolerant running state
            if action_result.extra.state != states.BLOCKED:
                logger.warning("can not start pipeline({}), message: {}".format(pipeline_id, action_result.message))
                return

    process.wake_up()
    if current_node_id:
        process.current_node_id = current_node_id

    runtime.run_loop(process)


@task(ignore_result=True)
def wake_up(process_id):
    process = PipelineProcess.objects.get(id=process_id)
    if not process.is_alive:
        logger.warning("process(%s) is not alive, mission cancel." % process_id)
        return

    process.wake_up()
    runtime.run_loop(process)


@task(ignore_result=True)
def batch_wake_up(process_id_list, pipeline_id):
    # success_when_unchanged to deal with parallel gateway subprocess wake up
    action_result = Status.objects.transit(pipeline_id, to_state=states.RUNNING, is_pipeline=True, unchanged_pass=True)
    if not action_result.result:
        logger.warning("can not start pipeline({}), message: {}".format(pipeline_id, action_result.message))
        return
    for process_id in process_id_list:
        task_id = wake_up.apply_async(args=[process_id]).id
        ProcessCeleryTask.objects.bind(process_id, task_id)


@task(ignore_result=True)
def wake_from_schedule(process_id, service_act_id):
    process = PipelineProcess.objects.get(id=process_id)
    process.wake_up()

    service_act = process.top_pipeline.node(service_act_id)
    process.current_node_id = service_act.next().id
    runtime.run_loop(process)


@task(ignore_result=True)
def service_schedule(process_id, schedule_id, data_id=None):
    schedule.schedule(process_id, schedule_id, data_id)


@task(ignore_result=True)
def node_timeout_check(node_id, version, root_pipeline_id):
    NodeCeleryTask.objects.destroy(node_id)
    state = Status.objects.state_for(node_id, version=version, may_not_exist=True)
    if not state or state != states.RUNNING:
        logger.warning("node {} {} timeout kill failed, node not exist or not in running".format(node_id, version))
        return

    action_result = api.forced_fail(node_id, kill=True, ex_data="node execution timeout")
    if action_result.result:
        signals.activity_failed.send(sender=Pipeline, pipeline_id=root_pipeline_id, pipeline_activity_id=node_id)
    else:
        logger.warning("node {} - {} timeout kill failed".format(node_id, version))


@periodic_task(run_every=(crontab(**default_settings.ENGINE_ZOMBIE_PROCESS_HEAL_CRON)), ignore_result=True)
def heal_zombie_process():
    logger.info("Zombie process heal start")

    healer = zombie.get_healer()

    try:
        healer.heal()
    except Exception:
        logger.exception("An error occurred when healing zombies")

    logger.info("Zombie process heal finish")


@periodic_task(run_every=(crontab(**default_settings.EXPIRED_TASK_CLEAN_CRON)), ignore_result=True)
def expired_tasks_clean():
    if not default_settings.EXPIRED_TASK_CLEAN:
        logger.info("EXPIRED_TASK_CLEAN switch off, won't clean expired tasks.")
        return
    timestamp = datetime.datetime.now().timestamp()
    logger.info("Expired tasks clean start, timestamp: {}".format(timestamp))

    expired_create_time = datetime.date.today() - relativedelta(months=default_settings.TASK_EXPIRED_MONTH)
    pipeline_instance_ids = list(
        PipelineInstance.objects.filter(
            create_time__lte=expired_create_time, is_finished=True, is_revoked=False, is_expired=False
        )
        .order_by("create_time")
        .values_list("instance_id", flat=True)[: default_settings.EXPIRED_TASK_CLEAN_NUM_LIMIT]
    )
    logger.info(
        "Clean expired tasks before {} with tasks number: {}, instance ids: {}, timestamp: {}".format(
            expired_create_time, len(pipeline_instance_ids), ",".join(pipeline_instance_ids), timestamp
        )
    )

    for instance_id in pipeline_instance_ids:
        try:
            logger.info("Clean expired task: {}, timestamp: {}".format(instance_id, timestamp))
            _clean_pipeline_instance_data(instance_id, timestamp)
        except Exception as e:
            logger.exception(
                "An error occurred when clean expired task instance {}: {}, {}".format(instance_id, e, timestamp)
            )

    logger.info("Expired tasks clean finish, timestamp: {}".format(timestamp))


def _clean_pipeline_instance_data(instance_id, timestamp):
    """
    根据instance_id删除对应的任务数据
    """
    process_nodes = list(
        set(NodeRelationship.objects.filter(ancestor_id=instance_id).values_list("descendant_id", flat=True))
    )
    process_nodes = [process_node for process_node in process_nodes if process_node]
    process_nodes_regex = "^" + "|^".join(process_nodes) if process_nodes else ""
    pipeline_processes = PipelineProcess.objects.filter(root_pipeline_id=instance_id).values_list("id", "snapshot__id")
    pipeline_process_ids, process_snapshot_ids = [], []
    for process_id, snapshot_id in pipeline_processes:
        if process_id:
            pipeline_process_ids.append(process_id)
        if snapshot_id:
            process_snapshot_ids.append(snapshot_id)

    delete_subprocess_relationship = (
        "DELETE FROM `engine_subprocessrelationship` WHERE `engine_subprocessrelationship`.`process_id` IN (%s)"
    )
    delete_process_snapshot = "DELETE FROM `engine_processsnapshot` WHERE `engine_processsnapshot`.`id` IN (%s)"
    delete_pipeline_model = "DELETE FROM `engine_pipelinemodel` WHERE `engine_pipelinemodel`.`process_id` IN (%s)"
    delete_process_celery_task = (
        "DELETE FROM `engine_processcelerytask` WHERE `engine_processcelerytask`.`process_id` IN (%s)"
    )
    schedule_service_ids = list(
        ScheduleService.objects.filter(process_id__in=pipeline_process_ids).values_list("id", flat=True)
    )
    schedule_service_ids = [schedule_service_id for schedule_service_id in schedule_service_ids if schedule_service_id]
    delete_schedule_service = "DELETE FROM `engine_scheduleservice` WHERE `engine_scheduleservice`.`process_id` IN (%s)"
    delete_multi_callback_data = (
        "DELETE FROM `engine_multicallbackdata` WHERE `engine_multicallbackdata`.`schedule_id` IN (%s)"
    )
    delete_node_relationship = (
        "DELETE FROM `engine_noderelationship` "
        "WHERE (`engine_noderelationship`.`ancestor_id` IN (%s) "
        "OR `engine_noderelationship`.`descendant_id` IN (%s)) "
    )
    delete_node_celery_tasks = "DELETE FROM `engine_nodecelerytask` " "WHERE `engine_nodecelerytask`.`node_id` IN (%s)"
    delete_status = "DELETE FROM `engine_status` WHERE `engine_status`.`id` IN (%s)"
    delete_data = "DELETE FROM `engine_data` WHERE `engine_data`.`id` IN (%s)"
    delete_datasnapshot = "DELETE FROM `engine_datasnapshot` WHERE `engine_datasnapshot`.`key` REGEXP %s"
    delete_schedule_celery_task = (
        "DELETE FROM `engine_schedulecelerytask`" "WHERE `engine_schedulecelerytask`.`schedule_id` REGEXP %s"
    )
    history_data_ids = list(
        History.objects.filter(identifier__in=process_nodes).only("data").values_list("data__id", flat=True)
    )
    delete_history = "DELETE FROM `engine_history` WHERE `engine_history`.`identifier` IN (%s)"
    delete_history_data = "DELETE FROM `engine_historydata` WHERE `engine_historydata`.`id` IN (%s)"
    delete_pipeline_process = (
        "DELETE FROM `engine_pipelineprocess` " "WHERE `engine_pipelineprocess`.`root_pipeline_id` = %s"
    )
    with transaction.atomic():
        with connection.cursor() as cursor:
            if pipeline_process_ids:
                process_fs = _sql_format_strings(pipeline_process_ids)
                _raw_sql_execute(cursor, delete_subprocess_relationship % process_fs, pipeline_process_ids, timestamp)
                _raw_sql_execute(cursor, delete_pipeline_model % process_fs, pipeline_process_ids, timestamp)
                _raw_sql_execute(cursor, delete_process_celery_task % process_fs, pipeline_process_ids, timestamp)
                _raw_sql_execute(cursor, delete_schedule_service % process_fs, pipeline_process_ids, timestamp)
            if process_snapshot_ids:
                snapshot_fd = _sql_format_strings(process_snapshot_ids)
                _raw_sql_execute(cursor, delete_process_snapshot % snapshot_fd, process_snapshot_ids, timestamp)
            if schedule_service_ids:
                service_fd = _sql_format_strings(schedule_service_ids)
                _raw_sql_execute(cursor, delete_multi_callback_data % service_fd, schedule_service_ids, timestamp)
            if process_nodes:
                node_fs = _sql_format_strings(process_nodes)
                _raw_sql_execute(
                    cursor, delete_node_relationship % (node_fs, node_fs), process_nodes + process_nodes, timestamp
                )
                _raw_sql_execute(cursor, delete_node_celery_tasks % node_fs, process_nodes, timestamp)
                _raw_sql_execute(cursor, delete_status % node_fs, process_nodes, timestamp)
                _raw_sql_execute(cursor, delete_data % node_fs, process_nodes, timestamp)
                _raw_sql_execute(cursor, delete_history % node_fs, process_nodes, timestamp)
            if process_nodes_regex:
                _raw_sql_execute(cursor, delete_datasnapshot, [process_nodes_regex], timestamp)
                _raw_sql_execute(cursor, delete_schedule_celery_task, [process_nodes_regex], timestamp)
            if history_data_ids:
                history_fs = _sql_format_strings(history_data_ids)
                _raw_sql_execute(cursor, delete_history_data % history_fs, history_data_ids, timestamp)
            _raw_sql_execute(cursor, delete_pipeline_process, [instance_id], timestamp)
            PipelineInstance.objects.filter(instance_id=instance_id).update(is_expired=True)


def _sql_log(sql, params, timestamp):
    if isinstance(params, list):
        logger.info("[execute raw sql]: {}, timestamp: {}".format(sql % tuple(params), timestamp))
    else:
        logger.info("[execute raw sql]: {}, timestamp: {}".format(sql % params, timestamp))


def _sql_format_strings(list_data):
    return ",".join(["%s"] * len(list_data))


def _raw_sql_execute(cursor, sql, params, timestamp):
    _sql_log(sql, params, timestamp)
    cursor.execute(sql, params)
