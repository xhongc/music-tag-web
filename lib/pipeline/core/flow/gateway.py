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
from abc import ABCMeta

import ujson as json

from pipeline.core.constants import ESCAPED_CHARS
from pipeline.core.data.expression import ConstantTemplate, deformat_constant_key
from pipeline.core.flow.base import FlowNode
from pipeline.exceptions import ConditionExhaustedException, EvaluationException, InvalidOperationException
from pipeline.utils.boolrule import BoolRule

logger = logging.getLogger("pipeline_engine")


class Gateway(FlowNode, metaclass=ABCMeta):
    pass


class ExclusiveGateway(Gateway):
    def __init__(self, id, conditions=None, name=None, data=None):
        super(ExclusiveGateway, self).__init__(id, name, data)
        self.conditions = conditions or []

    def add_condition(self, condition):
        self.conditions.append(condition)

    def next(self, data=None):
        default_flow = self.outgoing.default_flow()
        next_flow = self._determine_next_flow_with_boolrule(data)

        if not next_flow:  # determine fail
            if not default_flow:  # try to use default flow
                raise ConditionExhaustedException(
                    "all conditions of branches are False " "while default flow is not appointed"
                )
            return default_flow.target

        return next_flow.target

    def target_for_sequence_flow(self, flow_id):
        flow_to_target = {c.sequence_flow.id: c.sequence_flow.target for c in self.conditions}
        if flow_id not in flow_to_target:
            raise InvalidOperationException("sequence flow(%s) does not exist." % flow_id)
        return flow_to_target[flow_id]

    @staticmethod
    def _transform_escape_char(string):
        """
        对未转义的字符串进行转义，现有的转义字符包括\n, \r, \t
        """
        if not isinstance(string, str):
            return string
        # 已转义的情况
        if len([c for c in ESCAPED_CHARS.values() if c in string]) > 0:
            return string
        for key, value in ESCAPED_CHARS.items():
            if key in string:
                string = string.replace(key, value)
        return string

    def _determine_next_flow_with_boolrule(self, data):
        """
        根据当前传入的数据判断下一个应该流向的 flow （ 不使用 eval 的版本）
        :param data:
        :return:
        """
        for key, value in data.items():
            data[key] = self._transform_escape_char(value)
        logger.info("[{}] ready to resolve conditions: {}".format(self.id, [c.evaluate for c in self.conditions]))
        for condition in self.conditions:
            deformatted_data = {deformat_constant_key(key): value for key, value in list(data.items())}
            try:
                logger.info("[{}] before resolve condition: {}".format(self.id, condition.evaluate))
                resolved_evaluate = ConstantTemplate(condition.evaluate).resolve_data(deformatted_data)
                logger.info("[{}] test {} with data {}".format(self.id, resolved_evaluate, data))
                result = BoolRule(resolved_evaluate).test(data)
                logger.info("[{}] {} test result: {}".format(self.id, resolved_evaluate, result))
            except Exception as e:
                raise EvaluationException(
                    "evaluate[%s] fail with data[%s] message: %s"
                    % (condition.evaluate, json.dumps(deformatted_data), e)
                )
            if result:
                return condition.sequence_flow

        return None

    def skip(self):
        return True


class ParallelGateway(Gateway):
    def __init__(self, id, converge_gateway_id, name=None, data=None):
        super(ParallelGateway, self).__init__(id, name, data)
        self.converge_gateway_id = converge_gateway_id

    def next(self):
        raise InvalidOperationException("can not determine next node for parallel gateway.")


class ConditionalParallelGateway(Gateway):
    def __init__(self, id, converge_gateway_id, conditions=None, name=None, data=None):
        super(ConditionalParallelGateway, self).__init__(id, name, data)
        self.converge_gateway_id = converge_gateway_id
        self.conditions = conditions or []

    def add_condition(self, condition):
        self.conditions.append(condition)

    def targets_meet_condition(self, data):

        targets = []

        logger.info("[{}] ready to resolve conditions: {}".format(self.id, [c.evaluate for c in self.conditions]))
        for condition in self.conditions:
            deformatted_data = {deformat_constant_key(key): value for key, value in list(data.items())}
            try:
                logger.info("[{}] before resolve condition: {}".format(self.id, condition.evaluate))
                resolved_evaluate = ConstantTemplate(condition.evaluate).resolve_data(deformatted_data)
                logger.info("[{}] test {} with data {}".format(self.id, resolved_evaluate, data))
                result = BoolRule(resolved_evaluate).test(data)
                logger.info("[{}] {} test result: {}".format(self.id, resolved_evaluate, result))
            except Exception as e:
                raise EvaluationException(
                    "evaluate[%s] fail with data[%s] message: %s"
                    % (condition.evaluate, json.dumps(deformatted_data), e)
                )
            if result:
                targets.append(condition.sequence_flow.target)

        if not targets:
            raise ConditionExhaustedException("all conditions of branches are False")

        return targets

    def target_for_sequence_flows(self, flow_ids):
        flow_to_target = {c.sequence_flow.id: c.sequence_flow.target for c in self.conditions}
        if not set(flow_ids).issubset(set(flow_to_target.keys())):
            not_exist_flow_ids = set(flow_ids) - set(flow_to_target.keys())
            raise InvalidOperationException(f"sequence flows {not_exist_flow_ids} does not exist.")
        return [flow_to_target[flow_id] for flow_id in flow_ids]

    def next(self):
        raise InvalidOperationException("can not determine next node for conditional parallel gateway.")

    def skip(self):
        return True


class ConvergeGateway(Gateway):
    def next(self):
        return self.outgoing.unique_one().target

    def skip(self):
        raise InvalidOperationException("can not skip conditional converge gateway.")


class Condition(object):
    def __init__(self, evaluate, sequence_flow):
        self.evaluate = evaluate
        self.sequence_flow = sequence_flow
