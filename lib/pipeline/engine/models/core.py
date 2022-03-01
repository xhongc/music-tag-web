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

import ujson as json
import contextlib
import logging
import traceback

from celery import current_app
from celery.task.control import revoke
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from pipeline.conf import settings as pipeline_settings
from pipeline.constants import PIPELINE_DEFAULT_PRIORITY
from pipeline.core.data.base import DataObject
from pipeline.core.pipeline import Pipeline
from pipeline.django_signal_valve import valve
from pipeline.engine import exceptions, signals, states, utils
from pipeline.engine.core import data as data_service
from pipeline.engine.models.fields import IOField
from pipeline.engine.utils import ActionResult, Stack, calculate_elapsed_time
from pipeline.log.models import LogEntry
from pipeline.utils.uniqid import node_uniqid, uniqid

logger = logging.getLogger("celery")

RERUN_MAX_LIMIT = pipeline_settings.PIPELINE_RERUN_MAX_TIMES
NAME_MAX_LENGTH = 64


class ProcessSnapshotManager(models.Manager):
    def create_snapshot(self, pipeline_stack, children, root_pipeline, subprocess_stack):
        data = {
            "_pipeline_stack": pipeline_stack,
            "_subprocess_stack": subprocess_stack,
            "_children": children,
            "_root_pipeline": root_pipeline,
        }
        return self.create(data=data)


class ProcessSnapshot(models.Model):
    id = models.BigAutoField(_("ID"), primary_key=True)
    data = IOField(verbose_name=_("pipeline 运行时数据"))

    objects = ProcessSnapshotManager()

    @property
    def pipeline_stack(self):
        return self.data["_pipeline_stack"]

    @property
    def children(self):
        return self.data["_children"]

    @property
    def root_pipeline(self):
        return self.data["_root_pipeline"]

    @property
    def subprocess_stack(self):
        return self.data["_subprocess_stack"]

    def clean_children(self):
        self.data["_children"] = []

    def prune_top_pipeline(self, keep_from, keep_to):
        self.data["_pipeline_stack"].top().prune(keep_from, keep_to)


class ProcessManager(models.Manager):
    def prepare_for_pipeline(self, pipeline):
        """
        为 pipeline 创建相应的 process 并进行一系列初始化
        :param pipeline:
        :return:
        """
        # init runtime info
        snapshot = ProcessSnapshot.objects.create_snapshot(
            pipeline_stack=utils.Stack(), children=[], root_pipeline=pipeline, subprocess_stack=utils.Stack(),
        )
        process = self.create(
            id=node_uniqid(), root_pipeline_id=pipeline.id, current_node_id=pipeline.start_event.id, snapshot=snapshot,
        )
        process.push_pipeline(pipeline)
        process.save()
        return process

    def fork_child(self, parent, current_node_id, destination_id):
        """
        创建一个上下文信息与当前 parent 一致的 child process
        :param parent:
        :param current_node_id:
        :param destination_id:
        :return:
        """
        # init runtime info
        pipeline_stack = Stack([parent.top_pipeline])
        root_pipeline_shell = parent.root_pipeline.shell()
        snapshot = ProcessSnapshot.objects.create_snapshot(
            pipeline_stack=pipeline_stack,
            children=[],
            root_pipeline=root_pipeline_shell,
            subprocess_stack=parent.subprocess_stack,
        )
        # refresh first, avoid keep the same ref to parent.top_pipeline
        snapshot.refresh_from_db()
        snapshot.prune_top_pipeline(current_node_id, destination_id)
        snapshot.save()
        # clear parent's change
        snapshot.pipeline_stack.top().context.clear_change_keys()

        child = self.create(
            id=node_uniqid(),
            root_pipeline_id=parent.root_pipeline.id,
            current_node_id=current_node_id,
            destination_id=destination_id,
            parent_id=parent.id,
            snapshot=snapshot,
        )
        for subproc_id in parent.subprocess_stack:
            SubProcessRelationship.objects.add_relation(subproc_id, child.id)

        return child

    def process_ready(self, process_id, current_node_id=None, call_from_child=False):
        """
        发送一个进程已经准备好被调度的信号
        :param process_id: 已经准备好的进程 ID
        :param current_node_id: 下一个执行的节点的 ID（可用于失败跳过）
        :param call_from_child: 该信号是否由子进程发出
        :return:
        """
        valve.send(
            signals,
            "process_ready",
            sender=PipelineProcess,
            process_id=process_id,
            current_node_id=current_node_id,
            call_from_child=call_from_child,
        )

    def batch_process_ready(self, process_id_list, pipeline_id):
        """
        发送批量唤醒进程的信号
        :param process_id_list: 需要被唤醒的进程 ID 列表
        :param pipeline_id: 这些进程相关的 root pipeline
        :return:
        """
        valve.send(
            signals,
            "batch_process_ready",
            sender=PipelineProcess,
            process_id_list=process_id_list,
            pipeline_id=pipeline_id,
        )

    def child_process_ready(self, child_id):
        """
        发送子进程已经准备好被调度的信号
        :param child_id: 子进程 ID
        :return:
        """
        valve.send(signals, "child_process_ready", sender=PipelineProcess, child_id=child_id)

    def priority_for_process(self, process_id):
        """
        查询进程对应的 pipeline 的优先级
        :param process_id: 进程 ID
        :return:
        """
        return PipelineModel.objects.get(id=self.get(id=process_id).root_pipeline_id).priority

    def queue_for_process(self, process_id):
        """
        查询进程对应的 pipeline 所使用的队列
        :param process_id: 进程 ID
        :return:
        """
        return PipelineModel.objects.get(id=self.get(id=process_id).root_pipeline_id).queue

    def task_args_for_process(self, process_id):
        pipeline_model = PipelineModel.objects.get(id=self.get(id=process_id).root_pipeline_id)

        return {"priority": pipeline_model.priority, "queue": pipeline_model.queue}


