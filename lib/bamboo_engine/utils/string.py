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

# 字符串处理类工具


import uuid

ESCAPED_CHARS = {"\n": r"\n", "\r": r"\r", "\t": r"\t"}


def transform_escape_char(string: str) -> str:
    """
    对未转义的字符串进行转义，现有的转义字符包括\n, \r, \t
    """
    if not isinstance(string, str):
        return string
    # 已转义的情况
    if len([c for c in ESCAPED_CHARS.values() if c in string]) > 0:
        return string
    for key, value in ESCAPED_CHARS.items():
        if key in string:
            string = string.replace(key, value)
    return string


def format_var_key(key: str) -> str:
    """
    format key to ${key}

    :param key: key
    :type key: str
    :return: format key
    :rtype: str
    """
    return "${%s}" % key


def deformat_var_key(key: str) -> str:
    """
    deformat ${key} to key

    :param key: key
    :type key: str
    :return: deformat key
    :rtype: str
    """
    return key[2:-1]


def unique_id(prefix: str) -> str:
    if len(prefix) != 1:
        raise ValueError("prefix length must be 1")

    return "{}{}".format(prefix, uuid.uuid4().hex)


def get_lower_case_name(text: str) -> str:
    lst = []
    for index, char in enumerate(text):
        if char.isupper() and index != 0:
            lst.append("_")
        lst.append(char)

    return "".join(lst).lower()
