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

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Process(models.Model):
    id = models.BigAutoField(_("ID"), primary_key=True)
    parent_id = models.BigIntegerField(_("父进程 ID"), default=-1, db_index=True)
    ack_num = models.IntegerField(_("收到子进程 ACK 数量"), default=0)
    need_ack = models.IntegerField(_("需要收到的子进程 ACK 数量"), default=-1)
    asleep = models.BooleanField(_("是否处于休眠状态"), default=True)
    suspended = models.BooleanField(_("是否处于暂停状态"), default=False)
    frozen = models.BooleanField(_("是否处于冻结状态"), default=False)
    dead = models.BooleanField(_("是否已经死亡"), default=False)
    last_heartbeat = models.DateTimeField(_("上次心跳时间"), auto_now_add=True, db_index=True)
    destination_id = models.CharField(_("执行终点 ID"), default="", max_length=33)
    current_node_id = models.CharField(_("当前节点 ID"), default="", max_length=33, db_index=True)
    root_pipeline_id = models.CharField(_("根流程 ID"), null=False, max_length=33, db_index=True)
    suspended_by = models.CharField(_("导致进程暂停的节点 ID"), default="", max_length=33, db_index=True)
    priority = models.IntegerField(_("优先级"))
    queue = models.CharField(_("所属队列"), default="", max_length=128)
    pipeline_stack = models.TextField(_("流程栈"), default="[]", null=False)


class Node(models.Model):
    id = models.BigAutoField(_("ID"), primary_key=True)
    node_id = models.CharField(_("节点 ID"), null=False, max_length=33, db_index=True)
    detail = models.TextField(_("节点详情"), null=False)


class State(models.Model):
    id = models.BigAutoField(_("ID"), primary_key=True)
    node_id = models.CharField(_("节点 ID"), null=False, max_length=33, unique=True)
    root_id = models.CharField(_("根节点 ID"), null=False, default="", max_length=33, db_index=True)
    parent_id = models.CharField(_("父节点 ID"), null=False, default="", max_length=33, db_index=True)
    name = models.CharField(_("状态名"), null=False, max_length=64)
    version = models.CharField(_("状态版本"), null=False, max_length=33)
    loop = models.IntegerField(_("循环次数"), default=1)
    inner_loop = models.IntegerField(_("子流程内部循环次数"), default=1)
    retry = models.IntegerField(_("重试次数"), default=0)
    skip = models.BooleanField(_("是否跳过"), default=False)
    error_ignored = models.BooleanField(_("是否出错后自动忽略"), default=False)
    created_time = models.DateTimeField(_("创建时间"), auto_now_add=True)
    started_time = models.DateTimeField(_("开始时间"), null=True)
    archived_time = models.DateTimeField(_("归档时间"), null=True)


class Schedule(models.Model):
    id = models.BigAutoField(_("ID"), primary_key=True)
    type = models.IntegerField(_("调度类型"))
    process_id = models.BigIntegerField(_("进程 ID"), default=-1)
    node_id = models.CharField(_("节点 ID"), null=False, max_length=33)
    finished = models.BooleanField(_("是否已完成"), default=False)
    expired = models.BooleanField(_("是否已过期"), default=False)
    scheduling = models.BooleanField(_("是否正在调度"), default=False)
    version = models.CharField(_("状态版本"), null=False, max_length=33)
    schedule_times = models.IntegerField(_("被调度次数"), default=0)

    class Meta:
        unique_together = ["node_id", "version"]


class Data(models.Model):
    id = models.BigAutoField(_("ID"), primary_key=True)
    node_id = models.CharField(_("节点 ID"), null=False, max_length=33, db_index=True, unique=True)
    inputs = models.TextField(_("原始输入数据"))
    outputs = models.TextField(_("原始输出数据"))


class ExecutionData(models.Model):
    id = models.BigAutoField(_("ID"), primary_key=True)
    node_id = models.CharField(_("节点 ID"), null=False, max_length=33, db_index=True, unique=True)
    inputs_serializer = models.CharField(_("输入序列化器"), null=False, max_length=32)
    outputs_serializer = models.CharField(_("输出序列化器"), null=False, max_length=32)
    inputs = models.TextField(_("节点执行输入数据"))
    outputs = models.TextField(_("节点执行输出数据"))


class CallbackData(models.Model):
    id = models.BigAutoField(_("ID"), primary_key=True)
    node_id = models.CharField(_("节点 ID"), null=False, max_length=33)
    version = models.CharField(_("状态版本"), null=False, max_length=33)
    data = models.TextField(_("回调数据"))


class ContextValue(models.Model):
    id = models.BigAutoField(_("ID"), primary_key=True)
    pipeline_id = models.CharField(_("流程 ID"), null=False, max_length=33)
    key = models.CharField(_("变量 key"), null=False, max_length=128)
    type = models.IntegerField(_("变量类型"))
    serializer = models.CharField(_("序列化器"), null=False, max_length=32)
    code = models.CharField(_("计算型变量类型唯一标志"), default="", max_length=128)
    value = models.TextField(_("变量值"))
    references = models.TextField(_("所有对其他变量直接或间接的引用"))

    class Meta:
        unique_together = ["pipeline_id", "key"]


class ContextOutputs(models.Model):
    id = models.BigAutoField(_("ID"), primary_key=True)
    pipeline_id = models.CharField(_("流程 ID"), null=False, max_length=33, unique=True)
    outputs = models.TextField(_("输出配置"))


class ExecutionHistory(models.Model):
    id = models.BigAutoField(_("ID"), primary_key=True)
    node_id = models.CharField(_("节点 ID"), null=False, max_length=33)
    loop = models.IntegerField(_("循环次数"), default=1)
    retry = models.IntegerField(_("重试次数"), default=0)
    skip = models.BooleanField(_("是否跳过"), default=False)
    version = models.CharField(_("状态版本"), null=False, max_length=33)
    started_time = models.DateTimeField(_("开始时间"), null=False)
    archived_time = models.DateTimeField(_("归档时间"), null=False)
    inputs_serializer = models.CharField(_("输入序列化器"), null=False, max_length=32)
    outputs_serializer = models.CharField(_("输出序列化器"), null=False, max_length=32)
    inputs = models.TextField(_("节点执行输入数据"))
    outputs = models.TextField(_("节点执行输出数据"))

    class Meta:
        index_together = ["node_id", "loop"]


class LogEntry(models.Model):
    id = models.BigAutoField(_("ID"), primary_key=True)
    node_id = models.CharField(_("节点 ID"), max_length=33)
    version = models.CharField(_("状态版本"), default="", max_length=33)
    loop = models.IntegerField(_("循环次数"), default=1)
    logger_name = models.CharField(_("logger 名称"), max_length=128)
    level_name = models.CharField(_("日志等级"), max_length=32)
    message = models.TextField(_("日志内容"), null=True)
    logged_at = models.DateTimeField(_("输出时间"), auto_now_add=True, db_index=True)

    class Meta:
        index_together = ["node_id", "loop"]
