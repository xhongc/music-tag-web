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

import json
import pickle
import codecs
from typing import Any


class SerializerMixin:
    JSON_SERIALIZER = "json"
    PICKLE_SERIALIZER = "pickle"

    def _deserialize(self, data: str, serializer: str) -> Any:
        if serializer == self.JSON_SERIALIZER:
            return json.loads(data)
        elif serializer == self.PICKLE_SERIALIZER:
            return pickle.loads(codecs.decode(data.encode(), "base64"))
        else:
            raise ValueError("unsupport serializer type: {}".format(serializer))

    def _serialize(self, data: Any) -> (str, str):
        try:
            return json.dumps(data), self.JSON_SERIALIZER
        except TypeError:
            return codecs.encode(pickle.dumps(data), "base64").decode(), self.PICKLE_SERIALIZER