class PipelineProcess(models.Model):
    """
    @relationship with other models
        1. PipelineInstance
            process = PipelineProcess.objects.get(root_pipeline_id=pipeline_inst.instance_id)
            pipeline_inst = PipelineInstance.objects.get(instance_id=process.root_pipeline_id)
    """

    id = models.CharField(_("Process ID"), unique=True, primary_key=True, max_length=32)
    root_pipeline_id = models.CharField(_("根 pipeline 的 ID"), max_length=32, db_index=True)
    current_node_id = models.CharField(_("当前推进到的节点的 ID"), max_length=32, default="", db_index=True)
    destination_id = models.CharField(_("遇到该 ID 的节点就停止推进"), max_length=32, default="")
    parent_id = models.CharField(_("父 process 的 ID"), max_length=32, default="", db_index=True)
    ack_num = models.IntegerField(_("收到子节点 ACK 的数量"), default=0)
    need_ack = models.IntegerField(_("需要收到的子节点 ACK 的数量"), default=-1)
    is_alive = models.BooleanField(_("该 process 是否还有效"), default=True, db_index=True)
    is_sleep = models.BooleanField(_("该 process 是否正在休眠"), default=False, db_index=True)
    is_frozen = models.BooleanField(_("该 process 是否被冻结"), default=False, db_index=True)
    snapshot = models.ForeignKey(ProcessSnapshot, null=True, on_delete=models.SET_NULL)

    objects = ProcessManager()

    @property
    def pipeline_stack(self):
        return self.snapshot.pipeline_stack if self.snapshot else None

    @property
    def children(self):
        return self.snapshot.children if self.snapshot else None

    @property
    def root_pipeline(self):
        return self.snapshot.root_pipeline if self.snapshot else None

    @property
    def top_pipeline(self):
        return self.pipeline_stack.top()

    @property
    def subprocess_stack(self):
        return self.snapshot.subprocess_stack if self.snapshot else None

    @property
    def in_subprocess(self):
        return len(self.snapshot.pipeline_stack) > 1 if self.snapshot else False

    def push_pipeline(self, pipeline, is_subprocess=False):
        """
        将 pipeline 压入运行时栈中
        :param pipeline: 需要被压入栈中的 pipeline 对象
        :param is_subprocess: 该 pipeline 是否是子流程
        :return:
        """
        self.pipeline_stack.push(pipeline)
        if is_subprocess:
            self.subprocess_stack.push(pipeline.id)
            SubProcessRelationship.objects.add_relation(pipeline.id, self.id)

    def pop_pipeline(self):
        """
        从运行时栈中弹出一个 pipeline
        :return:
        """
        pipeline = self.pipeline_stack.pop()
        if self.subprocess_stack:
            subproc_id = self.subprocess_stack.pop()
            SubProcessRelationship.objects.delete_relation(subproc_id, self.id)
        return pipeline

    def join(self, children):
        """
        令父进程等待子进程
        :param children: 需要等待的子进程列表
        :return:
        """
        self.need_ack = len(children)
        for child in children:
            self.children.append(child.id)
        self.save()

    def root_sleep_check(self):
        """
        检测 root pipeline 的状态判断当前进程是否需要休眠
        :return:
        """
        root_state = Status.objects.state_for(self.root_pipeline.id)
        if root_state in states.SLEEP_STATES:
            return True, root_state
        if root_state == states.BLOCKED:
            # 子进程不会因为父进程进入了 BLOCKED 状态就进入睡眠
            return not self.parent_id, root_state
        return False, root_state

    def subproc_sleep_check(self):
        """
        检测当前子流程栈中所有子流程的状态判断当前进程是否需要休眠
        :return:
        """
        status = Status.objects.filter(id__in=self.subprocess_stack)
        status_map = {s.id: s.state for s in status}
        # 记录第一个处于暂停状态之前的所有子流程，用于子流程状态的修改
        before_suspended = []
        for subproc_id in self.subprocess_stack:
            if status_map[subproc_id] == states.SUSPENDED:
                return True, before_suspended
            else:
                before_suspended.append(subproc_id)
        return False, before_suspended

    def freeze(self):
        """
        冻结当前进程
        :return:
        """
        with transaction.atomic():
            self.__class__.objects.select_for_update().get(id=self.id)
            self.is_frozen = True
            self.save()
            ProcessCeleryTask.objects.unbind(self.id)

    def unfreeze(self):
        """
        解冻当前进程
        :return:
        """
        with transaction.atomic():
            self.__class__.objects.select_for_update().get(id=self.id)
            self.is_frozen = False
            self.save(save_snapshot=False)
            valve.send(signals, "process_unfreeze", sender=PipelineProcess, process_id=self.id)

    def sleep(self, do_not_save=False, adjust_status=False, adjust_scope=None):
        """
        休眠当前进程
        :param do_not_save: 是否需要保存进程信息
        :param adjust_status: 是否需要调整 pipeline 中当前节点父级节点的状态
        :param adjust_scope: 状态调整的范围
        :return:
        """
        if adjust_status:
            self.adjust_status(adjust_scope)
        if do_not_save:
            return
        with transaction.atomic():
            self.__class__.objects.select_for_update().get(id=self.id)
            self.is_sleep = True
            self.save()
            ProcessCeleryTask.objects.unbind(self.id)
        # dispatch children
        for child_id in self.children:
            PipelineProcess.objects.child_process_ready(child_id)

    def adjust_status(self, adjust_scope=None):
        """
        根据当前节点和子流程的状态来调整父级节点的状态
        :param adjust_scope: 子流程状态调整范围
        :return:
        """
        node_state = Status.objects.state_for(self.current_node_id, may_not_exist=True)
        pipeline_state = Status.objects.state_for(self.root_pipeline.id, may_not_exist=True)
        subproc_states = Status.objects.states_for(self.subprocess_stack)

        if node_state in {states.FAILED, states.SUSPENDED}:
            # if current node failed or suspended
            Status.objects.batch_transit(
                id_list=self.subprocess_stack, state=states.BLOCKED, from_state=states.RUNNING,
            )
            Status.objects.transit(self.root_pipeline.id, to_state=states.BLOCKED, is_pipeline=True)
        elif states.SUSPENDED in set(subproc_states):
            # if any subprocess suspended
            Status.objects.batch_transit(id_list=adjust_scope, state=states.BLOCKED, from_state=states.RUNNING)
            Status.objects.transit(self.root_pipeline.id, to_state=states.BLOCKED, is_pipeline=True)
        elif pipeline_state == states.SUSPENDED:
            # if root pipeline suspended
            Status.objects.batch_transit(
                id_list=self.subprocess_stack, state=pipeline_state, from_state=states.RUNNING,
            )

    def wake_up(self):
        """
        唤醒当前进程
        :return:
        """
        with transaction.atomic():
            self.__class__.objects.select_for_update().get(id=self.id)
            self.is_sleep = False
            self.save(save_snapshot=False)

    def destroy(self):
        """
        销毁当前进程及其上下文数据
        :return:
        """
        self.is_alive = False
        self.current_node_id = ""
        snapshot = self.snapshot
        self.snapshot = None

        self.save()
        snapshot.delete()
        ProcessCeleryTask.objects.destroy(self.id)

    def destroy_all(self):
        """
        销毁当前进程并递归销毁其所有子进程
        :return:
        """
        _destroy_recursively(self)

    def save(self, save_snapshot=True, **kwargs):
        if save_snapshot and self.snapshot:
            self.snapshot.save()
        return super(PipelineProcess, self).save(**kwargs)

    def blocked_by_failure_or_suspended(self):
        """
        检测当前进程是否因为节点失败而休眠
        :return:
        """
        if not self.is_sleep:
            return False
        if Status.objects.state_for(self.current_node_id, may_not_exist=True) in {
            states.FAILED,
            states.SUSPENDED,
        }:
            return True
        if not self.children:
            return False
        children = self.__class__.objects.filter(id__in=self.children)
        result = []
        for child in children:
            result.append(child.blocked_by_failure_or_suspended())
        return True in result

    def sync_with_children(self):
        """
        与子进程同步数据
        :return:
        """
        for child_id in self.children:
            context = data_service.get_object(self._context_key(child_id))
            parent_data = data_service.get_object(self._data_key(child_id))
            if context is None or parent_data is None:
                raise exceptions.ChildDataSyncError(
                    "sync data with children {} failed, context({}) or parent_data({}) is None".format(
                        child_id, context, parent_data
                    )
                )
            self.top_pipeline.context.sync_change(context)
            # self.top_pipeline.context.update_global_var(context.variables)
            self.top_pipeline.data.update_outputs(parent_data.get_outputs())
        self.clean_children()  # remove all children

    def destroy_and_wake_up_parent(self, destination_id):
        """
        销毁当前进程并尝试唤醒父进程
        :param destination_id: 当前进程终点节点 ID
        :return:
        """
        # save sync data
        data_service.set_object(self._context_key(), self.top_pipeline.context)
        data_service.set_object(self._data_key(), self.top_pipeline.data)

        self.__class__.objects.filter(id=self.parent_id).update(ack_num=models.F("ack_num") + 1)
        can_wake_up = False

        with transaction.atomic():
            parent = self.__class__.objects.select_for_update().get(id=self.parent_id)

            if parent.need_ack != -1:
                if parent.ack_num == parent.need_ack:
                    # try to wake up parent
                    parent.need_ack = -1
                    parent.ack_num = 0
                    can_wake_up = True
                else:
                    if parent.blocked_by_failure_or_suspended():
                        Status.objects.batch_transit(
                            id_list=self.subprocess_stack, state=states.BLOCKED, from_state=states.RUNNING,
                        )
                        Status.objects.transit(
                            id=self.root_pipeline.id, to_state=states.BLOCKED, is_pipeline=True,
                        )

            parent.save(save_snapshot=False)

        if can_wake_up:
            self.__class__.objects.process_ready(parent.id, current_node_id=destination_id, call_from_child=True)

        SubProcessRelationship.objects.delete_relation(None, self.id)
        self.destroy()

    def _context_key(self, process_id=None):
        return "%s_context" % (process_id if process_id else self.id)

    def _data_key(self, process_id=None):
        return "%s_data" % (process_id if process_id else self.id)

    def can_be_waked(self):
        """
        检测当前进程是否能够被唤醒
        :return:
        """
        if not self.is_sleep or not self.is_alive:
            return False
        if self.need_ack != -1 and self.need_ack != self.ack_num:
            return False
        return True

    def clean_children(self):
        """
        清空当前进程的 children
        :return:
        """
        for child_id in self.children:
            # 删除子进程的数据
            data_service.del_object(self._context_key(child_id))
            data_service.del_object(self._data_key(child_id))

        self.snapshot.clean_children()
        self.snapshot.save()

    def exit_gracefully(self, e):
        """
        在遇到无法处理的异常时优雅的退出当前进程
        :param e:
        :return:
        """
        ex_data = traceback.format_exc()
        try:
            current_node = self.top_pipeline.node(self.current_node_id)
        except IndexError:
            current_node = self.root_pipeline.node(self.current_node_id)

        # current_node may be a end_event in pipeline which had been popped
        if current_node is not None:
            result = Status.objects.fail(current_node, ex_data=ex_data)
        else:
            result = Status.objects.raw_fail(self.current_node_id, ex_data=ex_data)

        if not result.result:
            logger.error(
                "process({process_id}) exit_gracefully status transit failed, current_node :{node_id}".format(
                    process_id=self.id, node_id=current_node.id if current_node else self.current_node_id,
                )
            )
        self.sleep(adjust_status=True)

    def refresh_current_node(self, current_node_id):
        """
        刷新当前节点的 ID
        :param current_node_id:
        :return:
        """
        self.__class__.objects.filter(id=self.id).update(current_node_id=current_node_id)

    def revoke_subprocess(self):
        if self.subprocess_stack:
            Status.objects.batch_transit(id_list=list(self.subprocess_stack), state=states.REVOKED)

        if self.children:
            for child_id in self.children:
                PipelineProcess.objects.get(id=child_id).revoke_subprocess()

    def take_snapshot(self):
        """
        保存当前进程的快照对象
        :return:
        """
        self.snapshot.save()


