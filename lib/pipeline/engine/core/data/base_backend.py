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

from abc import abstractmethod, ABCMeta


class BaseDataBackend(object, metaclass=ABCMeta):
    @abstractmethod
    def set_object(self, key, obj):
        raise NotImplementedError()

    @abstractmethod
    def get_object(self, key):
        raise NotImplementedError()

    @abstractmethod
    def del_object(self, key):
        raise NotImplementedError()

    @abstractmethod
    def expire_cache(self, key, value, expires):
        raise NotImplementedError()

    @abstractmethod
    def cache_for(self, key):
        raise NotImplementedError()
