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

import warnings
from functools import wraps
from itertools import count

from django.conf import settings
from django.db import connection, models
from django.db.models.query import QuerySet

from pipeline.contrib.periodic_task.djcelery.db import (
    commit_on_success,
    get_queryset,
    rollback_unless_managed,
)
from pipeline.contrib.periodic_task.djcelery.utils import now

try:
    from django.db import connections, router
except ImportError:  # pre-Django 1.2
    connections = router = None  # noqa


try:
    from celery.utils.timeutils import maybe_timedelta
except ImportError:
    from celery.utils.time import maybe_timedelta


def update_model_with_dict(obj, fields):
    [setattr(obj, attr_name, attr_value) for attr_name, attr_value in list(fields.items())]
    obj.save()
    return obj


class TxIsolationWarning(UserWarning):
    pass


def transaction_retry(max_retries=1):
    """Decorator for methods doing database operations.

    If the database operation fails, it will retry the operation
    at most ``max_retries`` times.

    """

    def _outer(fun):
        @wraps(fun)
        def _inner(*args, **kwargs):
            _max_retries = kwargs.pop("exception_retry_count", max_retries)
            for retries in count(0):
                try:
                    return fun(*args, **kwargs)
                except Exception:  # pragma: no cover
                    # Depending on the database backend used we can experience
                    # various exceptions. E.g. psycopg2 raises an exception
                    # if some operation breaks the transaction, so saving
                    # the task result won't be possible until we rollback
                    # the transaction.
                    if retries >= _max_retries:
                        raise
                    try:
                        rollback_unless_managed()
                    except Exception:
                        pass

        return _inner

    return _outer


class ExtendedQuerySet(QuerySet):
    def update_or_create(self, **kwargs):
        obj, created = self.get_or_create(**kwargs)

        if not created:
            fields = dict(kwargs.pop("defaults", {}))
            fields.update(kwargs)
            update_model_with_dict(obj, fields)

        return obj, created


class ExtendedManager(models.Manager):
    def get_queryset(self):
        return ExtendedQuerySet(self.model)

    get_query_set = get_queryset  # Pre django 1.6

    def update_or_create(self, **kwargs):
        return get_queryset(self).update_or_create(**kwargs)

    def connection_for_write(self):
        if connections:
            return connections[router.db_for_write(self.model)]
        return connection

    def connection_for_read(self):
        if connections:
            return connections[self.db]
        return connection

    def current_engine(self):
        try:
            return settings.DATABASES[self.db]["ENGINE"]
        except AttributeError:
            return settings.DATABASE_ENGINE


class ResultManager(ExtendedManager):
    def get_all_expired(self, expires):
        """Get all expired task results."""
        return self.filter(date_done__lt=now() - maybe_timedelta(expires))

    def delete_expired(self, expires):
        """Delete all expired taskset results."""
        meta = self.model._meta
        with commit_on_success():
            self.get_all_expired(expires).update(hidden=True)
            cursor = self.connection_for_write().cursor()
            cursor.execute(
                "DELETE FROM {0.db_table} WHERE hidden=%s".format(meta), (True,),
            )


class PeriodicTaskManager(ExtendedManager):
    def enabled(self):
        return self.filter(enabled=True)


class TaskManager(ResultManager):
    """Manager for :class:`celery.models.Task` models."""

    _last_id = None

    def get_task(self, task_id):
        """Get task meta for task by ``task_id``.

        :keyword exception_retry_count: How many times to retry by
            transaction rollback on exception. This could theoretically
            happen in a race condition if another worker is trying to
            create the same task. The default is to retry once.

        """
        try:
            return self.get(task_id=task_id)
        except self.model.DoesNotExist:
            if self._last_id == task_id:
                self.warn_if_repeatable_read()
            self._last_id = task_id
            return self.model(task_id=task_id)

    @transaction_retry(max_retries=2)
    def store_result(self, task_id, result, status, traceback=None, children=None):
        """Store the result and status of a task.

        :param task_id: task id

        :param result: The return value of the task, or an exception
            instance raised by the task.

        :param status: Task status. See
            :meth:`celery.result.AsyncResult.get_status` for a list of
            possible status values.

        :keyword traceback: The traceback at the point of exception (if the
            task failed).

        :keyword children: List of serialized results of subtasks
            of this task.

        :keyword exception_retry_count: How many times to retry by
            transaction rollback on exception. This could theoretically
            happen in a race condition if another worker is trying to
            create the same task. The default is to retry twice.

        """
        return self.update_or_create(
            task_id=task_id,
            defaults={"status": status, "result": result, "traceback": traceback, "meta": {"children": children}},
        )

    def warn_if_repeatable_read(self):
        if "mysql" in self.current_engine().lower():
            cursor = self.connection_for_read().cursor()
            if cursor.execute("SELECT @@tx_isolation"):
                isolation = cursor.fetchone()[0]
                if isolation == "REPEATABLE-READ":
                    warnings.warn(
                        TxIsolationWarning(
                            "Polling results with transaction isolation level "
                            "repeatable-read within the same transaction "
                            "may give outdated results. Be sure to commit the "
                            "transaction for each poll iteration."
                        )
                    )
