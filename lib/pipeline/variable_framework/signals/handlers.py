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

from django.db.utils import ProgrammingError, OperationalError
from django.dispatch import receiver

from pipeline.core.data.var import LazyVariable
from pipeline.core.signals import pre_variable_register
from pipeline.variable_framework.models import VariableModel
from pipeline.variable_framework import context

logger = logging.getLogger("root")


@receiver(pre_variable_register, sender=LazyVariable)
def pre_variable_register_handler(sender, variable_cls, **kwargs):
    if context.skip_update_var_models():
        return

    try:
        print("update {} variable model".format(variable_cls.code))
        obj, created = VariableModel.objects.get_or_create(code=variable_cls.code, defaults={"status": __debug__})
        if not created and not obj.status:
            obj.status = True
            obj.save()
    except (ProgrammingError, OperationalError):
        # first migrate
        logger.exception("update variable model fail")