def _destroy_recursively(process):
    if not process.is_alive:
        return
    if process.children:
        for child_id in process.children:
            child = PipelineProcess.objects.get(id=child_id)
            _destroy_recursively(child)
        process.destroy()
    else:
        process.destroy()


class PipelineModelManager(models.Manager):
    def prepare_for_pipeline(self, pipeline, process, priority, queue=""):
        return self.create(id=pipeline.id, process=process, priority=priority, queue=queue)

    def pipeline_ready(self, process_id):
        valve.send(signals, "pipeline_ready", sender=Pipeline, process_id=process_id)

    def priority_for_pipeline(self, pipeline_id):
        return self.get(id=pipeline_id).priority

    def task_args_for_pipeline(self, pipeline_id):
        model = self.get(id=pipeline_id)

        return {"priority": model.priority, "queue": model.queue}


class PipelineModel(models.Model):
    id = models.CharField("pipeline ID", unique=True, primary_key=True, max_length=32)
    process = models.ForeignKey(PipelineProcess, null=True, on_delete=models.SET_NULL)
    priority = models.IntegerField(_("流程优先级"), default=PIPELINE_DEFAULT_PRIORITY)
    queue = models.CharField(_("流程使用的队列名"), max_length=512, default="")

    objects = PipelineModelManager()


