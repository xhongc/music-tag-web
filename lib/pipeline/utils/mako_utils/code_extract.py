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

import abc

from mako import parsetree
from mako.ast import PythonFragment

from .exceptions import ForbiddenMakoTemplateException


class MakoNodeCodeExtractor(object):
    @abc.abstractmethod
    def extract(self, node):
        """处理 Mako Lexer 分割出来的 code 对象，返回需要检测的 python 代码，返回 None 表示该节点不需要处理

        :param node: mako parsetree node
        :return: 需要处理的代码，或 None
        """
        raise NotImplementedError()


class StrictMakoNodeCodeExtractor(MakoNodeCodeExtractor):
    def extract(self, node):
        if isinstance(node, parsetree.Code) or isinstance(node, parsetree.Expression):
            return node.text
        elif isinstance(node, parsetree.ControlLine):
            if node.isend:
                return None
            return PythonFragment(node.text).code
        elif isinstance(node, parsetree.Text):
            return None
        else:
            raise ForbiddenMakoTemplateException("不支持[{}]节点".format(node.__class__.__name__))
