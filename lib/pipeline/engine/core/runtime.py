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

from pipeline.conf import settings as pipeline_settings
from pipeline.core.flow.activity import SubProcess
from pipeline.engine import states
from pipeline.engine.core import context
from pipeline.engine.core.handlers import HandlersFactory
from pipeline.engine.models import NAME_MAX_LENGTH, FunctionSwitch, NodeRelationship, Status

logger = logging.getLogger("pipeline_engine")
celery_logger = logging.getLogger("celery")

RERUN_MAX_LIMIT = pipeline_settings.PIPELINE_RERUN_MAX_TIMES


@contextlib.contextmanager
def runtime_exception_handler(process):
    try:
        yield
    except Exception as e:
        logger.error(traceback.format_exc())
        process.exit_gracefully(e)


def run_loop(process):
    """
    pipeline 推进主循环
    :param process: 当前进程
    :return:
    """
    with runtime_exception_handler(process):
        while True:

            current_node = process.top_pipeline.node(process.current_node_id)
            celery_logger.info(
                "[pipeline-trace](root_pipeline: %s) execute node %s" % (process.root_pipeline_id, current_node.id)
            )

            # check child process destination
            if process.destination_id == current_node.id:
                try:
                    process.destroy_and_wake_up_parent(current_node.id)
                except Exception:
                    logger.error(traceback.format_exc())
                logger.info("child process(%s) finish." % process.id)
                return

            # check root pipeline status
            need_sleep, pipeline_state = process.root_sleep_check()
            if need_sleep:
                logger.info("pipeline(%s) turn to sleep." % process.root_pipeline.id)
                process.sleep(do_not_save=(pipeline_state == states.REVOKED))
                return

            # check subprocess status
            need_sleep, subproc_above = process.subproc_sleep_check()
            if need_sleep:
                logger.info("process(%s) turn to sleep." % process.root_pipeline.id)
                process.sleep(adjust_status=True, adjust_scope=subproc_above)
                return

            # check engine status
            if FunctionSwitch.objects.is_frozen():
                logger.info("pipeline(%s) have been frozen." % process.id)
                process.freeze()
                return

                # try to transit current node to running state
            name = (current_node.name or str(current_node.__class__))[:NAME_MAX_LENGTH]
            action = Status.objects.transit(id=current_node.id, to_state=states.RUNNING, start=True, name=name)

            # check rerun limit
            if (
                not isinstance(current_node, SubProcess)
                and RERUN_MAX_LIMIT != 0
                and action.extra.loop > RERUN_MAX_LIMIT
            ):
                logger.info(
                    "node({nid}) rerun times exceed max limit: {limit}".format(
                        nid=current_node.id, limit=RERUN_MAX_LIMIT
                    )
                )

                # fail
                action = Status.objects.fail(
                    current_node, "rerun times exceed max limit: {limit}".format(limit=RERUN_MAX_LIMIT)
                )

                if not action.result:
                    logger.warning(
                        "can not transit node({}) to running, pipeline({}) turn to sleep. "
                        "message: {}".format(current_node.id, process.root_pipeline.id, action.message)
                    )

                process.sleep(adjust_status=True)
                return

            if not action.result:
                logger.warning(
                    "can not transit node({}) to running, pipeline({}) turn to sleep. message: {}".format(
                        current_node.id, process.root_pipeline.id, action.message
                    )
                )
                process.sleep(adjust_status=True)
                return

            # refresh current node
            process.refresh_current_node(current_node.id)

            # build relationship
            NodeRelationship.objects.build_relationship(process.top_pipeline.id, current_node.id)
            # set up context
            context.set_node_id(current_node.id)

            result = HandlersFactory.handlers_for(current_node)(process, current_node, action.extra)

            if result.should_return or result.should_sleep:
                if result.should_sleep:
                    process.sleep(adjust_status=True)
                    if result.after_sleep_call:
                        result.after_sleep_call(*result.args, **result.kwargs)
                return

            # store current node id
            process.current_node_id = result.next_node.id
