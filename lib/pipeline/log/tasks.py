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

import logging

from celery.decorators import periodic_task
from celery.schedules import crontab
from django.conf import settings

from pipeline.log.models import LogEntry

logger = logging.getLogger(__name__)


@periodic_task(run_every=(crontab(minute=0, hour=0)), ignore_result=True)
def clean_expired_log():
    expired_interval = getattr(settings, "LOG_PERSISTENT_DAYS", None)

    if expired_interval is None:
        expired_interval = 30
        logger.warning("LOG_PERSISTENT_DAYS are not found in settings, use default value: 30")

    del_num = LogEntry.objects.delete_expired_log(expired_interval)
    logger.info("%s log entry are deleted" % del_num)
