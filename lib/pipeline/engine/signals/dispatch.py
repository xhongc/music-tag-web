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

import traceback

from django.utils.module_loading import import_string

from pipeline.conf import settings
from pipeline.core.flow.activity import ServiceActivity
from pipeline.core.pipeline import Pipeline
from pipeline.engine import models, signals
from pipeline.engine.exceptions import InvalidPipelineEndHandleError
from pipeline.engine.signals import handlers

try:
    end_handler = import_string(settings.PIPELINE_END_HANDLER)
except ImportError:
    raise InvalidPipelineEndHandleError(
        "pipeline end handler ({}) import error with exception: {}".format(
            settings.PIPELINE_END_HANDLER, traceback.format_exc()
        )
    )


# DISPATCH_UID = __name__.replace('.', '_')


def dispatch_pipeline_ready():
    signals.pipeline_ready.connect(handlers.pipeline_ready_handler, sender=Pipeline, dispatch_uid="_pipeline_ready")


def dispatch_pipeline_end():
    signals.pipeline_end.connect(end_handler, sender=Pipeline, dispatch_uid="_pipeline_end")


def dispatch_child_process_ready():
    signals.child_process_ready.connect(
        handlers.child_process_ready_handler, sender=models.PipelineProcess, dispatch_uid="_child_process_ready"
    )


def dispatch_process_ready():
    signals.process_ready.connect(
        handlers.process_ready_handler, sender=models.PipelineProcess, dispatch_uid="_process_ready"
    )


def dispatch_batch_process_ready():
    signals.batch_process_ready.connect(
        handlers.batch_process_ready_handler, sender=models.PipelineProcess, dispatch_uid="_batch_process_ready"
    )


def dispatch_wake_from_schedule():
    signals.wake_from_schedule.connect(
        handlers.wake_from_schedule_handler, sender=models.ScheduleService, dispatch_uid="_wake_from_schedule"
    )


def dispatch_schedule_ready():
    signals.schedule_ready.connect(
        handlers.schedule_ready_handler, sender=models.ScheduleService, dispatch_uid="_schedule_ready"
    )


def dispatch_process_unfreeze():
    signals.process_unfreeze.connect(
        handlers.process_unfreeze_handler, sender=models.PipelineProcess, dispatch_uid="_process_unfreeze"
    )


def dispatch_service_activity_timeout_monitor_start():
    signals.service_activity_timeout_monitor_start.connect(
        handlers.service_activity_timeout_monitor_start_handler,
        sender=ServiceActivity,
        dispatch_uid="_service_activity_timeout_monitor_start",
    )


def dispatch_service_activity_timeout_monitor_end():
    signals.service_activity_timeout_monitor_end.connect(
        handlers.service_activity_timeout_monitor_end_handler,
        sender=ServiceActivity,
        dispatch_uid="__service_activity_timeout_monitor_end",
    )


def dispatch():
    dispatch_pipeline_ready()
    dispatch_pipeline_end()
    dispatch_child_process_ready()
    dispatch_process_ready()
    dispatch_batch_process_ready()
    dispatch_wake_from_schedule()
    dispatch_schedule_ready()
    dispatch_process_unfreeze()
    dispatch_service_activity_timeout_monitor_start()
    dispatch_service_activity_timeout_monitor_end()
