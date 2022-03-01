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

from pipeline.engine.utils import ConstantDict

CREATED = "CREATED"
READY = "READY"
RUNNING = "RUNNING"
SUSPENDED = "SUSPENDED"
BLOCKED = "BLOCKED"
FINISHED = "FINISHED"
FAILED = "FAILED"
REVOKED = "REVOKED"
EXPIRED = "EXPIRED"

ALL_STATES = frozenset([READY, RUNNING, SUSPENDED, BLOCKED, FINISHED, FAILED, REVOKED])

ARCHIVED_STATES = frozenset([FINISHED, FAILED, REVOKED])
SLEEP_STATES = frozenset([SUSPENDED, REVOKED])
CHILDREN_IGNORE_STATES = frozenset([BLOCKED])

_NODE_TRANSITION = ConstantDict(
    {
        READY: frozenset([RUNNING, SUSPENDED]),
        RUNNING: frozenset([FINISHED, FAILED]),
        SUSPENDED: frozenset([READY, REVOKED]),
        BLOCKED: frozenset([]),
        FINISHED: frozenset([RUNNING, FAILED]),
        FAILED: frozenset([]),
        REVOKED: frozenset([]),
    }
)

_PIPELINE_TRANSITION = ConstantDict(
    {
        READY: frozenset([RUNNING, SUSPENDED, BLOCKED]),
        RUNNING: frozenset([SUSPENDED, BLOCKED, FINISHED, FAILED]),
        SUSPENDED: frozenset([READY, REVOKED, BLOCKED]),
        BLOCKED: frozenset([READY, REVOKED]),
        FINISHED: frozenset([RUNNING]),
        FAILED: frozenset([]),
        REVOKED: frozenset([]),
    }
)

_APPOINT_PIPELINE_TRANSITION = ConstantDict(
    {
        READY: frozenset([SUSPENDED, REVOKED]),
        RUNNING: frozenset([SUSPENDED, REVOKED]),
        SUSPENDED: frozenset([READY, REVOKED, RUNNING]),
        BLOCKED: frozenset([REVOKED]),
        FINISHED: frozenset([]),
        FAILED: frozenset([REVOKED]),
        REVOKED: frozenset([]),
    }
)

_APPOINT_NODE_TRANSITION = ConstantDict(
    {
        READY: frozenset([SUSPENDED]),
        RUNNING: frozenset([]),
        SUSPENDED: frozenset([READY]),
        BLOCKED: frozenset([]),
        FINISHED: frozenset([]),
        FAILED: frozenset([READY, FINISHED]),
        REVOKED: frozenset([]),
    }
)

TRANSITION_MAP = {
    # first level: is_pipeline
    True: {
        # second level: appoint
        True: _APPOINT_PIPELINE_TRANSITION,
        False: _PIPELINE_TRANSITION,
    },
    False: {True: _APPOINT_NODE_TRANSITION, False: _NODE_TRANSITION},
}


def can_transit(from_state, to_state, is_pipeline=False, appoint=False):
    transition = TRANSITION_MAP[is_pipeline][appoint]

    if from_state in transition:
        if to_state in transition[from_state]:
            return True
    return False


def is_rerunning(from_state, to_state):
    return from_state == FINISHED and to_state == RUNNING
