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

# mock str return value of Built-in Functions，make str(func) return "func" rather than "<built-in function func>"

import builtins
import importlib

from pipeline.conf import default_settings

SANDBOX = {}


class MockStrMeta(type):
    def __new__(cls, name, bases, attrs):
        new_cls = super(MockStrMeta, cls).__new__(cls, name, bases, attrs)
        SANDBOX.update({new_cls.str_return: new_cls})
        return new_cls

    def __str__(cls):
        return cls.str_return

    def __call__(cls, *args, **kwargs):
        return cls.call(*args, **kwargs)


def _shield_words(sandbox, words):
    for shield_word in words:
        sandbox[shield_word] = None


class ModuleObject:
    def __init__(self, sub_paths, module):
        if len(sub_paths) == 1:
            setattr(self, sub_paths[0], module)
            return
        setattr(self, sub_paths[0], ModuleObject(sub_paths[1:], module))


def _import_modules(sandbox, modules):
    for mod_path, alias in modules.items():
        mod = importlib.import_module(mod_path)
        sub_paths = alias.split(".")
        if len(sub_paths) == 1:
            sandbox[alias] = mod
        else:
            sandbox[sub_paths[0]] = ModuleObject(sub_paths[1:], mod)


def _mock_builtins():
    """
    @summary: generate mock class of built-in functions like id,int
    """
    for func_name in dir(builtins):
        if func_name.lower() == func_name and not func_name.startswith("_"):
            new_func_name = "Mock{}".format(func_name.capitalize())
            MockStrMeta(new_func_name, (object,), {"call": getattr(builtins, func_name), "str_return": func_name})


_mock_builtins()

_shield_words(SANDBOX, default_settings.MAKO_SANDBOX_SHIELD_WORDS)

_import_modules(SANDBOX, default_settings.MAKO_SANDBOX_IMPORT_MODULES)
