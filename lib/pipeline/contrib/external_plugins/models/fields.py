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

import ujson as json
from django.db import models


class JSONTextField(models.TextField):
    def __init__(self, *args, **kwargs):
        super(JSONTextField, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        return json.dumps(value)

    def to_python(self, value):
        value = super(JSONTextField, self).to_python(value)
        return json.loads(value)

    def from_db_value(self, value, expression, connection, context=None):
        return self.to_python(value)
