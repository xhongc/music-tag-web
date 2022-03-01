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

import sys
import logging
import traceback

import redis
from django.apps import AppConfig
from django.conf import settings
from redis.sentinel import Sentinel
from rediscluster import RedisCluster

logger = logging.getLogger("root")


def get_client_through_sentinel():
    kwargs = {"sentinel_kwargs": {}}
    sentinel_pwd = settings.REDIS.get("sentinel_password")
    if sentinel_pwd:
        kwargs["sentinel_kwargs"]["password"] = sentinel_pwd
    if "password" in settings.REDIS:
        kwargs["password"] = settings.REDIS["password"]
    host = settings.REDIS["host"]
    port = settings.REDIS["port"]
    sentinels = list(zip([h.strip() for h in host.split(",")], [p.strip() for p in str(port).split(",")],))
    rs = Sentinel(sentinels, **kwargs)
    # avoid None value in settings.REDIS
    r = rs.master_for(settings.REDIS.get("service_name") or "mymaster")
    # try to connect master
    r.echo("Hello Redis")
    return r


def get_cluster_client():
    kwargs = {"startup_nodes": [{"host": settings.REDIS["host"], "port": settings.REDIS["port"]}]}
    if "password" in settings.REDIS:
        kwargs["password"] = settings.REDIS["password"]

    r = RedisCluster(**kwargs)
    r.echo("Hello Redis")
    return r


def get_single_client():
    kwargs = {
        "host": settings.REDIS["host"],
        "port": settings.REDIS["port"],
    }
    if "password" in settings.REDIS:
        kwargs["password"] = settings.REDIS["password"]
    if "db" in settings.REDIS:
        kwargs["db"] = settings.REDIS["db"]

    pool = redis.ConnectionPool(**kwargs)
    return redis.StrictRedis(connection_pool=pool)


CLIENT_GETTER = {
    "replication": get_client_through_sentinel,
    "cluster": get_cluster_client,
    "single": get_single_client,
}


class PipelineConfig(AppConfig):
    name = "pipeline"
    verbose_name = "Pipeline"

    def ready(self):
        from pipeline.signals.handlers import pipeline_template_post_save_handler  # noqa
        from pipeline.validators.handlers import post_new_end_event_register_handler  # noqa

        # init redis pool
        if hasattr(settings, "REDIS"):
            mode = settings.REDIS.get("mode") or "single"
            try:
                settings.REDIS_INST = CLIENT_GETTER[mode]()
                settings.redis_inst = CLIENT_GETTER[mode]()
            except Exception:
                # fall back to single node mode
                logger.error("redis client init error: %s" % traceback.format_exc())
        elif (
            getattr(settings, "PIPELINE_DATA_BACKEND", None)
            == "pipeline.engine.core.data.redis_backend.RedisDataBackend"
        ):
            logger.error("can not find REDIS in settings!")

        # avoid big flow pickle raise maximum recursion depth exceeded error
        sys.setrecursionlimit(10000)