class RelationshipManager(models.Manager):
    def build_relationship(self, ancestor_id, descendant_id):
        if self.filter(ancestor_id=ancestor_id, descendant_id=descendant_id).exists():
            # already build
            return
        ancestors = self.filter(descendant_id=ancestor_id)
        relationships = [NodeRelationship(ancestor_id=descendant_id, descendant_id=descendant_id, distance=0)]
        for ancestor in ancestors:
            rel = NodeRelationship(
                ancestor_id=ancestor.ancestor_id, descendant_id=descendant_id, distance=ancestor.distance + 1,
            )
            relationships.append(rel)
        self.bulk_create(relationships)


class NodeRelationship(models.Model):
    id = models.BigAutoField(_("ID"), primary_key=True)
    ancestor_id = models.CharField(_("祖先 ID"), max_length=32, db_index=True)
    descendant_id = models.CharField(_("后代 ID"), max_length=32, db_index=True)
    distance = models.IntegerField(_("距离"), db_index=True)

    objects = RelationshipManager()

    def __unicode__(self):
        return str("#{} -({})-> #{}".format(self.ancestor_id, self.distance, self.descendant_id,))


class StatusManager(models.Manager):
    def transit(
        self, id, to_state, is_pipeline=False, appoint=False, start=False, name="", version=None, unchanged_pass=False,
    ):
        """
        尝试改变某个节点的状态
        :param id: 节点 ID
        :param to_state: 目标状态
        :param is_pipeline: 该节点是否是 pipeline
        :param appoint: 该动作是否由用户发起（非引擎内部操作）
        :param start: 是否刷新其开始时间
        :param name: 节点名称
        :param version: 节点版本
        :param unchanged_pass: 当 to_state 与当前节点状态相同时则视为操作成功
        :return:
        """
        defaults = {
            "name": name,
            "state": to_state,
            "version": uniqid(),
        }
        if start:
            now = timezone.now()
            defaults["started_time"] = now
            defaults["state_refresh_at"] = now
        status, created = self.get_or_create(id=id, defaults=defaults)

        # reservation or first creation
        if created:
            return ActionResult(result=True, message="success", extra=status)

        with transaction.atomic():
            kwargs = {"id": id}
            if version:
                kwargs["version"] = version

            try:
                status = self.select_for_update().get(**kwargs)

            except Status.DoesNotExist:
                return ActionResult(result=False, message="node not exists or not be executed yet")

            if unchanged_pass and status.state == to_state:
                return ActionResult(result=True, message="success", extra=status)

            if states.can_transit(
                from_state=status.state, to_state=to_state, is_pipeline=is_pipeline, appoint=appoint,
            ):

                # 在冻结状态下不能改变 pipeline 的状态
                if is_pipeline:
                    subprocess_rel = SubProcessRelationship.objects.filter(subprocess_id=id)
                    if subprocess_rel:
                        process = PipelineProcess.objects.get(id=subprocess_rel[0].process_id)
                        if process.is_frozen:
                            return ActionResult(result=False, message="engine is frozen, can not perform operation",)

                    processes = PipelineProcess.objects.filter(root_pipeline_id=id)
                    if processes and processes[0].is_frozen:
                        return ActionResult(result=False, message="engine is frozen, can not perform operation",)

                if name:
                    status.name = name
                if to_state in states.ARCHIVED_STATES:
                    status.archived_time = timezone.now()

                # from FINISHED to RUNNING
                if states.is_rerunning(from_state=status.state, to_state=to_state):
                    history = History.objects.record(status, is_rerunning=True)
                    if history:
                        LogEntry.objects.link_history(node_id=status.id, history_id=history.id)
                    status.loop += 1
                    status.skip = False
                    status.version = uniqid()

                # reset started_time after record last status
                if start:
                    status.started_time = timezone.now()
                status.state = to_state
                status.state_refresh_at = timezone.now()
                status.save()
                return ActionResult(result=True, message="success", extra=status)
            else:
                return ActionResult(
                    result=False,
                    message="can't transit state({}) from {} to {}".format(id, status.state, to_state),
                    extra=status,
                )

    def batch_transit(self, id_list, state, from_state=None, exclude=None):
        """
        批量改变节点状态，仅用于子流程的状态修改
        :param id_list: 子流程 ID 列表
        :param state: 目标状态
        :param from_state: 起始状态
        :param exclude: 不需要改变状态的子流程 ID 列表
        :return:
        """
        if not id_list:
            return
        if not exclude:
            exclude = []

        id_list = set(id_list)
        exclude = set(exclude)
        kwargs = {"id__in": [i for i in id_list if i not in exclude]}
        if from_state:
            kwargs["state"] = from_state
        with transaction.atomic():
            self.select_for_update().filter(**kwargs).update(state=state)

    def state_for(self, id, may_not_exist=False, version=None):
        """
        获取某个节点的状态
        :param id: 节点 ID
        :param may_not_exist: 该节点是否可能不存在（未执行到）
        :param version: 节点版本
        :return:
        """
        kwargs = {"id": id}
        if version:
            kwargs["version"] = version
        if may_not_exist:
            try:
                return self.get(**kwargs).state
            except Status.DoesNotExist:
                return None
        return self.get(**kwargs).state

    def version_for(self, id):
        return self.get(id=id).version

    def states_for(self, id_list):
        return [s.state for s in self.filter(id__in=id_list)]

    def prepare_for_pipeline(self, pipeline):
        cls_str = str(pipeline.__class__)
        cls_name = pipeline.__class__.__name__[:NAME_MAX_LENGTH]
        self.create(
            id=pipeline.id, state=states.READY, name=cls_str if len(cls_str) <= NAME_MAX_LENGTH else cls_name,
        )

    def fail(self, node, ex_data):
        action_res = self.transit(node.id, states.FAILED)

        if not action_res.result:
            return action_res

        Data.objects.write_node_data(node, ex_data)
        return action_res

    def raw_fail(self, node_id, ex_data):
        action_res = self.transit(node_id, states.FAILED)

        if not action_res.result:
            return action_res

        Data.objects.write_ex_data(node_id, ex_data)
        return action_res

    def finish(self, node, error_ignorable=False):
        action_res = self.transit(node.id, states.FINISHED)

        if not action_res.result:
            return action_res

        Data.objects.write_node_data(node)
        if error_ignorable:
            s = Status.objects.get(id=node.id)
            s.error_ignorable = True
            s.save()

        return action_res

    def skip(self, process, node):
        s = Status.objects.get(id=node.id)  # 一定要先取出来，不然 archive time 会被覆盖
        if RERUN_MAX_LIMIT != 0 and s.loop > RERUN_MAX_LIMIT:
            return ActionResult(
                result=False,
                message="rerun times exceed max limit: {limit}, can not skip".format(limit=RERUN_MAX_LIMIT),
            )

        action_res = self.transit(id=node.id, to_state=states.FINISHED, appoint=True)
        if not action_res.result:
            return action_res

        history = History.objects.record(s)
        LogEntry.objects.link_history(node_id=node.id, history_id=history.id)

        s.refresh_from_db()
        s.started_time = s.archived_time

        s.skip = True
        s.save()

        # 由于节点执行失败，数据可能尚未写入当前的 Data 对象，所以要在这里做一次写入操作
        node.skip()
        Data.objects.write_node_data(node)

        self.recover_from_block(process.root_pipeline.id, process.subprocess_stack)
        signals.node_skip_call.send(sender=Status, process=process, node=node)

        return action_res

    def retry(self, process, node, inputs):
        if RERUN_MAX_LIMIT != 0 and self.get(id=node.id).loop > RERUN_MAX_LIMIT:
            return ActionResult(
                result=False,
                message="rerun times exceed max limit: {limit}, can not retry".format(limit=RERUN_MAX_LIMIT),
            )

        action_res = self.transit(id=node.id, to_state=states.READY, appoint=True)
        if not action_res.result:
            return action_res

        # add retry times
        s = Status.objects.get(id=node.id)
        s.version = uniqid()
        history = History.objects.record(s)
        LogEntry.objects.link_history(node_id=node.id, history_id=history.id)
        s.retry += 1
        s.started_time = None
        s.archived_time = None
        s.save()

        # update inputs
        if inputs:
            new_data = DataObject(inputs=inputs, outputs={})
            node.data = new_data
            Data.objects.write_node_data(node)

        # mark
        node.next_exec_is_retry()

        self.recover_from_block(process.root_pipeline.id, process.subprocess_stack)
        signals.node_retry_ready.send(sender=Status, process=process, node=node)

        # because node may be updated
        process.save()

        return action_res

    def recover_from_block(self, root_pipeline_id, subprocess_stack):
        Status.objects.batch_transit(id_list=subprocess_stack, state=states.RUNNING, from_state=states.BLOCKED)
        Status.objects.transit(id=root_pipeline_id, to_state=states.READY, is_pipeline=True)

    @contextlib.contextmanager
    def lock(self, id):
        with transaction.atomic():
            self.select_for_update().get(id=id)
            yield


