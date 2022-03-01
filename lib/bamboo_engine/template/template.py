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

# 封装模板处理，渲染逻辑的相关模块

import copy
import re
import logging

from typing import Any, List, Set

from mako.template import Template as MakoTemplate
from mako import lexer, codegen
from mako.exceptions import MakoException

from bamboo_engine.utils.mako_utils.checker import check_mako_template_safety
from bamboo_engine.utils.mako_utils.exceptions import ForbiddenMakoTemplateException
from bamboo_engine.utils import mako_safety
from bamboo_engine.utils.string import deformat_var_key

from . import sandbox


logger = logging.getLogger("root")
# find mako template(format is ${xxx}，and ${}# not in xxx, # may raise memory error)
TEMPLATE_PATTERN = re.compile(r"\${[^${}#]+}")


class Template:
    def __init__(self, data: Any):
        self.data = data

    def get_reference(self, deformat=False) -> Set[str]:
        """
        获取当前数据中模板所引用的所有标志符

        :return: 标志符列表
        :rtype: List[str]
        """

        reference = []
        templates = self.get_templates()
        for tpl in templates:
            reference += self._get_template_reference(tpl)
        reference = set(reference)
        if not deformat:
            reference = {"${%s}" % r for r in reference}

        return reference

    def get_templates(self) -> List[str]:
        """
        获取当前数据中所有的模板片段

        :return: 模板片段列表
        :rtype: List[str]
        """
        templates = []
        data = self.data
        if isinstance(data, str):
            templates += self._get_string_templates(data)
        if isinstance(data, (list, tuple)):
            for item in data:
                templates += Template(item).get_templates()
        if isinstance(data, dict):
            for value in list(data.values()):
                templates += Template(value).get_templates()
        return list(set(templates))

    def render(self, context: dict) -> Any:
        """
        渲染当前模板

        :param context: 模板渲染上下文
        :type context: dict
        :return: 模板渲染后的数据
        :rtype: Any
        """
        data = self.data
        if isinstance(data, str):
            return self._render_string(data, context)
        if isinstance(data, list):
            ldata = [""] * len(data)
            for index, item in enumerate(data):
                ldata[index] = Template(copy.deepcopy(item)).render(context)
            return ldata
        if isinstance(data, tuple):
            ldata = [""] * len(data)
            for index, item in enumerate(data):
                ldata[index] = Template(copy.deepcopy(item)).render(context)
            return tuple(ldata)
        if isinstance(data, dict):
            for key, value in list(data.items()):
                data[key] = Template(copy.deepcopy(value)).render(context)
            return data
        return data

    def _get_string_templates(self, string) -> List[str]:
        return list(set(TEMPLATE_PATTERN.findall(string)))

    def _get_template_reference(self, template: str) -> List[str]:
        lex = lexer.Lexer(template)

        try:
            node = lex.parse()
        except MakoException as e:
            logger.warning("pipeline get template[{}] reference error[{}]".format(template, e))
            return []

        # Dummy compiler. _Identifiers class requires one
        # but only interested in the reserved_names field
        def compiler():
            return None

        compiler.reserved_names = set()
        identifiers = codegen._Identifiers(compiler, node)

        return list(identifiers.undeclared)

    def _render_string(self, string: str, context: dict) -> str:
        """
        使用特定上下文渲染指定模板

        :param string: 模板
        :type string: str
        :param context: 上下文
        :type context: dict
        :return: 渲染后的模板
        :rtype: str
        """
        if not isinstance(string, str):
            return string
        templates = self._get_string_templates(string)

        # TODO keep render return object, here only process simple situation
        if len(templates) == 1 and templates[0] == string and deformat_var_key(string) in context:
            return context[deformat_var_key(string)]

        for tpl in templates:
            try:
                check_mako_template_safety(
                    tpl,
                    mako_safety.SingleLineNodeVisitor(),
                    mako_safety.SingleLinCodeExtractor(),
                )
            except ForbiddenMakoTemplateException as e:
                logger.warning("forbidden template: {}, exception: {}".format(tpl, e))
                continue
            except Exception:
                logger.exception("{} safety check error.".format(tpl))
                continue
            resolved = Template._render_template(tpl, context)
            string = string.replace(tpl, resolved)
        return string

    @staticmethod
    def _render_template(template: str, context: dict) -> Any:
        """
        使用特定上下文渲染指定模板

        :param template: 模板
        :type template: Any
        :param context: 上下文
        :type context: dict
        :raises TypeError: [description]
        :return: [description]
        :rtype: str
        """
        data = {}
        data.update(sandbox.get())
        data.update(context)
        if not isinstance(template, str):
            raise TypeError("constant resolve error, template[%s] is not a string" % template)
        try:
            tm = MakoTemplate(template)
        except (MakoException, SyntaxError) as e:
            logger.error("pipeline resolve template[{}] error[{}]".format(template, e))
            return template
        try:
            resolved = tm.render_unicode(**data)
        except Exception as e:
            logger.warning("constant content({}) is invalid, data({}), error: {}".format(template, data, e))
            return template
        else:
            return resolved
