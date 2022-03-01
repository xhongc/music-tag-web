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

# 引擎内部配置模块


class Settings:
    """
    引擎全局配置对象
    """

    MAKO_SANDBOX_SHIELD_WORDS = [
        "ascii",
        "bytearray",
        "bytes",
        "callable",
        "chr",
        "classmethod",
        "compile",
        "delattr",
        "dir",
        "divmod",
        "exec",
        "eval",
        "filter",
        "frozenset",
        "getattr",
        "globals",
        "hasattr",
        "hash",
        "help",
        "id",
        "input",
        "isinstance",
        "issubclass",
        "iter",
        "locals",
        "map",
        "memoryview",
        "next",
        "object",
        "open",
        "print",
        "property",
        "repr",
        "setattr",
        "staticmethod",
        "super",
        "type",
        "vars",
        "__import__",
    ]

    MAKO_SANDBOX_IMPORT_MODULES = {}

    RERUN_INDEX_OFFSET = 0
