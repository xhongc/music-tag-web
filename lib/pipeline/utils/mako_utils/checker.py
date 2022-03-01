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


import ast
from typing import List

from mako import parsetree
from mako.exceptions import MakoException
from mako.lexer import Lexer

from .code_extract import MakoNodeCodeExtractor
from .exceptions import ForbiddenMakoTemplateException


def parse_template_nodes(
    nodes: List[parsetree.Node], node_visitor: ast.NodeVisitor, code_extractor: MakoNodeCodeExtractor,
):
    """
    解析mako模板节点，逐个节点解析抽象语法树并检查安全性
    :param nodes: mako模板节点列表
    :param node_visitor: 节点访问类，用于遍历AST节点
    :param code_extractor: Mako 词法节点处理器，用于提取 python 代码
    """
    for node in nodes:
        code = code_extractor.extract(node)
        if code is None:
            continue

        ast_node = ast.parse(code, "<unknown>", "exec")
        node_visitor.visit(ast_node)
        if hasattr(node, "nodes"):
            parse_template_nodes(node.nodes, node_visitor)


def check_mako_template_safety(text: str, node_visitor: ast.NodeVisitor, code_extractor: MakoNodeCodeExtractor) -> bool:
    """
    检查mako模板是否安全，若不安全直接抛出异常，安全则返回True
    :param text: mako模板内容
    :param node_visitor: 节点访问器，用于遍历AST节点
    """
    try:
        lexer_template = Lexer(text).parse()
    except MakoException as mako_error:
        raise ForbiddenMakoTemplateException("非mako模板，解析失败, {err_msg}".format(err_msg=mako_error.__class__.__name__))
    parse_template_nodes(lexer_template.nodes, node_visitor, code_extractor)
    return True