class Status(models.Model):
    id = models.CharField(_("节点 ID"), unique=True, primary_key=True, max_length=32)
    state = models.CharField(_("状态"), max_length=10)
    name = models.CharField(_("节点名称"), max_length=NAME_MAX_LENGTH, default="")
    retry = models.IntegerField(_("重试次数"), default=0)
    loop = models.IntegerField(_("循环次数"), default=1)
    skip = models.BooleanField(_("是否跳过"), default=False)
    error_ignorable = models.BooleanField(_("是否出错后自动忽略"), default=False)
    created_time = models.DateTimeField(_("创建时间"), auto_now_add=True, db_index=True)
    started_time = models.DateTimeField(_("开始时间"), null=True)
    archived_time = models.DateTimeField(_("归档时间"), null=True)
    version = models.CharField(_("版本"), max_length=32)
    state_refresh_at = models.DateTimeField(_("上次状态更新的时间"), null=True)

    objects = StatusManager()

    class Meta:
        ordering = ["-created_time"]

    def is_state_for_subproc(self):
        return self.name.endswith("SubProcess")


class DataManager(models.Manager):
    def write_node_data(self, node, ex_data=None):
        data, created = self.get_or_create(id=node.id)
        if hasattr(node, "data") and node.data:
            data.inputs = node.data.get_inputs()
            outputs = node.data.get_outputs()
            ex_data = outputs.pop("ex_data", ex_data)
            data.outputs = outputs
        data.ex_data = ex_data
        data.save()

    def write_ex_data(self, node_id, ex_data=None):
        data, created = self.get_or_create(id=node_id)
        data.ex_data = ex_data
        data.save()

    def forced_fail(self, node_id, ex_data=""):
        data, created = self.get_or_create(id=node_id)
        data.outputs = {
            "_forced_failed": True,
        }
        data.ex_data = ex_data
        data.save()


