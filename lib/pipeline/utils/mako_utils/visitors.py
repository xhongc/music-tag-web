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

import _ast
import ast

from django.utils.module_loading import import_string

from .exceptions import ForbiddenMakoTemplateException


class StrictNodeVisitor(ast.NodeVisitor):
    """
    遍历语法树节点，遇到魔术方法使用或import时，抛出异常
    """

    BLACK_LIST_MODULE_METHODS = {
        "os": dir(__import__("os")),
        "subprocess": dir(__import__("subprocess")),
        "shutil": dir(__import__("shutil")),
        "ctypes": dir(__import__("ctypes")),
        "codecs": dir(__import__("codecs")),
        "sys": dir(__import__("sys")),
        "socket": dir(__import__("socket")),
        "webbrowser": dir(__import__("webbrowser")),
        "threading": dir(__import__("threading")),
        "sqlite3": dir(__import__("threading")),
        "signal": dir(__import__("signal")),
        "imaplib": dir(__import__("imaplib")),
        "fcntl": dir(__import__("fcntl")),
        "pdb": dir(__import__("pdb")),
        "pty": dir(__import__("pty")),
        "glob": dir(__import__("glob")),
        "tempfile": dir(__import__("tempfile")),
        "types": dir(import_string("types.CodeType")) + dir(import_string("types.FrameType")),
        "builtins": [
            "getattr",
            "hasattr",
            "breakpoint",
            "compile",
            "delattr",
            "open",
            "eval",
            "exec",
            "execfile",
            "exit",
            "dir",
            "globals",
            "locals",
            "input",
            "iter",
            "next",
            "quit",
            "setattr",
            "vars",
            "memoryview",
            "super",
            "print",
        ],
    }

    BLACK_LIST_METHODS = []
    for module_name, methods in BLACK_LIST_MODULE_METHODS.items():
        BLACK_LIST_METHODS.append(module_name)
        BLACK_LIST_METHODS.extend(methods)
    BLACK_LIST_METHODS = set(BLACK_LIST_METHODS)

    WHITE_LIST_MODULES = ["datetime", "re", "random", "json", "math"]

    def __init__(self, black_list_methods=None, white_list_modules=None):
        self.black_list_methods = black_list_methods or self.BLACK_LIST_METHODS
        self.white_list_modules = white_list_modules or self.WHITE_LIST_MODULES

    @staticmethod
    def is_white_list_ast_obj(ast_obj: _ast.AST) -> bool:
        """
        判断是否白名单对象，特殊豁免
        :param ast_obj: 抽象语法树节点
        :return: bool
        """
        # re 正则表达式允许使用 compile
        if isinstance(ast_obj, _ast.Attribute) and isinstance(ast_obj.value, _ast.Name):
            if ast_obj.value.id == "re" and ast_obj.attr in ["compile"]:
                return True

        return False

    def visit_Attribute(self, node):
        if self.is_white_list_ast_obj(node):
            return

        if node.attr in self.black_list_methods or node.attr.startswith("_"):
            raise ForbiddenMakoTemplateException("Mako template forbidden.")

    def visit_Name(self, node):
        if node.id in self.black_list_methods or node.id.startswith("_"):
            raise ForbiddenMakoTemplateException("Mako template forbidden.")

    def visit_Import(self, node):
        for name in node.names:
            if name.name not in self.white_list_modules:
                raise ForbiddenMakoTemplateException("Mako template forbidden.")

    def visit_ImportFrom(self, node):
        self.visit_Import(node)
