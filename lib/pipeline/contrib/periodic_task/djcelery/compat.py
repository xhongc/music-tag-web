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

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


def python_2_unicode_compatible(cls):
    """Taken from Django project (django/utils/encoding.py) & modified a bit to
    always have __unicode__ method available.
    """
    if "__str__" not in cls.__dict__:
        raise ValueError(
            "@python_2_unicode_compatible cannot be applied "
            "to %s because it doesn't define __str__()." % cls.__name__
        )

    cls.__unicode__ = cls.__str__

    if PY2:
        cls.__str__ = lambda self: self.__unicode__().encode("utf-8")

    return cls
