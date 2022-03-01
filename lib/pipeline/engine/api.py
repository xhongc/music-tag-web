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

import functools
import logging
import time
import traceback

from celery import current_app
from django.db import transaction
from redis.exceptions import ConnectionError as RedisConnectionError

from pipeline.celery.queues import ScalableQueues
from pipeline.constants import PIPELINE_DEFAULT_PRIORITY, PIPELINE_MAX_PRIORITY, PIPELINE_MIN_PRIORITY
from pipeline.core.flow.activity import ServiceActivity
from pipeline.core.flow.gateway import ExclusiveGateway, ParallelGateway, ConditionalParallelGateway
from pipeline.engine import exceptions, states
from pipeline.engine.core.api import workers
from pipeline.engine.models import (
    Data,
    FunctionSwitch,
    History,
    NodeRelationship,
    Pipeline,
    PipelineModel,
    PipelineProcess,
    ProcessCeleryTask,
    ScheduleService,
    Status,
    SubProcessRelationship,
)
from pipeline.engine.signals import pipeline_revoke
from pipeline.engine.utils import ActionResult, calculate_elapsed_time
from pipeline.exceptions import PipelineException
from pipeline.utils import uniqid

logger = logging.getLogger("celery")


def _node_existence_check(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        id_from_kwargs = kwargs.get("node_id")
        node_id = id_from_kwargs if id_from_kwargs else args[0]
        try:
            Status.objects.get(id=node_id)
        except Status.DoesNotExist:
            return ActionResult(result=False, message="node not exists or not be executed yet")
        return func(*args, **kwargs)

    return wrapper


def _frozen_check(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if FunctionSwitch.objects.is_frozen():
            return ActionResult(result=False, message="engine is frozen, can not perform operation")

        return func(*args, **kwargs)

    return wrapper


def _worker_check(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        def on_connection_error(exc, interval):
            logger.warning("Connection Error: {!r}. Retry in {}s.".format(exc, interval))

        if kwargs.get("check_workers", True):
            try:
                with current_app.connection() as conn:
                    try:
                        conn.ensure_connection(on_connection_error, current_app.conf.BROKER_CONNECTION_MAX_RETRIES)
                    except conn.connection_errors + conn.channel_errors as exc:
                        logger.warning("Connection lost: {!r}".format(exc))
                    if not workers(conn):
                        return ActionResult(
                            result=False, message="can not find celery workers, please check worker status"
                        )
            except exceptions.RabbitMQConnectionError as e:
                return ActionResult(
                    result=False,
                    message="celery worker status check failed with message: %s, " "check rabbitmq status please" % e,
                )
            except RedisConnectionError:
                return ActionResult(result=False, message="redis connection error, check redis status please")

        return func(*args, **kwargs)

    return wrapper


@_worker_check
@_frozen_check
def start_pipeline(pipeline_instance, check_workers=True, priority=PIPELINE_DEFAULT_PRIORITY, queue=""):
    """
    start a pipeline
    :param pipeline_instance:
    :param priority:
    :return:
    """

    if priority > PIPELINE_MAX_PRIORITY or priority < PIPELINE_MIN_PRIORITY:
        raise exceptions.InvalidOperationException(
            "pipeline priority must between [{min}, {max}]".format(min=PIPELINE_MIN_PRIORITY, max=PIPELINE_MAX_PRIORITY)
        )

    if queue and not ScalableQueues.has_queue(queue):
        return ActionResult(result=False, message="can't not find queue({}) in any config queues.".format(queue))

    Status.objects.prepare_for_pipeline(pipeline_instance)
    process = PipelineProcess.objects.prepare_for_pipeline(pipeline_instance)
    PipelineModel.objects.prepare_for_pipeline(pipeline_instance, process, priority, queue=queue)

    PipelineModel.objects.pipeline_ready(process_id=process.id)

    return ActionResult(result=True, message="success")


@_frozen_check
def pause_pipeline(pipeline_id):
    """
    pause a running pipeline
    :param pipeline_id:
    :return:
    """

    return Status.objects.transit(id=pipeline_id, to_state=states.SUSPENDED, is_pipeline=True, appoint=True)


@_worker_check
@_frozen_check
def resume_pipeline(pipeline_id):
    """
    resume a pipeline from suspended
    :param pipeline_id:
    :return:
    """
    if not Status.objects.filter(id=pipeline_id).exists():
        return ActionResult(result=False, message="only started pipeline can be resumed.")

    action_result = Status.objects.transit(id=pipeline_id, to_state=states.READY, is_pipeline=True, appoint=True)
    if not action_result.result:
        return action_result

    process = PipelineModel.objects.get(id=pipeline_id).process
    to_be_waked = []
    _get_process_to_be_waked(process, to_be_waked)
    PipelineProcess.objects.batch_process_ready(process_id_list=to_be_waked, pipeline_id=pipeline_id)

    return action_result


@_frozen_check
def revoke_pipeline(pipeline_id):
    """
    revoke a pipeline
    :param pipeline_id:
    :return:
    """

    try:
        pipeline_model = PipelineModel.objects.get(id=pipeline_id)
    except PipelineModel.DoesNotExist:
        return ActionResult(result=False, message="pipeline to be revoked does not exist.")

    action_result = Status.objects.transit(id=pipeline_id, to_state=states.REVOKED, is_pipeline=True, appoint=True)
    if not action_result.result:
        return action_result

    process = pipeline_model.process

    if not process:
        return ActionResult(result=False, message="relate process is none, this pipeline may be revoked.")

    with transaction.atomic():
        PipelineProcess.objects.select_for_update().get(id=process.id)
        process.revoke_subprocess()
        process.destroy_all()

    pipeline_revoke.send(sender=Pipeline, root_pipeline_id=pipeline_id)

    return action_result


@_frozen_check
def pause_node_appointment(node_id):
    """
    make a appointment to pause a node
    :param node_id:
    :return:
    """

    return Status.objects.transit(id=node_id, to_state=states.SUSPENDED, appoint=True)


@_worker_check
@_frozen_check
@_node_existence_check
def resume_node_appointment(node_id):
    """
    make a appointment to resume a node
    :param node_id:
    :return:
    """

    qs = PipelineProcess.objects.filter(current_node_id=node_id, is_sleep=True)
    if qs.exists():
        # a process had sleep caused by pause reservation
        action_result = Status.objects.transit(id=node_id, to_state=states.READY, appoint=True)
        if not action_result.result:
            return action_result

        process = qs.first()
        Status.objects.recover_from_block(process.root_pipeline.id, process.subprocess_stack)
        PipelineProcess.objects.process_ready(process_id=process.id)
        return ActionResult(result=True, message="success")

    processing_sleep = SubProcessRelationship.objects.get_relate_process(subprocess_id=node_id)
    if processing_sleep.exists():
        action_result = Status.objects.transit(id=node_id, to_state=states.RUNNING, appoint=True, is_pipeline=True)
        if not action_result.result:
            return action_result
        # processes had sleep caused by subprocess pause
        root_pipeline_id = processing_sleep.first().root_pipeline_id

        process_can_be_waked = [p for p in processing_sleep if p.can_be_waked()]
        can_be_waked_ids = [p.id for p in process_can_be_waked]

        # get subprocess id which should be transited
        subprocess_to_be_transit = set()
        for process in process_can_be_waked:
            _, subproc_above = process.subproc_sleep_check()
            for subproc in subproc_above:
                subprocess_to_be_transit.add(subproc)

        Status.objects.recover_from_block(root_pipeline_id, subprocess_to_be_transit)
        PipelineProcess.objects.batch_process_ready(process_id_list=can_be_waked_ids, pipeline_id=root_pipeline_id)
        return ActionResult(result=True, message="success")

    return ActionResult(result=False, message="node not exists or not be executed yet")


@_worker_check
@_frozen_check
@_node_existence_check
def retry_node(node_id, inputs=None):
    """
    retry a node
    :param node_id:
    :param inputs:
    :return:
    """

    try:
        PipelineProcess.objects.get(current_node_id=node_id)
    except PipelineProcess.DoesNotExist:  # can not retry subprocess
        return ActionResult(result=False, message="can't not retry a subprocess or this process has been revoked")

    process = PipelineProcess.objects.get(current_node_id=node_id)

    # try to get next
    node = process.top_pipeline.node(node_id)
    if not (isinstance(node, ServiceActivity) or isinstance(node, ParallelGateway)):
        return ActionResult(result=False, message="can't retry this type of node")

    if hasattr(node, "retryable") and not node.retryable:
        return ActionResult(result=False, message="the node is set to not be retryable, try skip it please.")

    action_result = Status.objects.retry(process, node, inputs)
    if not action_result.result:
        return action_result

    # wake up process
    PipelineProcess.objects.process_ready(process_id=process.id)

    return action_result


@_worker_check
@_frozen_check
@_node_existence_check
def skip_node(node_id):
    """
    skip a node
    :param node_id:
    :return:
    """

    try:
        process = PipelineProcess.objects.get(current_node_id=node_id)
    except PipelineProcess.DoesNotExist:  # can not skip subprocess
        return ActionResult(result=False, message="can't not skip a subprocess or this process has been revoked")

    # try to get next
    node = process.top_pipeline.node(node_id)
    if not isinstance(node, ServiceActivity):
        return ActionResult(result=False, message="can't skip this type of node")

    if hasattr(node, "skippable") and not node.skippable:
        return ActionResult(result=False, message="this node is set to not be skippable, try retry it please.")

    # skip and write result bit
    action_result = Status.objects.skip(process, node)
    if not action_result.result:
        return action_result

    next_node_id = node.next().id

    # extract outputs and wake up process
    process.top_pipeline.context.extract_output(node)
    process.save()
    PipelineProcess.objects.process_ready(process_id=process.id, current_node_id=next_node_id)

    return action_result


@_worker_check
@_frozen_check
@_node_existence_check
def skip_exclusive_gateway(node_id, flow_id):
    """
    skip a failed exclusive gateway and appoint the flow to be pushed
    :param node_id:
    :param flow_id:
    :return:
    """

    try:
        process = PipelineProcess.objects.get(current_node_id=node_id)
    except PipelineProcess.DoesNotExist:
        return ActionResult(
            result=False, message="invalid operation, this gateway is finished or pipeline have been revoked"
        )

    exclusive_gateway = process.top_pipeline.node(node_id)

    if not isinstance(exclusive_gateway, ExclusiveGateway):
        return ActionResult(result=False, message="invalid operation, this node is not a exclusive gateway")

    next_node_id = exclusive_gateway.target_for_sequence_flow(flow_id).id

    action_result = Status.objects.skip(process, exclusive_gateway)
    if not action_result.result:
        return action_result

    # wake up process
    PipelineProcess.objects.process_ready(process_id=process.id, current_node_id=next_node_id)

    return action_result


@_worker_check
@_frozen_check
@_node_existence_check
def skip_conditional_parallel_gateway(node_id, flow_ids, converge_gateway_id):
    """
    skip a failed conditional parallel gateway and appoint the flow to be pushed
    :param node_id:
    :param flow_ids:
    :param converge_gateway_id:
    :return:
    """

    try:
        process = PipelineProcess.objects.get(current_node_id=node_id)
    except PipelineProcess.DoesNotExist:
        return ActionResult(
            result=False, message="invalid operation, this gateway is finished or pipeline have been revoked"
        )

    if process.children:
        process.clean_children()

    conditional_parallel_gateway = process.top_pipeline.node(node_id)

    if not isinstance(conditional_parallel_gateway, ConditionalParallelGateway):
        return ActionResult(result=False, message="invalid operation, this node is not a conditional parallel gateway")

    children = []
    targets = conditional_parallel_gateway.target_for_sequence_flows(flow_ids)

    for target in targets:
        try:
            child = PipelineProcess.objects.fork_child(
                parent=process, current_node_id=target.id, destination_id=converge_gateway_id
            )
        except PipelineException as e:
            logger.error(traceback.format_exc())
            Status.objects.fail(conditional_parallel_gateway, ex_data=str(e))
            return ActionResult(result=False, message=e)

        children.append(child)

    action_result = Status.objects.skip(process, conditional_parallel_gateway)
    if not action_result.result:
        return action_result

    Status.objects.transit(id=process.top_pipeline.id, to_state=states.RUNNING, is_pipeline=True)
    process.join(children)
    process.sleep(adjust_status=True)

    return action_result


def get_status_tree(node_id, max_depth=1):
    """
    get state and children states for a node
    :param node_id:
    :param max_depth:
    :return:
    """
    rel_qs = NodeRelationship.objects.filter(ancestor_id=node_id, distance__lte=max_depth)
    if not rel_qs.exists():
        raise exceptions.InvalidOperationException(
            "node(%s) does not exist, may have not by executed or expired" % node_id
        )
    descendants = [rel.descendant_id for rel in rel_qs]
    # remove root node
    descendants.remove(node_id)

    rel_qs = NodeRelationship.objects.filter(descendant_id__in=descendants, distance=1)
    targets = [rel.descendant_id for rel in rel_qs]

    root_status = Status.objects.filter(id=node_id).values().first()
    root_status["elapsed_time"] = calculate_elapsed_time(root_status["started_time"], root_status["archived_time"])
    status_map = {node_id: root_status}
    status_qs = Status.objects.filter(id__in=targets).values()
    for status in status_qs:
        status["elapsed_time"] = calculate_elapsed_time(status["started_time"], status["archived_time"])
        status_map[status["id"]] = status

    relationships = [(s.ancestor_id, s.descendant_id) for s in rel_qs]
    for (parent_id, child_id) in relationships:
        if parent_id not in status_map:
            return

        parent_status = status_map[parent_id]
        child_status = status_map[child_id]
        child_status.setdefault("children", {})

        parent_status.setdefault("children", {}).setdefault(child_id, child_status)

    return status_map[node_id]


@_worker_check
@_frozen_check
def activity_callback(activity_id, callback_data):
    """
    callback a schedule node
    :param activity_id:
    :param callback_data:
    :return:
    """

    version = Status.objects.version_for(activity_id)
    times = 0

    # it's possible that ScheduleService is not be set when callback make
    while times < 3:
        try:
            service = ScheduleService.objects.schedule_for(activity_id, version)
            break
        except ScheduleService.DoesNotExist as e:
            times += 1
            time.sleep(times)
            if times >= 3:
                raise e

    try:
        process_id = PipelineProcess.objects.get(current_node_id=activity_id).id
    except PipelineProcess.DoesNotExist:
        return ActionResult(
            result=False, message="invalid operation, this node is finished or pipeline have been revoked"
        )

    if service.is_finished:
        raise exceptions.InvalidOperationException("activity(%s) callback already finished" % activity_id)
    service.callback(callback_data, process_id)
    return ActionResult(result=True, message="success")


def get_inputs(node_id):
    """
    get inputs data for a node
    :param node_id:
    :return:
    """
    return Data.objects.get(id=node_id).inputs


def get_outputs(node_id):
    """
    get outputs data for a node
    :param node_id:
    :return:
    """
    data = Data.objects.get(id=node_id)
    return {"outputs": data.outputs, "ex_data": data.ex_data}


def get_batch_outputs(node_ids):
    """
    get outputs data for a batch of nodes
    :param node_ids: a list of node_id
    :return:
    """
    nodes_data = Data.objects.filter(id__in=node_ids)
    return {node_data.id: {"outputs": node_data.outputs, "ex_data": node_data.ex_data} for node_data in nodes_data}


def get_activity_histories(node_id, loop=None):
    """
    get get_activity_histories data for a node
    :param node_id: 节点 ID
    :param loop: 循环序号
    :return:
    """
    return History.objects.get_histories(node_id, loop)


@_frozen_check
@_node_existence_check
def forced_fail(node_id, kill=False, ex_data=""):
    """
    forced fail a node
    :param node_id:
    :param kill:
    :param ex_data:
    :return:
    """

    try:
        process = PipelineProcess.objects.get(current_node_id=node_id)
    except PipelineProcess.DoesNotExist:
        return ActionResult(
            result=False, message="invalid operation, this node is finished or pipeline have been revoked"
        )

    node = process.top_pipeline.node(node_id)
    if not isinstance(node, ServiceActivity):
        return ActionResult(result=False, message="can't not forced fail this type of node")

    action_result = Status.objects.transit(node_id, to_state=states.FAILED)
    if not action_result.result:
        return action_result

    try:
        node.failure_handler(process.root_pipeline.data)
    except Exception:
        pass

    with transaction.atomic():
        s = Status.objects.get(id=node.id)
        ScheduleService.objects.delete_schedule(s.id, s.version)
        Data.objects.forced_fail(node_id, ex_data)
        ProcessCeleryTask.objects.revoke(process.id, kill)
        process.adjust_status()
        process.is_sleep = True
        process.save()
        s.version = uniqid.uniqid()
        s.save()

    return ActionResult(result=True, message="success")


def _get_process_to_be_waked(process, to_be_waked):
    if process.can_be_waked():
        to_be_waked.append(process.id)
    elif process.children:
        for child_id in process.children:
            child = PipelineProcess.objects.get(id=child_id)
            _get_process_to_be_waked(child, to_be_waked)
