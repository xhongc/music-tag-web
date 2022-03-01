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

# 异常定义模块


class EngineException(Exception):
    pass


class InvalidOperationError(EngineException):
    pass


class NotFoundError(EngineException):
    pass


class ValueError(EngineException):
    pass


class StateVersionNotMatchError(EngineException):
    pass


class TreeInvalidException(EngineException):
    pass


class ConnectionValidateError(TreeInvalidException):
    def __init__(self, failed_nodes, detail, *args):
        self.failed_nodes = failed_nodes
        self.detail = detail
        super(ConnectionValidateError, self).__init__(*args)


class ConvergeMatchError(TreeInvalidException):
    def __init__(self, gateway_id, *args):
        self.gateway_id = gateway_id
        super(ConvergeMatchError, self).__init__(*args)


class StreamValidateError(TreeInvalidException):
    def __init__(self, node_id, *args):
        self.node_id = node_id
        super(StreamValidateError, self).__init__(*args)


class IsolateNodeError(TreeInvalidException):
    pass