class Data(models.Model):
    id = models.CharField(_("节点 ID"), unique=True, primary_key=True, max_length=32)
    inputs = IOField(verbose_name=_("输入数据"), default=None)
    outputs = IOField(verbose_name=_("输出数据"), default=None)
    ex_data = IOField(verbose_name=_("异常数据"), default=None)

    objects = DataManager()


class HistoryData(models.Model):
    id = models.BigAutoField(_("ID"), primary_key=True)
    inputs = IOField(verbose_name=_("输入数据"), default=None)
    outputs = IOField(verbose_name=_("输出数据"), default=None)
    ex_data = IOField(verbose_name=_("异常数据"), default=None)

    objects = DataManager()


class MultiCallbackData(models.Model):
    id = models.BigAutoField(_("自增ID"), primary_key=True)
    schedule_id = models.CharField(_("回调服务ID"), max_length=NAME_MAX_LENGTH)
    data = IOField(verbose_name=_("回调数据"))


DO_NOT_RECORD_WHEN_RERUN = frozenset({"<class 'pipeline.core.flow.activity.LoopServiceActivity'>"})


class HistoryManager(models.Manager):
    def record(self, status, is_rerunning=False):
        if is_rerunning and status.name in DO_NOT_RECORD_WHEN_RERUN:
            return None

        data = Data.objects.get(id=status.id)
        history_data = HistoryData.objects.create(inputs=data.inputs, outputs=data.outputs, ex_data=data.ex_data)
        return self.create(
            identifier=status.id,
            started_time=status.started_time,
            archived_time=status.archived_time,
            data=history_data,
            loop=status.loop,
            skip=status.skip,
        )

    def get_histories(self, identifier, loop=None):
        filters = {"identifier": identifier}
        if loop is not None:
            filters["loop"] = loop
        histories = self.filter(**filters).order_by("started_time")
        data = [
            {
                "history_id": item.id,
                "started_time": item.started_time,
                "archived_time": item.archived_time,
                "elapsed_time": calculate_elapsed_time(item.started_time, item.archived_time),
                "inputs": item.data.inputs,
                "outputs": item.data.outputs,
                "ex_data": item.data.ex_data,
                "loop": item.loop,
                "skip": item.skip,
            }
            for item in histories
        ]
        return data


class History(models.Model):
    id = models.BigAutoField(_("ID"), primary_key=True)
    identifier = models.CharField(_("节点 id"), max_length=32, db_index=True)
    started_time = models.DateTimeField(_("开始时间"))
    archived_time = models.DateTimeField(_("结束时间"))
    loop = models.IntegerField(_("循环次数"), default=1)
    skip = models.BooleanField(_("是否跳过"), default=False)

    data = models.ForeignKey(HistoryData, null=True, on_delete=models.SET_NULL)

    objects = HistoryManager()


class ScheduleServiceManager(models.Manager):
    def set_schedule(self, activity_id, service_act, process_id, version, parent_data):
        wait_callback = service_act.service.interval is None
        multi_callback_enabled = service_act.service.multi_callback_enabled()
        schedule = self.create(
            id="{}{}".format(activity_id, version),
            activity_id=activity_id,
            service_act=service_act,
            process_id=process_id,
            wait_callback=wait_callback,
            multi_callback_enabled=multi_callback_enabled,
            version=version,
        )
        data_service.set_schedule_data(schedule.id, parent_data)

        if not wait_callback:
            count_down = service_act.service.interval.next()
            valve.send(
                signals,
                "schedule_ready",
                sender=ScheduleService,
                process_id=process_id,
                schedule_id=schedule.id,
                countdown=count_down,
            )

        return schedule

    def schedule_for(self, activity_id, version):
        return self.get(id="{}{}".format(activity_id, version))

    def delete_schedule(self, activity_id, version):
        return self.filter(activity_id=activity_id, version=version).delete()

    def update_celery_info(self, id, lock, celery_id, schedule_date, is_scheduling=False):
        return self.filter(id=id, celery_info_lock=lock).update(
            celery_info_lock=models.F("celery_info_lock") + 1,
            celery_id=celery_id,
            schedule_date=schedule_date,
            is_scheduling=is_scheduling,
        )


