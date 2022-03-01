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
from pipeline.validators.connection import (
    validate_graph_connection,
    validate_graph_without_circle,
)
from pipeline.validators.gateway import validate_gateways, validate_stream
from pipeline.validators.utils import format_pipeline_tree_io_to_list


def validate_pipeline_tree(pipeline_tree, cycle_tolerate=False):
    format_pipeline_tree_io_to_list(pipeline_tree)
    # 1. connection validation
    try:
        validate_graph_connection(pipeline_tree)
    except exceptions.ConnectionValidateError as e:
        raise exceptions.ParserException(e.detail)

    # do not tolerate circle in flow
    if not cycle_tolerate:
        no_cycle = validate_graph_without_circle(pipeline_tree)
        if not no_cycle["result"]:
            raise exceptions.ParserException(no_cycle["message"])

    # 2. gateway validation
    validate_gateways(pipeline_tree)

    # 3. stream validation
    validate_stream(pipeline_tree)
