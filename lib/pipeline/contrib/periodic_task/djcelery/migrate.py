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

from django.db import transaction
from django_celery_beat.models import (
    IntervalSchedule,
    CrontabSchedule,
    PeriodicTask,
)

from pipeline.contrib.periodic_task.djcelery.models import (
    IntervalSchedule as DjCeleryIntervalSchedule,
    CrontabSchedule as DjCeleryCrontabSchedule,
    DjCeleryPeriodicTask,
)

BATCH_SIZE = 500


@transaction.atomic
def try_to_migrate_to_django_celery_beat():
    """
    try to migrate djcelery to django_celery_beat
    if django_celery_beat models has data, indicate that pipeline is first use in project
    (because old version pipeline is not compatible with django celery beat)
    so we will not do the migration works
    """
    if IntervalSchedule.objects.exists() or CrontabSchedule.objects.exists() or PeriodicTask.objects.exists():
        print("django_celery_beat in used, skip pipeline djcelery migration works")
        return

    # migrate IntervalScheudle
    old_intervals = DjCeleryIntervalSchedule.objects.all()
    new_intervals = []
    for oi in old_intervals:
        new_intervals.append(IntervalSchedule(id=oi.id, every=oi.every, period=oi.period))
    IntervalSchedule.objects.bulk_create(new_intervals, batch_size=BATCH_SIZE)
    print("[pipeline]migrate {} interval objects".format(len(new_intervals)))

    # migrate CrontabSchedule
    old_crontabs = DjCeleryCrontabSchedule.objects.all()
    new_crontabs = []
    for oc in old_crontabs:
        new_crontabs.append(
            CrontabSchedule(
                id=oc.id,
                minute=oc.minute,
                hour=oc.hour,
                day_of_week=oc.day_of_week,
                day_of_month=oc.day_of_month,
                month_of_year=oc.month_of_year,
                timezone=oc.timezone,
            )
        )
    CrontabSchedule.objects.bulk_create(new_crontabs, batch_size=BATCH_SIZE)
    print("[pipeline]migrate {} crontab objects".format(len(new_crontabs)))

    # migrate PeriodicTask
    old_tasks = DjCeleryPeriodicTask.objects.all()
    new_tasks = []
    for ot in old_tasks:
        new_tasks.append(
            PeriodicTask(
                id=ot.id,
                name=ot.name,
                task=ot.task,
                interval_id=ot.interval_id,
                crontab_id=ot.crontab_id,
                solar_id=None,
                clocked_id=None,
                args=ot.args,
                kwargs=ot.kwargs,
                queue=ot.queue,
                exchange=ot.exchange,
                routing_key=ot.routing_key,
                expires=ot.expires,
                enabled=ot.enabled,
                last_run_at=ot.last_run_at,
                total_run_count=ot.total_run_count,
                date_changed=ot.date_changed,
                description=ot.description,
            )
        )
    PeriodicTask.objects.bulk_create(new_tasks, batch_size=BATCH_SIZE)
    print("[pipeline]migrate {} periodic tasks".format(len(new_tasks)))
