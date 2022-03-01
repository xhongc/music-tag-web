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

from pipeline import exceptions
from pipeline.core.data.var import PlainVariable, SpliceVariable, Variable
from pipeline.core.data import library


def get_variable(key, info, context, pipeline_data):
    if isinstance(info["value"], Variable):
        variable = info["value"]
    else:
        if info.get("type", "plain") == "plain":
            variable = PlainVariable(key, info["value"])
        elif info["type"] == "splice":
            variable = SpliceVariable(key, info["value"], context)
        elif info["type"] == "lazy":
            variable = library.VariableLibrary.get_var_class(info["custom_type"])(
                key, info["value"], context, pipeline_data
            )
        else:
            raise exceptions.DataTypeErrorException(
                "Unknown type: %s, which should be one of [plain, splice, lazy]" % info["type"]
            )
    return variable
