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

from pipeline.conf import settings
from pipeline.utils import env

UPDATE_TRIGGER = "update_variable_models"


def skip_update_var_models():
    if settings.AUTO_UPDATE_VARIABLE_MODELS:
        return False

    django_command = env.get_django_command()
    if django_command is None:
        return True

    return django_command != UPDATE_TRIGGER
