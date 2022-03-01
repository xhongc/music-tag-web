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
from pipeline.utils.collections import FancyDict


class Data(object):
    def __init__(self, inputs=None, outputs=None):
        self.inputs = FancyDict(inputs or {})
        self.outputs = outputs or []

    def to_dict(self):
        base = {"inputs": {}, "outputs": self.outputs}

        for key, value in list(self.inputs.items()):
            base["inputs"][key] = value.to_dict() if isinstance(value, Var) else value

        return base


class Params(object):
    def __init__(self, params=None):
        self.params = FancyDict(params or {})

    def to_dict(self):
        base = {}

        for key, value in list(self.params.items()):
            base[key] = value.to_dict() if isinstance(value, Var) else value

        return base


class Var(object):
    PLAIN = PE.plain
    SPLICE = PE.splice
    LAZY = PE.lazy

    def __init__(self, type, value, custom_type=None):
        self.type = type
        self.value = value
        self.custom_type = custom_type

    def to_dict(self):
        base = {"type": self.type, "value": self.value}
        if self.type == self.LAZY:
            base["custom_type"] = self.custom_type

        return base


class DataInput(Var):
    def __init__(self, *args, **kwargs):
        super(DataInput, self).__init__(*args, **kwargs)

    def to_dict(self):
        base = super(DataInput, self).to_dict()
        base["is_param"] = True
        return base


class NodeOutput(Var):
    def __init__(self, source_act, source_key, *args, **kwargs):
        self.source_act = source_act
        self.source_key = source_key
        kwargs["value"] = None
        super(NodeOutput, self).__init__(*args, **kwargs)

    def to_dict(self):
        base = super(NodeOutput, self).to_dict()
        base["source_act"] = self.source_act
        base["source_key"] = self.source_key
        return base


class RewritableNodeOutput(Var):
    def __init__(self, source_act, *args, **kwargs):
        self.source_act = source_act
        kwargs["value"] = None
        super(RewritableNodeOutput, self).__init__(*args, **kwargs)

    def to_dict(self):
        base = super(RewritableNodeOutput, self).to_dict()
        base["source_act"] = self.source_act
        return base
