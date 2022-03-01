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
from django.db import models
from django.utils.translation import ugettext_lazy as _

from pipeline.constants import PIPELINE_DEFAULT_PRIORITY
from pipeline.contrib.periodic_task.signals import periodic_task_start_failed
from pipeline.exceptions import InvalidOperationException
from pipeline.models import (
    CompressJSONField,
    PipelineInstance,
    PipelineTemplate,
    Snapshot,
)
from pipeline.utils.uniqid import uniqid
from django_celery_beat.models import (
    PeriodicTask as DjangoCeleryBeatPeriodicTask,
    CrontabSchedule as DjangoCeleryBeatCrontabSchedule,
)

from pipeline.contrib.periodic_task.djcelery.models import *  # noqa

BAMBOO_ENGINE_TRIGGER_TASK = "pipeline.contrib.periodic_task.tasks.bamboo_engine_periodic_task_start"


class PeriodicTaskManager(models.Manager):
    def create_task(
        self,
        name,
        template,
        cron,
        data,
        creator,
        timezone=None,
        extra_info=None,
        spread=False,
        priority=PIPELINE_DEFAULT_PRIORITY,
        queue="",
        trigger_task="",
    ):
        snapshot = Snapshot.objects.create_snapshot(data)
        schedule, _ = DjangoCeleryBeatCrontabSchedule.objects.get_or_create(
            minute=cron.get("minute", "*"),
            hour=cron.get("hour", "*"),
            day_of_week=cron.get("day_of_week", "*"),
            day_of_month=cron.get("day_of_month", "*"),
            month_of_year=cron.get("month_of_year", "*"),
            timezone=timezone or "UTC",
        )
        _ = schedule.schedule  # noqa

        task = self.create(
            name=name,
            template=template,
            snapshot=snapshot,
            cron=schedule.__str__(),
            creator=creator,
            extra_info=extra_info,
            priority=priority,
            queue=queue,
        )

        kwargs = {"period_task_id": task.id, "spread": spread}
        celery_task = DjangoCeleryBeatPeriodicTask.objects.create(
            crontab=schedule,
            name=uniqid(),
            task=trigger_task or "pipeline.contrib.periodic_task.tasks.periodic_task_start",
            enabled=False,
            kwargs=json.dumps(kwargs),
        )
        task.celery_task = celery_task
        task.save()
        return task


class PeriodicTask(models.Model):
    name = models.CharField(_("周期任务名称"), max_length=64)
    template = models.ForeignKey(
        PipelineTemplate,
        related_name="periodic_tasks",
        to_field="template_id",
        verbose_name=_("周期任务对应的模板"),
        null=True,
        on_delete=models.deletion.SET_NULL,
    )
    cron = models.CharField(_("调度策略"), max_length=128)
    celery_task = models.ForeignKey(
        DjangoCeleryBeatPeriodicTask, verbose_name=_("celery 周期任务实例"), null=True, on_delete=models.SET_NULL,
    )
    snapshot = models.ForeignKey(
        Snapshot, related_name="periodic_tasks", verbose_name=_("用于创建流程实例的结构数据"), on_delete=models.DO_NOTHING,
    )
    total_run_count = models.PositiveIntegerField(_("执行次数"), default=0)
    last_run_at = models.DateTimeField(_("上次运行时间"), null=True)
    creator = models.CharField(_("创建者"), max_length=32, default="")
    priority = models.IntegerField(_("流程优先级"), default=PIPELINE_DEFAULT_PRIORITY)
    queue = models.CharField(_("流程使用的队列名"), max_length=512, default="")
    extra_info = CompressJSONField(verbose_name=_("额外信息"), null=True)

    objects = PeriodicTaskManager()

    def __unicode__(self):
        return "{name}({id})".format(name=self.name, id=self.id)

    @property
    def enabled(self):
        return self.celery_task.enabled

    @property
    def execution_data(self):
        return self.snapshot.data

    @property
    def form(self):
        form = {
            key: var_info
            for key, var_info in list(self.execution_data["constants"].items())
            if var_info["show_type"] == "show"
        }
        return form

    def delete(self, using=None):
        self.set_enabled(False)
        self.celery_task.delete()
        PeriodicTaskHistory.objects.filter(periodic_task=self).delete()
        return super(PeriodicTask, self).delete(using)

    def set_enabled(self, enabled):
        self.celery_task.enabled = enabled
        self.celery_task.save()

    def modify_cron(self, cron, timezone=None):
        if self.enabled:
            raise InvalidOperationException("can not modify cron when task is enabled")
        schedule, _ = DjangoCeleryBeatCrontabSchedule.objects.get_or_create(
            minute=cron.get("minute", "*"),
            hour=cron.get("hour", "*"),
            day_of_week=cron.get("day_of_week", "*"),
            day_of_month=cron.get("day_of_month", "*"),
            month_of_year=cron.get("month_of_year", "*"),
            timezone=timezone or "UTC",
        )
        # try to initiate schedule object
        _ = schedule.schedule  # noqa
        self.cron = schedule.__str__()
        self.celery_task.crontab = schedule
        self.celery_task.save()
        self.save()

    def modify_constants(self, constants):
        if self.enabled:
            raise InvalidOperationException("can not modify constants when task is enabled")
        exec_data = self.execution_data
        for key, value in list(constants.items()):
            if key in exec_data["constants"]:
                exec_data["constants"][key]["value"] = value
        self.snapshot.data = exec_data
        self.snapshot.save()
        return exec_data["constants"]


class PeriodicTaskHistoryManager(models.Manager):
    def record_schedule(self, periodic_task, pipeline_instance, ex_data, start_success=True):
        history = self.create(
            periodic_task=periodic_task,
            pipeline_instance=pipeline_instance,
            ex_data=ex_data,
            start_success=start_success,
            priority=periodic_task.priority,
            queue=periodic_task.queue,
        )

        if not start_success:
            periodic_task_start_failed.send(sender=PeriodicTask, periodic_task=periodic_task, history=history)

        return history


class PeriodicTaskHistory(models.Model):
    periodic_task = models.ForeignKey(
        PeriodicTask, related_name="instance_rel", verbose_name=_("周期任务"), null=True, on_delete=models.DO_NOTHING,
    )
    pipeline_instance = models.ForeignKey(
        PipelineInstance,
        related_name="periodic_task_rel",
        verbose_name=_("Pipeline 实例"),
        to_field="instance_id",
        null=True,
        on_delete=models.DO_NOTHING,
    )
    ex_data = models.TextField(_("异常信息"))
    start_at = models.DateTimeField(_("开始时间"), auto_now_add=True)
    start_success = models.BooleanField(_("是否启动成功"), default=True)
    priority = models.IntegerField(_("流程优先级"), default=PIPELINE_DEFAULT_PRIORITY)
    queue = models.CharField(_("流程使用的队列名"), max_length=512, default="")

    objects = PeriodicTaskHistoryManager()
