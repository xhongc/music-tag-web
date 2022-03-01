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
import traceback
from abc import ABCMeta, abstractmethod

from pipeline.core.flow.base import FlowNode
from pipeline.core.pipeline import Pipeline
from pipeline.engine.signals import pipeline_end

logger = logging.getLogger("celery")


class Event(FlowNode, metaclass=ABCMeta):
    def __init__(self, id, name=None, data=None):
        super(Event, self).__init__(id, name, data)

    def next(self):
        return self.outgoing.unique_one().target


class ThrowEvent(Event, metaclass=ABCMeta):
    pass


class CatchEvent(Event, metaclass=ABCMeta):
    pass


class EndEvent(ThrowEvent, metaclass=ABCMeta):
    def pipeline_finish(self, root_pipeline_id):
        try:
            pipeline_end.send(sender=Pipeline, root_pipeline_id=root_pipeline_id)
        except Exception:
            logger.error("pipeline end handler error %s" % traceback.format_exc())


class StartEvent(CatchEvent, metaclass=ABCMeta):
    pass


class EmptyStartEvent(StartEvent):
    pass


class EmptyEndEvent(EndEvent):
    pass


class ExecutableEndEvent(EndEvent, metaclass=ABCMeta):
    @abstractmethod
    def execute(self, in_subprocess, root_pipeline_id, current_pipeline_id):
        raise NotImplementedError()
