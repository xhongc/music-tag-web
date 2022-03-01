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
import traceback

from pipeline.conf import default_settings
from pipeline.core.data.hydration import hydrate_node_data
from pipeline.core.flow.activity import ServiceActivity
from pipeline.django_signal_valve import valve
from pipeline.engine import signals
from pipeline.engine.models import Data, ScheduleService, Status

from .base import FlowElementHandler

logger = logging.getLogger("pipeline_engine")

__all__ = ["ServiceActivityHandler"]


class ServiceActivityHandler(FlowElementHandler):
    @staticmethod
    def element_cls():
        return ServiceActivity

    def handle(self, process, element, status):
        pre_execute_success = False
        success = False
        exception_occurred = False
        monitoring = False
        version = status.version
        root_pipeline = process.root_pipeline

        # rerun mode
        if status.loop > 1 and not element.on_retry():
            element.prepare_rerun_data()
            process.top_pipeline.context.recover_variable()

        elif element.on_retry():
            element.retry_at_current_exec()

        # set loop to data
        element.data.inputs._loop = status.loop + default_settings.PIPELINE_RERUN_INDEX_OFFSET
        element.data.outputs._loop = status.loop + default_settings.PIPELINE_RERUN_INDEX_OFFSET

        # pre output extract
        process.top_pipeline.context.extract_output(element, set_miss=False)

        # hydrate inputs
        hydrate_node_data(element)

        if element.timeout:
            logger.info("node {} {} start timeout monitor, timeout: {}".format(element.id, version, element.timeout))
            signals.service_activity_timeout_monitor_start.send(
                sender=element.__class__,
                node_id=element.id,
                version=version,
                root_pipeline_id=root_pipeline.id,
                countdown=element.timeout,
            )
            monitoring = True

        element.setup_runtime_attrs(
            id=element.id, root_pipeline_id=root_pipeline.id,
        )

        # pre_process inputs and execute service
        try:
            pre_execute_success = element.execute_pre_process(root_pipeline.data)
            if pre_execute_success:
                success = element.execute(root_pipeline.data)
        except Exception:
            if element.error_ignorable:
                # ignore exception
                pre_execute_success = True
                success = True
                exception_occurred = True
                element.ignore_error()
            ex_data = traceback.format_exc()
            element.data.outputs.ex_data = ex_data
            logger.error(ex_data)

        # process result
        if pre_execute_success is False or success is False:
            ex_data = element.data.get_one_of_outputs("ex_data")
            Status.objects.fail(element, ex_data)
            try:
                element.failure_handler(root_pipeline.data)
            except Exception:
                logger.error("failure_handler({}) failed: {}".format(element.id, traceback.format_exc()))

            if monitoring:
                signals.service_activity_timeout_monitor_end.send(
                    sender=element.__class__, node_id=element.id, version=version
                )
                logger.info("node {} {} timeout monitor revoke".format(element.id, version))

            # send activity error signal
            valve.send(
                signals,
                "activity_failed",
                sender=root_pipeline,
                pipeline_id=root_pipeline.id,
                pipeline_activity_id=element.id,
                subprocess_id_stack=process.subprocess_stack,
            )

            return self.HandleResult(next_node=None, should_return=False, should_sleep=True)
        else:
            is_error_ignored = element.error_ignorable and not element.get_result_bit()
            if element.need_schedule() and not exception_occurred and not is_error_ignored:
                # write data before schedule
                Data.objects.write_node_data(element)
                return self.HandleResult(
                    next_node=None,
                    should_return=True,
                    should_sleep=True,
                    after_sleep_call=ScheduleService.objects.set_schedule,
                    args=[],
                    kwargs=dict(
                        activity_id=element.id,
                        service_act=element.shell(),
                        process_id=process.id,
                        version=version,
                        parent_data=process.top_pipeline.data,
                    ),
                )

            process.top_pipeline.context.extract_output(element)
            error_ignorable = not element.get_result_bit()

            if monitoring:
                signals.service_activity_timeout_monitor_end.send(
                    sender=element.__class__, node_id=element.id, version=version
                )
                logger.info("node {} {} timeout monitor revoke".format(element.id, version))

            if not Status.objects.finish(element, error_ignorable):
                # has been forced failed
                return self.HandleResult(next_node=None, should_return=False, should_sleep=True)
            return self.HandleResult(next_node=element.next(), should_return=False, should_sleep=False)