class ScheduleService(models.Model):
    SCHEDULE_ID_SPLIT_DIVISION = 32

    id = models.CharField(_("ID 节点ID+version"), max_length=NAME_MAX_LENGTH, unique=True, primary_key=True)
    activity_id = models.CharField(_("节点 ID"), max_length=32, db_index=True)
    process_id = models.CharField(_("Pipeline 进程 ID"), max_length=32)
    schedule_times = models.IntegerField(_("被调度次数"), default=0)
    wait_callback = models.BooleanField(_("是否是回调型调度"), default=False)
    multi_callback_enabled = models.BooleanField(_("是否支持多次回调"), default=False)
    callback_data = IOField(verbose_name=_("回调数据"), default=None)
    service_act = IOField(verbose_name=_("待调度服务"))
    is_finished = models.BooleanField(_("是否已完成"), default=False)
    version = models.CharField(_("Activity 的版本"), max_length=32, db_index=True)
    is_scheduling = models.BooleanField(_("是否正在被调度"), default=False, db_index=True)

    objects = ScheduleServiceManager()

    def set_next_schedule(self):
        if self.wait_callback:
            raise exceptions.InvalidOperationException("can't set next schedule on callback schedule.")
        count_down = self.service_act.service.interval.next()
        self.is_scheduling = False
        self.save()
        ScheduleCeleryTask.objects.unbind(self.id)

        valve.send(
            signals,
            "schedule_ready",
            sender=ScheduleService,
            process_id=self.process_id,
            schedule_id=self.id,
            countdown=count_down,
        )

    def destroy(self):
        schedule_id = self.id
        self.delete()
        data_service.delete_parent_data(schedule_id)
        ScheduleCeleryTask.objects.destroy(schedule_id)

    def finish(self):
        self.is_finished = True
        self.service_act = None
        self.is_scheduling = False
        self.save()
        ScheduleCeleryTask.objects.destroy(self.id)

    def callback(self, callback_data, process_id):
        if not self.wait_callback:
            raise exceptions.InvalidOperationException("can't callback a poll schedule.")

        if self.multi_callback_enabled:
            callback_data = MultiCallbackData.objects.create(schedule_id=self.id, data=callback_data)
            valve.send(
                signals,
                "schedule_ready",
                sender=ScheduleService,
                process_id=process_id,
                schedule_id=self.id,
                data_id=callback_data.id,
                countdown=0,
            )
        else:
            self.callback_data = callback_data
            self.save()
            valve.send(
                signals,
                "schedule_ready",
                sender=ScheduleService,
                process_id=process_id,
                schedule_id=self.id,
                countdown=0,
            )

    def is_one_time_callback(self):
        return self.wait_callback and not self.multi_callback_enabled


class SubProcessRelationshipManager(models.Manager):
    def add_relation(self, subprocess_id, process_id):
        return self.create(subprocess_id=subprocess_id, process_id=process_id)

    def delete_relation(self, subprocess_id, process_id):
        kwargs = {}
        if subprocess_id:
            kwargs["subprocess_id"] = subprocess_id
        if process_id:
            kwargs["process_id"] = process_id
        self.filter(**kwargs).delete()

    def get_relate_process(self, subprocess_id):
        qs = self.filter(subprocess_id=subprocess_id)
        proc_ids = [i.process_id for i in qs]
        return PipelineProcess.objects.filter(id__in=proc_ids)


class SubProcessRelationship(models.Model):
    id = models.BigAutoField(_("ID"), primary_key=True)
    subprocess_id = models.CharField(_("子流程 ID"), max_length=32, db_index=True)
    process_id = models.CharField(_("对应的进程 ID"), max_length=32)

    objects = SubProcessRelationshipManager()


class ProcessCeleryTaskManager(models.Manager):
    def bind(self, process_id, celery_task_id):
        rel, created = self.get_or_create(process_id=process_id, defaults={"celery_task_id": celery_task_id})
        if not created:
            rel.celery_task_id = celery_task_id
            rel.save()

    def unbind(self, process_id):
        self.filter(process_id=process_id).update(celery_task_id="")

    def destroy(self, process_id):
        self.filter(process_id=process_id).delete()

    def start_task(self, process_id, task, kwargs, record_error=True):
        if record_error:
            with SendFailedCeleryTask.watch(
                name=task.name,
                kwargs=kwargs,
                type=SendFailedCeleryTask.TASK_TYPE_PROCESS,
                extra_kwargs={"process_id": process_id},
            ):
                task_id = task.apply_async(**kwargs)
        else:
            task_id = task.apply_async(**kwargs)
        self.bind(process_id, task_id)

    def revoke(self, process_id, kill=False):
        task = self.get(process_id=process_id)
        kwargs = {} if not kill else {"signal": "SIGKILL"}
        revoke(task.celery_task_id, terminate=True, **kwargs)
        self.destroy(process_id)


class ProcessCeleryTask(models.Model):
    id = models.BigAutoField(_("ID"), primary_key=True)
    process_id = models.CharField(_("pipeline 进程 ID"), max_length=32, unique=True, db_index=True)
    celery_task_id = models.CharField(_("celery 任务 ID"), max_length=40, default="")

    objects = ProcessCeleryTaskManager()


