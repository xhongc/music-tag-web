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

import logging
import weakref
from abc import ABCMeta, abstractmethod
from functools import wraps

from pipeline.exceptions import InvalidOperationException


def extra_inject(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        kwargs["extra"]["_id"] = args[0].id
        return func(*args, **kwargs)

    return wrapper


class FlowElement(object, metaclass=ABCMeta):
    def __init__(self, id, name=None):
        self.id = id
        self.name = name


class FlowNode(FlowElement, metaclass=ABCMeta):
    ON_RETRY = "_on_retry"

    def __init__(self, id, name=None, data=None):
        super(FlowNode, self).__init__(id, name)
        self.incoming = SequenceFlowCollection()
        self.outgoing = SequenceFlowCollection()
        self.data = data

    def on_retry(self):
        return hasattr(self, self.ON_RETRY)

    def next_exec_is_retry(self):
        setattr(self, self.ON_RETRY, True)

    def retry_at_current_exec(self):
        delattr(self, self.ON_RETRY)

    @abstractmethod
    def next(self):
        """
        该节点的下一个节点，由子类来实现
        :return:
        """
        raise NotImplementedError()

    class FlowNodeLogger:
        def __init__(self, id):
            self.id = id
            self._logger = logging.getLogger("pipeline.logging")

        @extra_inject
        def info(self, *args, **kwargs):
            self._logger.info(*args, **kwargs)

        @extra_inject
        def warning(self, *args, **kwargs):
            self._logger.warning(*args, **kwargs)

        @extra_inject
        def error(self, *args, **kwargs):
            self._logger.error(*args, **kwargs)

        @extra_inject
        def critical(self, *args, **kwargs):
            self._logger.critical(*args, **kwargs)

    @property
    def logger(self):
        _logger = getattr(self, "_logger", None)
        if not _logger:
            _logger = self.FlowNodeLogger(self.id)
            setattr(self, "_logger", _logger)
        return _logger

    def __getstate__(self):
        if "_logger" in self.__dict__:
            del self.__dict__["_logger"]
        return self.__dict__


class SequenceFlow(FlowElement):
    def __init__(self, id, source, target, is_default=False, name=None):
        super(SequenceFlow, self).__init__(id, name)
        self.source = weakref.proxy(source) if source is not None else source
        self.target = weakref.proxy(target) if target is not None else target
        self.is_default = is_default


class SequenceFlowCollection(object):
    def __init__(self, *flows):
        flow_dict = {}
        for flow in flows:
            flow_dict[flow.id] = flow

        self.flows = list(flows)
        self.flow_dict = flow_dict

    def get_flow(self, id):
        """
        获取 flow.id = id 的某个 flow
        :param id: flow id
        :return:
        """
        return self.flow_dict.get(id)

    def unique_one(self):
        """
        获取唯一的一个 flow，若当前集合内 flow 不只一条则抛出异常
        :return:
        """
        if len(self.flows) != 1:
            raise InvalidOperationException("this collection contains multiple flow, can not get unique one.")
        return self.flows[0]

    def is_empty(self):
        """
        当前集合是否为空
        :return:
        """
        return len(self.flows) == 0

    def default_flow(self):
        """
        获取当前集合中默认的 flow
        :return: 若存在默认的 flow 则返回，否则返回 None
        """
        for flow in self.flows:
            if flow.is_default:
                return flow
        return None

    def add_flow(self, flow):
        """
        向当前结合中添加一条 flow
        :param flow: 待添加的 flow
        :return:
        """
        self.flows.append(flow)
        self.flow_dict[flow.id] = flow

    def all_target_node(self):
        """
        返回当前集合中所有 flow 的 target
        :return:
        """
        nodes = []
        for flow in self.flows:
            nodes.append(flow.target)
        return nodes

    def all_source_node(self):
        """
        返回当前集合中所有 flow 的 source
        :return:
        """
        nodes = []
        for flow in self.flows:
            nodes.append(flow.source)
        return nodes

    def __iter__(self):
        return iter(self.flows)
