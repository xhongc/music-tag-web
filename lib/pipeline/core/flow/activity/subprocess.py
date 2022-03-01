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

from copy import deepcopy

from pipeline.core.flow.activity.base import Activity
from pipeline.utils.utils import convert_bytes_to_str


class SubProcess(Activity):
    def __init__(self, id, pipeline, name=None):
        super(SubProcess, self).__init__(id, name, pipeline.data)
        self.pipeline = pipeline
        self._prepared_inputs = self.pipeline.data.inputs_copy()
        self._prepared_outputs = self.pipeline.data.outputs_copy()

    def prepare_rerun_data(self):
        self.data.override_inputs(deepcopy(self._prepared_inputs))
        self.data.override_outputs(deepcopy(self._prepared_outputs))

    def __setstate__(self, state):
        for attr, obj in list(state.items()):
            if isinstance(attr, bytes):
                attr = attr.decode("utf-8")
                obj = convert_bytes_to_str(obj)
            setattr(self, attr, obj)

        if "_prepared_inputs" not in state:
            self._prepared_inputs = self.pipeline.data.inputs_copy()

        if "_prepared_outputs" not in state:
            self._prepared_outputs = self.pipeline.data.outputs_copy()