class ScheduleCeleryTaskManager(models.Manager):
    def bind(self, schedule_id, celery_task_id):
        rel, created = self.get_or_create(schedule_id=schedule_id, defaults={"celery_task_id": celery_task_id})
        if not created:
            rel.celery_task_id = celery_task_id
            rel.save()

    def unbind(self, schedule_id):
        self.filter(schedule_id=schedule_id).update(celery_task_id="")

    def destroy(self, schedule_id):
        self.filter(schedule_id=schedule_id).delete()

    def start_task(self, schedule_id, task, kwargs, record_error=True):
        if record_error:
            with SendFailedCeleryTask.watch(
                name=task.name,
                kwargs=kwargs,
                type=SendFailedCeleryTask.TASK_TYPE_SCHEDULE,
                extra_kwargs={"schedule_id": schedule_id},
            ):
                task_id = task.apply_async(**kwargs)
        else:
            task_id = task.apply_async(**kwargs)
        self.bind(schedule_id, task_id)


class ScheduleCeleryTask(models.Model):
    id = models.BigAutoField(_("ID"), primary_key=True)
    schedule_id = models.CharField(_("schedule ID"), max_length=NAME_MAX_LENGTH, unique=True, db_index=True)
    celery_task_id = models.CharField(_("celery 任务 ID"), max_length=40, default="")

    objects = ScheduleCeleryTaskManager()


class NodeCeleryTaskManager(models.Manager):
    def bind(self, node_id, celery_task_id):
        rel, created = self.update_or_create(node_id=node_id, defaults={"celery_task_id": celery_task_id})
        if not created:
            rel.celery_task_id = celery_task_id
            rel.save()

    def unbind(self, node_id):
        self.filter(node_id=node_id).update(celery_task_id="")

    def destroy(self, node_id):
        self.filter(node_id=node_id).delete()

    def start_task(self, node_id, task, kwargs, record_error=True):
        if record_error:
            with SendFailedCeleryTask.watch(
                name=task.name,
                kwargs=kwargs,
                type=SendFailedCeleryTask.TASK_TYPE_NODE,
                extra_kwargs={"node_id": node_id},
            ):
                task_id = task.apply_async(**kwargs)
        else:
            task_id = task.apply_async(**kwargs)
        self.bind(node_id, task_id)

    def revoke(self, node_id):
        task = self.get(node_id=node_id)
        revoke(task.celery_task_id)
        self.destroy(node_id)


class NodeCeleryTask(models.Model):
    id = models.BigAutoField(_("ID"), primary_key=True)
    node_id = models.CharField(_("节点 ID"), max_length=32, unique=True, db_index=True)
    celery_task_id = models.CharField(_("celery 任务 ID"), max_length=40, default="")

    objects = NodeCeleryTaskManager()


class SendFailedCeleryTaskManager(models.Manager):
    def record(self, name, kwargs, type, extra_kwargs, exec_trace):
        save_extra_kwargs = extra_kwargs
        save_kwargs = kwargs

        if not isinstance(save_extra_kwargs, str):
            save_extra_kwargs = json.dumps(save_extra_kwargs)

        if not isinstance(save_kwargs, str):
            save_kwargs = json.dumps(save_kwargs)

        return self.create(
            name=name, kwargs=save_kwargs, type=type, extra_kwargs=save_extra_kwargs, exec_trace=exec_trace,
        )

    def resend(self, id):
        self.get(id=id).resend()


class SendFailedCeleryTask(models.Model):

    TASK_TYPE_EMPTY = 0
    TASK_TYPE_PROCESS = 1
    TASK_TYPE_NODE = 2
    TASK_TYPE_SCHEDULE = 3

    TASK_TYPE_CHOICES = (
        (TASK_TYPE_EMPTY, "empty"),
        (TASK_TYPE_PROCESS, "process"),
        (TASK_TYPE_NODE, "node"),
        (TASK_TYPE_SCHEDULE, "schedule"),
    )

    id = models.BigAutoField(_("ID"), primary_key=True)
    name = models.CharField(_("任务名"), max_length=1024)
    kwargs = models.TextField(_("任务参数"))
    type = models.IntegerField(_("任务类型"), choices=TASK_TYPE_CHOICES)
    extra_kwargs = models.TextField(_("额外参数"))
    exec_trace = models.TextField(_("错误信息"))
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True)

    objects = SendFailedCeleryTaskManager()

    @property
    def kwargs_dict(self):
        return json.loads(self.kwargs)

    @property
    def extra_kwargs_dict(self):
        return json.loads(self.extra_kwargs)

    def resend(self):
        try:
            task = current_app.tasks[self.name]

            if self.type == self.TASK_TYPE_EMPTY:
                task.apply_async(**self.kwargs_dict)
            elif self.type == self.TASK_TYPE_PROCESS:
                ProcessCeleryTask.objects.start_task(
                    process_id=self.extra_kwargs_dict["process_id"],
                    task=task,
                    kwargs=self.kwargs_dict,
                    record_error=False,
                )
            elif self.type == self.TASK_TYPE_NODE:
                NodeCeleryTask.objects.start_task(
                    node_id=self.extra_kwargs_dict["node_id"], task=task, kwargs=self.kwargs_dict, record_error=False,
                )
            elif self.type == self.TASK_TYPE_SCHEDULE:
                ScheduleCeleryTask.objects.start_task(
                    schedule_id=self.extra_kwargs_dict["schedule_id"],
                    task=task,
                    kwargs=self.kwargs_dict,
                    record_error=False,
                )
            else:
                raise TypeError("unsupport type: {}.".format(self.type))
        except Exception as e:
            logger.exception("fail task send replay error.")
            raise e
        else:
            self.delete()

    @classmethod
    @contextlib.contextmanager
    def watch(cls, name, kwargs, type, extra_kwargs):
        try:
            yield
        except Exception:
            logger.exception("celery task({}) watcher catch error.".format(name))
            cls.objects.record(
                name=name, kwargs=kwargs, type=type, extra_kwargs=extra_kwargs, exec_trace=traceback.format_exc(),
            )
            # raise specific exception to indicate that send fail task have been catched
            raise exceptions.CeleryFailedTaskCatchException(name)
