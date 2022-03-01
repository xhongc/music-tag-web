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


# 引擎内部状态及状态相关数据定义模块


from enum import Enum

from .utils.collections import ConstantDict


class StateType(Enum):
    CREATED = "CREATED"
    READY = "READY"
    RUNNING = "RUNNING"
    SUSPENDED = "SUSPENDED"
    BLOCKED = "BLOCKED"
    FINISHED = "FINISHED"
    FAILED = "FAILED"
    REVOKED = "REVOKED"


CREATED = StateType.CREATED.value
READY = StateType.READY.value
RUNNING = StateType.RUNNING.value
SUSPENDED = StateType.SUSPENDED.value
BLOCKED = StateType.BLOCKED.value
FINISHED = StateType.FINISHED.value
FAILED = StateType.FAILED.value
REVOKED = StateType.REVOKED.value

ALL_STATES = frozenset([READY, RUNNING, SUSPENDED, BLOCKED, FINISHED, FAILED, REVOKED])

ARCHIVED_STATES = frozenset([FINISHED, FAILED, REVOKED])
SLEEP_STATES = frozenset([SUSPENDED, REVOKED])
CHILDREN_IGNORE_STATES = frozenset([BLOCKED])

INVERTED_TRANSITION = ConstantDict({RUNNING: frozenset([READY, FINISHED])})

TRANSITION = ConstantDict(
    {
        READY: frozenset([RUNNING, SUSPENDED]),
        RUNNING: frozenset([FINISHED, FAILED, REVOKED, SUSPENDED]),
        SUSPENDED: frozenset([READY, REVOKED, RUNNING]),
        BLOCKED: frozenset([]),
        FINISHED: frozenset([RUNNING, FAILED]),
        FAILED: frozenset([READY, FINISHED]),
        REVOKED: frozenset([]),
    }
)


def can_transit(from_state, to_state):

    if from_state in TRANSITION:
        if to_state in TRANSITION[from_state]:
            return True
    return False
