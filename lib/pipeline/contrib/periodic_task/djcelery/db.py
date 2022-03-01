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

from contextlib import contextmanager

import django
from django.db import transaction

if django.VERSION < (1, 6):  # pragma: no cover

    def get_queryset(s):
        return s.get_query_set()


else:

    def get_queryset(s):  # noqa
        return s.get_queryset()


try:
    from django.db.transaction import atomic  # noqa
except ImportError:  # pragma: no cover

    try:
        from django.db.transaction import Transaction  # noqa
    except ImportError:

        @contextmanager
        def commit_on_success(*args, **kwargs):
            try:
                transaction.enter_transaction_management(*args, **kwargs)
                transaction.managed(True, *args, **kwargs)
                try:
                    yield
                except Exception:
                    if transaction.is_dirty(*args, **kwargs):
                        transaction.rollback(*args, **kwargs)
                    raise
                else:
                    if transaction.is_dirty(*args, **kwargs):
                        try:
                            transaction.commit(*args, **kwargs)
                        except Exception:
                            transaction.rollback(*args, **kwargs)
                            raise
            finally:
                transaction.leave_transaction_management(*args, **kwargs)

    else:  # pragma: no cover
        from django.db.transaction import commit_on_success  # noqa

    commit_unless_managed = transaction.commit_unless_managed
    rollback_unless_managed = transaction.rollback_unless_managed
else:

    @contextmanager
    def commit_on_success(using=None):  # noqa
        connection = transaction.get_connection(using)
        if connection.features.autocommits_when_autocommit_is_off:
            # ignore stupid warnings and errors
            yield
        else:
            with transaction.atomic(using):
                yield

    def commit_unless_managed(*args, **kwargs):  # noqa
        pass

    def rollback_unless_managed(*args, **kwargs):  # noqa
        pass
