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

PIPELINE_TREE_PARSER = {
    "type": "object",
    "properties": {
        "data": {"type": "object", "properties": {"inputs": {"type": "object"}, "outputs": {"type": "object"}}},
        "activities": {"type": "object"},
        "end_event": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "incoming": {"type": "string"},
                "name": {"type": "string"},
                "outgoing": {"type": "string"},
                "type": {"type": "string"},
            },
        },
        "flows": {"type": "object"},
        "gateways": {"type": "object"},
        "id": {"type": "string"},
        "line": {"type": "array"},
        "location": {"type": "array"},
        "start_event": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "incoming": {"type": "string"},
                "name": {"type": "string"},
                "outgoing": {"type": "string"},
                "type": {"type": "string"},
            },
        },
    },
}
