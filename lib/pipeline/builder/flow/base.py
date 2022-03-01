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

from pipeline.core.constants import PE
from pipeline.utils.uniqid import uniqid

__all__ = ["Element", "PE"]


class Element(object):
    def __init__(self, id=None, name=None, outgoing=None):
        self.id = id or uniqid()
        self.name = name
        self.outgoing = outgoing or []

    def extend(self, element):
        """
        build a connection from self to element and return element
        :param element: target
        :rtype: Element
        """
        self.outgoing.append(element)
        return element

    def connect(self, *args):
        """
        build connections from self to elements in args and return self
        :param args: target elements
        :rtype: Element
        """
        for e in args:
            self.outgoing.append(e)
        return self

    def converge(self, element):
        """
        converge all connection those diverge from self to element and return element
        :param element: target
        :rtype: Element
        """
        for e in self.outgoing:
            e.tail().connect(element)
        return element

    def to(self, element):
        return element

    def tail(self):
        """
        get tail element for self
        :rtype: Element
        """
        is_tail = len(self.outgoing) == 0
        e = self

        while not is_tail:
            e = e.outgoing[0]
            is_tail = len(e.outgoing) == 0

        return e

    def type(self):
        raise NotImplementedError()

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return "<{cls} {name}:{id}>".format(cls=type(self).__name__, name=self.name, id=self.id)
