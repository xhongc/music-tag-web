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

import pickle
import logging

from pipeline.conf import settings
from pipeline.engine.core.data.base_backend import BaseDataBackend

logger = logging.getLogger("celery")


class RedisDataBackend(BaseDataBackend):
    def set_object(self, key, obj):
        return settings.REDIS_INST.set(key, pickle.dumps(obj))

    def get_object(self, key):
        pickle_str = settings.REDIS_INST.get(key)
        if not pickle_str:
            logger.warning(
                "[RedisDataBackend.get_object]redis(%s) get %s return %s" % (str(settings.REDIS_INST), key, pickle_str)
            )
            return None
        return pickle.loads(pickle_str)

    def del_object(self, key):
        return settings.REDIS_INST.delete(key)

    def expire_cache(self, key, value, expires):
        settings.REDIS_INST.set(key, pickle.dumps(value))
        settings.REDIS_INST.expire(key, expires)
        return True

    def cache_for(self, key):
        cache = settings.REDIS_INST.get(key)
        return pickle.loads(cache) if cache else cache
