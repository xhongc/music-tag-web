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


class PipelineException(Exception):
    pass


class FlowTypeError(PipelineException):
    pass


class InvalidOperationException(PipelineException):
    pass


class ConditionExhaustedException(PipelineException):
    pass


class EvaluationException(PipelineException):
    pass


class NodeNotExistException(PipelineException):
    pass


class SourceKeyException(NodeNotExistException):
    pass


class VariableHydrateException(PipelineException):
    pass


class ParserException(PipelineException):
    pass


class SubprocessRefError(PipelineException):
    pass


class TemplateImportError(PipelineException):
    pass


class SubprocessExpiredError(PipelineException):
    pass


#
# data exception
#


class DataException(PipelineException):
    pass


class DataInitException(DataException):
    pass


class DataAttrException(DataException):
    pass


class DataTypeErrorException(DataException):
    pass


class CycleErrorException(DataException):
    pass


class ConnectionValidateError(DataException):
    def __init__(self, failed_nodes, detail, *args):
        self.failed_nodes = failed_nodes
        self.detail = detail
        super(ConnectionValidateError, self).__init__(*args)


class ConvergeMatchError(DataException):
    def __init__(self, gateway_id, *args):
        self.gateway_id = gateway_id
        super(ConvergeMatchError, self).__init__(*args)


class StreamValidateError(DataException):
    def __init__(self, node_id, *args):
        self.node_id = node_id
        super(StreamValidateError, self).__init__(*args)


class IsolateNodeError(DataException):
    pass


#
# component exception
#


class ComponentException(PipelineException):
    pass


class ComponentDataFormatException(ComponentException):
    pass


class ComponentNotExistException(ComponentException):
    pass


class ComponentDataLackException(ComponentDataFormatException):
    pass


#
# tag exception
#


class PipelineError(Exception):
    pass


class TagError(PipelineError):
    pass


class AttributeMissingError(TagError):
    pass


class AttributeValidationError(TagError):
    pass


#
# constant exception
#
class ConstantException(PipelineException):
    pass


class ConstantNotExistException(ConstantException):
    pass


class ConstantReferenceException(ConstantException):
    pass


class ConstantTypeException(ConstantException):
    pass


class ConstantSyntaxException(ConstantException):
    pass


#
# context exception
#
class ContextError(PipelineError):
    pass


class ReferenceNotExistError(ContextError):
    pass


class InsufficientVariableError(ContextError):
    pass


#
# periodic task exception
#
class InvalidCrontabException(PipelineException):
    pass
