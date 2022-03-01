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

import datetime
import logging
import traceback

import pytz
from celery import task
from django.utils import timezone
from django.utils.module_loading import import_string
from bamboo_engine import api as bamboo_engine_api

from pipeline.contrib.periodic_task import signals
from pipeline.contrib.periodic_task.models import PeriodicTask, PeriodicTaskHistory
from pipeline.engine.models import FunctionSwitch
from pipeline.models import PipelineInstance
from pipeline.parser.context import get_pipeline_context
from pipeline.eri.runtime import BambooDjangoRuntime
from pipeline.contrib.periodic_task.context import (
    get_periodic_task_root_pipeline_context,
    get_periodic_task_subprocess_context,
)

logger = logging.getLogger("celery")


@task(ignore_result=True)
def periodic_task_start(*args, **kwargs):
    try:
        periodic_task = PeriodicTask.objects.get(id=kwargs["period_task_id"])
    except PeriodicTask.DoesNotExist:
        # task has been deleted
        return

    if FunctionSwitch.objects.is_frozen():
        PeriodicTaskHistory.objects.record_schedule(
            periodic_task=periodic_task,
            pipeline_instance=None,
            ex_data="engine is frozen, can not start task",
            start_success=False,
        )
        return

    try:
        tz = periodic_task.celery_task.crontab.timezone
        now = datetime.datetime.now(tz=pytz.utc).astimezone(tz)
        instance, _ = PipelineInstance.objects.create_instance(
            template=periodic_task.template,
            exec_data=periodic_task.execution_data,
            spread=kwargs.get("spread", True),
            name="{}_{}".format(periodic_task.name[:113], now.strftime("%Y%m%d%H%M%S")),
            creator=periodic_task.creator,
            description="periodic task instance",
        )

        signals.pre_periodic_task_start.send(
            sender=PeriodicTask, periodic_task=periodic_task, pipeline_instance=instance
        )

        result = instance.start(
            periodic_task.creator, check_workers=False, priority=periodic_task.priority, queue=periodic_task.queue,
        )
    except Exception:
        et = traceback.format_exc()
        logger.error(et)
        PeriodicTaskHistory.objects.record_schedule(
            periodic_task=periodic_task, pipeline_instance=None, ex_data=et, start_success=False,
        )
        return

    if not result.result:
        PeriodicTaskHistory.objects.record_schedule(
            periodic_task=periodic_task, pipeline_instance=None, ex_data=result.message, start_success=False,
        )
        return

    periodic_task.total_run_count += 1
    periodic_task.last_run_at = timezone.now()
    periodic_task.save()
    signals.post_periodic_task_start.send(sender=PeriodicTask, periodic_task=periodic_task, pipeline_instance=instance)

    PeriodicTaskHistory.objects.record_schedule(periodic_task=periodic_task, pipeline_instance=instance, ex_data="")


@task(ignore_result=True)
def bamboo_engine_periodic_task_start(*args, **kwargs):
    try:
        periodic_task = PeriodicTask.objects.get(id=kwargs["period_task_id"])
    except PeriodicTask.DoesNotExist:
        # task has been deleted
        return

    try:
        tz = periodic_task.celery_task.crontab.timezone
        now = datetime.datetime.now(tz=pytz.utc).astimezone(tz)
        instance, _ = PipelineInstance.objects.create_instance(
            template=periodic_task.template,
            exec_data=periodic_task.execution_data,
            spread=kwargs.get("spread", True),
            name="{}_{}".format(periodic_task.name[:113], now.strftime("%Y%m%d%H%M%S")),
            creator=periodic_task.creator,
            description="periodic task instance",
        )

        signals.pre_periodic_task_start.send(
            sender=PeriodicTask, periodic_task=periodic_task, pipeline_instance=instance
        )

        # convert web pipeline to pipeline
        pipeline_formator = import_string(periodic_task.extra_info["pipeline_formator"])
        pipeline = pipeline_formator(instance.execution_data)

        # run pipeline
        instance.calculate_tree_info()
        PipelineInstance.objects.filter(instance_id=instance.instance_id).update(
            tree_info_id=instance.tree_info.id,
            start_time=timezone.now(),
            is_started=True,
            executor=periodic_task.creator,
        )
        root_pipeline_data = get_pipeline_context(
            instance, obj_type="instance", data_type="data", username=periodic_task.creator
        )
        root_pipeline_context = get_periodic_task_root_pipeline_context(root_pipeline_data)
        subprocess_context = get_periodic_task_subprocess_context(root_pipeline_data)
        result = bamboo_engine_api.run_pipeline(
            runtime=BambooDjangoRuntime(),
            pipeline=pipeline,
            root_pipeline_data=root_pipeline_data,
            root_pipeline_context=root_pipeline_context,
            subprocess_context=subprocess_context,
            queue=periodic_task.queue,
            cycle_tolerate=True,
        )
    except Exception:
        et = traceback.format_exc()
        logger.error(et)
        PeriodicTaskHistory.objects.record_schedule(
            periodic_task=periodic_task, pipeline_instance=None, ex_data=et, start_success=False,
        )
        return

    if not result.result:
        PipelineInstance.objects.filter(id=instance.instance_id).update(
            start_time=None, is_started=False, executor="",
        )
        PeriodicTaskHistory.objects.record_schedule(
            periodic_task=periodic_task, pipeline_instance=None, ex_data=result.message, start_success=False,
        )
        return

    periodic_task.total_run_count += 1
    periodic_task.last_run_at = timezone.now()
    periodic_task.save()
    signals.post_periodic_task_start.send(sender=PeriodicTask, periodic_task=periodic_task, pipeline_instance=instance)

    PeriodicTaskHistory.objects.record_schedule(periodic_task=periodic_task, pipeline_instance=instance, ex_data="")
