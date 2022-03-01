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
from django import forms

from pipeline.contrib.external_plugins.models.fields import JSONTextField


class JsonFieldModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(JsonFieldModelForm, self).__init__(*args, **kwargs)
        # for edit in django admin web
        all_fields = self.instance.__class__._meta.get_fields()
        for field in all_fields:
            if isinstance(field, JSONTextField):
                self.initial[field.name] = json.dumps(getattr(self.instance, field.name))
