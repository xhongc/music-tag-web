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
from collections import namedtuple
from datetime import datetime

import pytz
from celery import schedules
from celery.utils.time import is_naive, make_aware

schedstate = namedtuple("schedstate", ("is_due", "next"))
logger = logging.getLogger("celery")


class TzAwareCrontab(schedules.crontab):
    """Timezone Aware Crontab."""

    def __init__(
        self, minute="*", hour="*", day_of_week="*", day_of_month="*", month_of_year="*", tz=pytz.utc, app=None,
    ):
        """Overwrite Crontab constructor to include a timezone argument."""
        self.tz = tz

        nowfun = self.nowfunc

        super(TzAwareCrontab, self).__init__(
            minute=minute,
            hour=hour,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
            month_of_year=month_of_year,
            nowfun=nowfun,
            app=app,
        )

    def nowfunc(self):
        return self.tz.normalize(pytz.utc.localize(datetime.utcnow()))

    def is_due(self, last_run_at):
        """Calculate when the next run will take place.
        Return tuple of (is_due, next_time_to_check).
        The last_run_at argument needs to be timezone aware.
        """
        logger.debug("################### is_due begin ###################")
        logger.debug("native last_run_at: %s" % last_run_at)

        last_run_at = last_run_at.astimezone(self.tz)

        now = datetime.now(self.tz)
        logger.debug("last_run_at: %s" % last_run_at)
        logger.debug("now: %s" % now)

        rem_delta = self.remaining_estimate(last_run_at)

        logger.debug("rem_delta: %s" % rem_delta)
        logger.debug("next run at: %s" % (now + rem_delta))

        rem = max(rem_delta.total_seconds(), 0)
        due = rem == 0
        if due:
            rem_delta = self.remaining_estimate(self.now())
            rem = max(rem_delta.total_seconds(), 0)

        logger.debug("self: %s" % self)
        logger.debug("due: {} {} {}".format(self.tz, due, rem))
        logger.debug("################### is_due end ###################")
        return schedstate(due, rem)

    # Needed to support pickling
    def __repr__(self):
        return (
            "<crontab: {0._orig_minute} {0._orig_hour} {0._orig_day_of_week} {0._orig_day_of_month} "
            "{0._orig_month_of_year} (m/h/d/dM/MY), {0.tz}>".format(self)
        )

    def __reduce__(self):
        return (
            self.__class__,
            (
                self._orig_minute,
                self._orig_hour,
                self._orig_day_of_week,
                self._orig_day_of_month,
                self._orig_month_of_year,
                self.tz,
            ),
            None,
        )

    def __eq__(self, other):
        if isinstance(other, schedules.crontab):
            return (
                other.month_of_year == self.month_of_year
                and other.day_of_month == self.day_of_month
                and other.day_of_week == self.day_of_week
                and other.hour == self.hour
                and other.minute == self.minute
                and other.tz == self.tz
            )
        return NotImplemented

    def maybe_make_aware(self, dt):
        if not is_naive(dt):
            return dt
        return make_aware(dt, self.tz)

    def to_local(self, dt):
        return self.maybe_make_aware(dt)
