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

import logging
import contextlib

from pipeline.celery.settings import QueueResolver
from pipeline.engine import tasks, exceptions
from pipeline.engine.models import (
    NodeCeleryTask,
    PipelineModel,
    PipelineProcess,
    ProcessCeleryTask,
    ScheduleCeleryTask,
    SendFailedCeleryTask,
)

logger = logging.getLogger("root")


@contextlib.contextmanager
def celery_task_send_fail_pass():
    try:
        yield
    except exceptions.CeleryFailedTaskCatchException as e:
        # we catch CeleryFailedTaskCatchException here and ignore it.
        # so we can process the fail task in SendFailedCeleryTask
        logger.exception("{} task send error.".format(e.task_name))


class CeleryTaskArgsResolver(object):
    def __init__(self, process_id):
        self.process_id = process_id

    def resolve_args(self, task):
        args = {}
        task_args = PipelineProcess.objects.task_args_for_process(self.process_id)

        queue = task_args["queue"]
        priority = task_args["priority"]

        args["priority"] = priority

        if queue:
            queue_resolver = QueueResolver(queue)
            args["routing_key"] = queue_resolver.resolve_task_routing_key(task)
            args["queue"] = queue_resolver.resolve_task_queue_name(task)

        return args


def pipeline_ready_handler(sender, process_id, **kwargs):
    task = tasks.start
    args_resolver = CeleryTaskArgsResolver(process_id)

    with celery_task_send_fail_pass():
        ProcessCeleryTask.objects.start_task(
            process_id=process_id, task=task, kwargs={"args": [process_id], **args_resolver.resolve_args(task)},
        )


def pipeline_end_handler(sender, root_pipeline_id, **kwargs):
    pass


def child_process_ready_handler(sender, child_id, **kwargs):
    task = tasks.dispatch
    args_resolver = CeleryTaskArgsResolver(child_id)

    with celery_task_send_fail_pass():
        ProcessCeleryTask.objects.start_task(
            process_id=child_id, task=task, kwargs={"args": [child_id], **args_resolver.resolve_args(task)},
        )


def process_ready_handler(sender, process_id, current_node_id=None, call_from_child=False, **kwargs):

    task = tasks.process_wake_up
    args_resolver = CeleryTaskArgsResolver(process_id)

    with celery_task_send_fail_pass():
        ProcessCeleryTask.objects.start_task(
            process_id=process_id,
            task=task,
            kwargs={"args": [process_id, current_node_id, call_from_child], **args_resolver.resolve_args(task)},
        )


def batch_process_ready_handler(sender, process_id_list, pipeline_id, **kwargs):

    task = tasks.batch_wake_up
    task_args = PipelineModel.objects.task_args_for_pipeline(pipeline_id)
    priority = task_args["priority"]
    queue = task_args["queue"]

    kwargs = {
        "args": [process_id_list, pipeline_id],
        "priority": priority,
    }
    if queue:
        kwargs["routing_key"] = QueueResolver(queue).resolve_task_routing_key(task)

    with celery_task_send_fail_pass():
        with SendFailedCeleryTask.watch(
            name=task.name, kwargs=kwargs, type=SendFailedCeleryTask.TASK_TYPE_EMPTY, extra_kwargs={},
        ):
            task.apply_async(**kwargs)


def wake_from_schedule_handler(sender, process_id, activity_id, **kwargs):

    task = tasks.wake_from_schedule
    args_resolver = CeleryTaskArgsResolver(process_id)

    with celery_task_send_fail_pass():
        ProcessCeleryTask.objects.start_task(
            process_id=process_id,
            task=task,
            kwargs={"args": [process_id, activity_id], **args_resolver.resolve_args(task)},
        )


def process_unfreeze_handler(sender, process_id, **kwargs):
    task = tasks.process_unfreeze
    args_resolver = CeleryTaskArgsResolver(process_id)

    with celery_task_send_fail_pass():
        ProcessCeleryTask.objects.start_task(
            process_id=process_id, task=task, kwargs={"args": [process_id], **args_resolver.resolve_args(task)},
        )


def schedule_ready_handler(sender, process_id, schedule_id, countdown, data_id=None, **kwargs):
    task = tasks.service_schedule
    args_resolver = CeleryTaskArgsResolver(process_id)

    with celery_task_send_fail_pass():
        ScheduleCeleryTask.objects.start_task(
            schedule_id=schedule_id,
            task=task,
            kwargs={
                "args": [process_id, schedule_id, data_id],
                "countdown": countdown,
                **args_resolver.resolve_args(task),
            },
        )


def service_activity_timeout_monitor_start_handler(sender, node_id, version, root_pipeline_id, countdown, **kwargs):
    NodeCeleryTask.objects.start_task(
        node_id=node_id,
        task=tasks.node_timeout_check,
        kwargs={
            "args": [node_id, version, root_pipeline_id],
            "countdown": countdown,
            "priority": PipelineModel.objects.priority_for_pipeline(root_pipeline_id),
        },
    )


def service_activity_timeout_monitor_end_handler(sender, node_id, version, **kwargs):
    NodeCeleryTask.objects.revoke(node_id)
