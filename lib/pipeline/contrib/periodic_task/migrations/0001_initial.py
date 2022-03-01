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


from django.db import migrations, models
import django.db.models.deletion
import timezone_field.fields
import pipeline.models


class Migration(migrations.Migration):

    dependencies = [
        ("pipeline", "0016_auto_20181220_0958"),
    ]

    operations = [
        migrations.CreateModel(
            name="CrontabSchedule",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True,),),
                ("minute", models.CharField(default=b"*", max_length=64, verbose_name="minute"),),
                ("hour", models.CharField(default=b"*", max_length=64, verbose_name="hour"),),
                ("day_of_week", models.CharField(default=b"*", max_length=64, verbose_name="day of week"),),
                ("day_of_month", models.CharField(default=b"*", max_length=64, verbose_name="day of month"),),
                ("month_of_year", models.CharField(default=b"*", max_length=64, verbose_name="month of year"),),
                ("timezone", timezone_field.fields.TimeZoneField(default=b"UTC")),
            ],
            options={
                "ordering": ["month_of_year", "day_of_month", "day_of_week", "hour", "minute",],
                "verbose_name": "crontab",
                "verbose_name_plural": "crontabs",
            },
        ),
        migrations.CreateModel(
            name="DjCeleryPeriodicTask",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True,),),
                (
                    "name",
                    models.CharField(help_text="Useful description", unique=True, max_length=200, verbose_name="name",),
                ),
                ("task", models.CharField(max_length=200, verbose_name="task name")),
                (
                    "args",
                    models.TextField(
                        default=b"[]",
                        help_text="JSON encoded positional arguments",
                        verbose_name="Arguments",
                        blank=True,
                    ),
                ),
                (
                    "kwargs",
                    models.TextField(
                        default=b"{}",
                        help_text="JSON encoded keyword arguments",
                        verbose_name="Keyword arguments",
                        blank=True,
                    ),
                ),
                (
                    "queue",
                    models.CharField(
                        default=None,
                        max_length=200,
                        blank=True,
                        help_text="Queue defined in CELERY_QUEUES",
                        null=True,
                        verbose_name="queue",
                    ),
                ),
                (
                    "exchange",
                    models.CharField(default=None, max_length=200, null=True, verbose_name="exchange", blank=True,),
                ),
                (
                    "routing_key",
                    models.CharField(default=None, max_length=200, null=True, verbose_name="routing key", blank=True,),
                ),
                ("expires", models.DateTimeField(null=True, verbose_name="expires", blank=True),),
                ("enabled", models.BooleanField(default=True, verbose_name="enabled")),
                ("last_run_at", models.DateTimeField(null=True, editable=False, blank=True),),
                ("total_run_count", models.PositiveIntegerField(default=0, editable=False),),
                ("date_changed", models.DateTimeField(auto_now=True)),
                ("description", models.TextField(verbose_name="description", blank=True),),
                (
                    "crontab",
                    models.ForeignKey(
                        blank=True,
                        to="periodic_task.CrontabSchedule",
                        help_text="Use one of interval/crontab",
                        null=True,
                        verbose_name="crontab",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={"verbose_name": "periodic task", "verbose_name_plural": "periodic tasks",},
        ),
        migrations.CreateModel(
            name="DjCeleryPeriodicTasks",
            fields=[
                ("ident", models.SmallIntegerField(default=1, unique=True, serialize=False, primary_key=True),),
                ("last_update", models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name="IntervalSchedule",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True,),),
                ("every", models.IntegerField(verbose_name="every")),
                (
                    "period",
                    models.CharField(
                        max_length=24,
                        verbose_name="period",
                        choices=[
                            (b"days", "Days"),
                            (b"hours", "Hours"),
                            (b"minutes", "Minutes"),
                            (b"seconds", "Seconds"),
                            (b"microseconds", "Microseconds"),
                        ],
                    ),
                ),
            ],
            options={"ordering": ["period", "every"], "verbose_name": "interval", "verbose_name_plural": "intervals",},
        ),
        migrations.CreateModel(
            name="PeriodicTask",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True,),),
                ("name", models.CharField(max_length=64, verbose_name="\u5468\u671f\u4efb\u52a1\u540d\u79f0",),),
                ("cron", models.CharField(max_length=128, verbose_name="\u8c03\u5ea6\u7b56\u7565"),),
                ("total_run_count", models.PositiveIntegerField(default=0, verbose_name="\u6267\u884c\u6b21\u6570"),),
                ("last_run_at", models.DateTimeField(null=True, verbose_name="\u4e0a\u6b21\u8fd0\u884c\u65f6\u95f4"),),
                ("creator", models.CharField(default=b"", max_length=32, verbose_name="\u521b\u5efa\u8005"),),
                ("extra_info", pipeline.models.CompressJSONField(verbose_name="\u989d\u5916\u4fe1\u606f", null=True),),
                (
                    "celery_task",
                    models.ForeignKey(
                        verbose_name="celery \u5468\u671f\u4efb\u52a1\u5b9e\u4f8b",
                        to="periodic_task.DjCeleryPeriodicTask",
                        null=True,
                        on_delete=models.SET_NULL,
                    ),
                ),
                (
                    "snapshot",
                    models.ForeignKey(
                        related_name="periodic_tasks",
                        verbose_name="\u7528\u4e8e\u521b\u5efa\u6d41\u7a0b\u5b9e\u4f8b\u7684\u7ed3\u6784\u6570\u636e",
                        to="pipeline.Snapshot",
                        on_delete=models.DO_NOTHING,
                    ),
                ),
                (
                    "template",
                    models.ForeignKey(
                        related_name="periodic_tasks",
                        on_delete=django.db.models.deletion.SET_NULL,
                        verbose_name="\u5468\u671f\u4efb\u52a1\u5bf9\u5e94\u7684\u6a21\u677f",
                        to_field="template_id",
                        to="pipeline.PipelineTemplate",
                        null=True,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PeriodicTaskHistory",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True,),),
                ("ex_data", models.TextField(verbose_name="\u5f02\u5e38\u4fe1\u606f")),
                ("start_at", models.DateTimeField(auto_now_add=True, verbose_name="\u5f00\u59cb\u65f6\u95f4"),),
                (
                    "start_success",
                    models.BooleanField(default=True, verbose_name="\u662f\u5426\u542f\u52a8\u6210\u529f",),
                ),
                (
                    "periodic_task",
                    models.ForeignKey(
                        related_name="instance_rel",
                        verbose_name="\u5468\u671f\u4efb\u52a1",
                        to="periodic_task.PeriodicTask",
                        null=True,
                        on_delete=models.DO_NOTHING,
                    ),
                ),
                (
                    "pipeline_instance",
                    models.ForeignKey(
                        related_name="periodic_task_rel",
                        verbose_name="Pipeline \u5b9e\u4f8b",
                        to_field="instance_id",
                        to="pipeline.PipelineInstance",
                        null=True,
                        on_delete=models.DO_NOTHING,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="djceleryperiodictask",
            name="interval",
            field=models.ForeignKey(
                verbose_name="interval",
                blank=True,
                to="periodic_task.IntervalSchedule",
                null=True,
                on_delete=models.CASCADE,
            ),
        ),
    ]
