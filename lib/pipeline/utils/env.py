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

import sys
import traceback

DJANGO_MANAGE_CMD = "manage.py"


def get_django_command():
    if sys.argv and sys.argv[0] == DJANGO_MANAGE_CMD:
        try:
            return sys.argv[1]
        except Exception:
            print(
                "get django start up command error with argv: {argv}, traceback: {traceback}".format(
                    argv=sys.argv, traceback=traceback.format_exc()
                )
            )

            return None

    return None
