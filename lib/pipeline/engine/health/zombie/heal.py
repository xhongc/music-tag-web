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

from django.utils.module_loading import import_string

from pipeline.conf import default_settings
from pipeline.engine.models import PipelineProcess

logger = logging.getLogger("celery")


def get_healer():
    if not default_settings.ENGINE_ZOMBIE_PROCESS_DOCTORS:
        logger.info("ENGINE_ZOMBIE_PROCESS_DOCTORS settings is empty, use dummy healer")
        return DummyZombieProcHealer()

    doctors = []

    for dr_setting in default_settings.ENGINE_ZOMBIE_PROCESS_DOCTORS:
        try:
            doctors.append(import_string(dr_setting["class"])(**dr_setting["config"]))
        except Exception:
            logger.exception("Error occurred when init doctor({}), skip".format(dr_setting))

    if not doctors:
        logger.info("All doctor init failed, use dummy healer")
        return DummyZombieProcHealer()

    return ZombieProcHealer(doctors=doctors)


class DummyZombieProcHealer(object):
    def heal(self):
        pass


class ZombieProcHealer(object):
    def __init__(self, doctors):
        self.doctors = doctors

    def heal(self):

        if not self.doctors:
            return

        proc_ids = self._get_process_ids()

        for proc_id in proc_ids:

            # get proc every time for latest state
            proc = PipelineProcess.objects.get(id=proc_id)

            if not proc.is_alive or proc.is_frozen:
                continue

            for dr in self.doctors:
                if dr.confirm(proc):
                    dr.cure(proc)
                    break

    def _get_process_ids(self):
        return PipelineProcess.objects.filter(is_alive=True, is_frozen=False).values_list("id", flat=True)
