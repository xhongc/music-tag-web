from django.db import models

from applications.flow.models import ProcessRun


class Task(models.Model):
    TypeChoices = (
        ("hand", "手动"),
        ("now", "立即"),
        ("time", "定时"),
        ("cycle", "周期"),
        ("cron", "cron表达式"),
    )
    CycleChoices = (
        ("min", "分钟"),
        ("hour", "小时"),
        ("day", "天"),
    )
    name = models.CharField("任务名称", max_length=255, blank=False, null=False)

    process_run = models.ForeignKey(ProcessRun, on_delete=models.CASCADE, null=True, db_constraint=False,
                                    related_name="tasks")
    run_type = models.CharField("执行方式", choices=TypeChoices,max_length=64)
    when_start = models.CharField(max_length=100, verbose_name="执行时间")
    cycle_time = models.CharField(max_length=20, null=True, verbose_name="周期时间")
    cycle_type = models.CharField(max_length=20, null=True, verbose_name="周期间隔(min,hour,day)", choices=CycleChoices)
    cron_time = models.TextField(default="", verbose_name="cron表达式")

    celery_task_id = models.CharField(max_length=64, null=True, verbose_name="celery的任务ID")