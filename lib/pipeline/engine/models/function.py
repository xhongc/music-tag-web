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
import traceback

from django.db import models
from django.utils.translation import ugettext_lazy as _

from pipeline.engine.conf import function_switch

logger = logging.getLogger("celery")


class FunctionSwitchManager(models.Manager):
    def init_db(self):
        try:
            name_set = {s.name for s in self.all()}
            s_to_be_created = []
            for switch in function_switch.switch_list:
                if switch["name"] not in name_set:
                    s_to_be_created.append(
                        FunctionSwitch(
                            name=switch["name"], description=switch["description"], is_active=switch["is_active"]
                        )
                    )
                else:
                    self.filter(name=switch["name"]).update(description=switch["description"])
            self.bulk_create(s_to_be_created)
        except Exception:
            logger.error("function switch init failed: %s" % traceback.format_exc())

    def is_frozen(self):
        return self.get(name=function_switch.FREEZE_ENGINE).is_active

    def freeze_engine(self):
        self.filter(name=function_switch.FREEZE_ENGINE).update(is_active=True)

    def unfreeze_engine(self):
        self.filter(name=function_switch.FREEZE_ENGINE).update(is_active=False)


class FunctionSwitch(models.Model):
    name = models.CharField(_("功能名称"), max_length=32, null=False, unique=True)
    description = models.TextField(_("功能描述"), default="")
    is_active = models.BooleanField(_("是否激活"), default=False)

    objects = FunctionSwitchManager()
