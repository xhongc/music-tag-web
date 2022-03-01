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

import copy
import re
import logging

from mako.template import Template
from mako import lexer, codegen
from mako.exceptions import MakoException

from pipeline import exceptions
from pipeline.conf.default_settings import MAKO_SAFETY_CHECK
from pipeline.core.data.sandbox import SANDBOX
from pipeline.core.data import mako_safety
from pipeline.utils.mako_utils.checker import check_mako_template_safety
from pipeline.utils.mako_utils.exceptions import ForbiddenMakoTemplateException


logger = logging.getLogger("root")
# find mako template(format is ${xxx}，and ${}# not in xxx, # may raise memory error)
TEMPLATE_PATTERN = re.compile(r"\${[^$#]+}")


def format_constant_key(key):
    """
    @summary: format key to ${key}
    @param key:
    @return:
    """
    return "${%s}" % key


def deformat_constant_key(key):
    """
    @summary: deformat ${key} to key
    @param key:
    @return:
    """
    return key[2:-1]


class ConstantTemplate(object):
    def __init__(self, data):
        self.data = data

    def get_reference(self):
        reference = []
        templates = self.get_templates()
        for tpl in templates:
            reference += self.get_template_reference(tpl)
        reference = list(set(reference))
        return reference

    def get_templates(self):
        templates = []
        data = self.data
        if isinstance(data, str):
            templates += self.get_string_templates(data)
        if isinstance(data, (list, tuple)):
            for item in data:
                templates += ConstantTemplate(item).get_templates()
        if isinstance(data, dict):
            for value in list(data.values()):
                templates += ConstantTemplate(value).get_templates()
        return list(set(templates))

    def resolve_data(self, value_maps):
        data = self.data
        if isinstance(data, str):
            return self.resolve_string(data, value_maps)
        if isinstance(data, list):
            ldata = [""] * len(data)
            for index, item in enumerate(data):
                ldata[index] = ConstantTemplate(copy.deepcopy(item)).resolve_data(value_maps)
            return ldata
        if isinstance(data, tuple):
            ldata = [""] * len(data)
            for index, item in enumerate(data):
                ldata[index] = ConstantTemplate(copy.deepcopy(item)).resolve_data(value_maps)
            return tuple(ldata)
        if isinstance(data, dict):
            for key, value in list(data.items()):
                data[key] = ConstantTemplate(copy.deepcopy(value)).resolve_data(value_maps)
            return data
        return data

    @staticmethod
    def get_string_templates(string):
        return list(set(TEMPLATE_PATTERN.findall(string)))

    @staticmethod
    def get_template_reference(template):
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

    @staticmethod
    def resolve_string(string, value_maps):
        if not isinstance(string, str):
            return string
        templates = ConstantTemplate.get_string_templates(string)

        # TODO keep render return object, here only process simple situation
        if len(templates) == 1 and templates[0] == string and deformat_constant_key(string) in value_maps:
            return value_maps[deformat_constant_key(string)]

        for tpl in templates:
            if MAKO_SAFETY_CHECK:
                try:
                    check_mako_template_safety(
                        tpl, mako_safety.SingleLineNodeVisitor(), mako_safety.SingleLinCodeExtractor()
                    )
                except ForbiddenMakoTemplateException as e:
                    logger.warning("forbidden template: {}, exception: {}".format(tpl, e))
                    continue
                except Exception:
                    logger.exception("{} safety check error.".format(tpl))
                    continue
            resolved = ConstantTemplate.resolve_template(tpl, value_maps)
            string = string.replace(tpl, resolved)
        return string

    @staticmethod
    def resolve_template(template, value_maps):
        data = {}
        data.update(SANDBOX)
        data.update(value_maps)
        if not isinstance(template, str):
            raise exceptions.ConstantTypeException("constant resolve error, template[%s] is not a string" % template)
        try:
            tm = Template(template)
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
