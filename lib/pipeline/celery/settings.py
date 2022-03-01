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

import copy

from kombu import Exchange, Queue

from pipeline.celery.queues import ScalableQueues
from pipeline.constants import PIPELINE_MAX_PRIORITY

default_exchange = Exchange("default", type="direct")

# 设置时区
CELERY_TIMEZONE = "Asia/Shanghai"
# 启动时区设置
CELERY_ENABLE_UTC = False

# new priority queues
PUSH_DEFAULT_QUEUE_NAME = "pipeline_priority"
PUSH_DEFAULT_ROUTING_KEY = "pipeline_push_priority"

SCHEDULE_DEFAULT_QUEUE_NAME = "service_schedule_priority"
SCHEDULE_DEFAULT_ROUTING_KEY = "schedule_service_priority"

ADDITIONAL_DEFAULT_QUEUE_NAME = "pipeline_additional_task_priority"
ADDITIONAL_DEFAULT_ROUTING_KEY = "additional_task_priority"

STATISTICS_PRIORITY_QUEUE_NAME = "pipeline_statistics_priority"
STATISTICS_PRIORITY_ROUTING_KEY = "pipeline_statistics_priority"

SCALABLE_QUEUES_CONFIG = {
    PUSH_DEFAULT_QUEUE_NAME: {"name": PUSH_DEFAULT_QUEUE_NAME, "routing_key": PUSH_DEFAULT_ROUTING_KEY},
    SCHEDULE_DEFAULT_QUEUE_NAME: {"name": SCHEDULE_DEFAULT_QUEUE_NAME, "routing_key": SCHEDULE_DEFAULT_ROUTING_KEY},
}

PIPELINE_PRIORITY_ROUTING = {
    "queue": PUSH_DEFAULT_QUEUE_NAME,
    "routing_key": PUSH_DEFAULT_ROUTING_KEY,
}

PIPELINE_SCHEDULE_PRIORITY_ROUTING = {
    "queue": SCHEDULE_DEFAULT_QUEUE_NAME,
    "routing_key": SCHEDULE_DEFAULT_ROUTING_KEY,
}

PIPELINE_ADDITIONAL_PRIORITY_ROUTING = {
    "queue": ADDITIONAL_DEFAULT_QUEUE_NAME,
    "routing_key": ADDITIONAL_DEFAULT_ROUTING_KEY,
}

PIPELINE_STATISTICS_PRIORITY_ROUTING = {
    "queue": STATISTICS_PRIORITY_QUEUE_NAME,
    "routing_key": STATISTICS_PRIORITY_ROUTING_KEY,
}

CELERY_ROUTES = {
    # schedule
    "pipeline.engine.tasks.service_schedule": PIPELINE_SCHEDULE_PRIORITY_ROUTING,
    # pipeline
    "pipeline.engine.tasks.batch_wake_up": PIPELINE_PRIORITY_ROUTING,
    "pipeline.engine.tasks.dispatch": PIPELINE_PRIORITY_ROUTING,
    "pipeline.engine.tasks.process_wake_up": PIPELINE_PRIORITY_ROUTING,
    "pipeline.engine.tasks.start": PIPELINE_PRIORITY_ROUTING,
    "pipeline.engine.tasks.wake_from_schedule": PIPELINE_PRIORITY_ROUTING,
    "pipeline.engine.tasks.wake_up": PIPELINE_PRIORITY_ROUTING,
    "pipeline.engine.tasks.process_unfreeze": PIPELINE_PRIORITY_ROUTING,
    # another
    "pipeline.log.tasks.clean_expired_log": PIPELINE_ADDITIONAL_PRIORITY_ROUTING,
    "pipeline.engine.tasks.node_timeout_check": PIPELINE_ADDITIONAL_PRIORITY_ROUTING,
    "pipeline.contrib.periodic_task.tasks.periodic_task_start": PIPELINE_ADDITIONAL_PRIORITY_ROUTING,
    "pipeline.contrib.periodic_task.tasks.bamboo_engine_periodic_task_start": PIPELINE_ADDITIONAL_PRIORITY_ROUTING,
    "pipeline.engine.tasks.heal_zombie_process": PIPELINE_ADDITIONAL_PRIORITY_ROUTING,
    "pipeline.engine.tasks.expired_tasks_clean": PIPELINE_ADDITIONAL_PRIORITY_ROUTING,
    # statistics
    "pipeline.contrib.statistics.tasks.pipeline_post_save_statistics_task": PIPELINE_STATISTICS_PRIORITY_ROUTING,
    "pipeline.contrib.statistics.tasks.pipeline_archive_statistics_task": PIPELINE_STATISTICS_PRIORITY_ROUTING,
}


class QueueResolver(object):
    def __init__(self, queue):
        self.queue = queue

    def default_setting_for(self, task, setting_key):
        if not isinstance(task, str):
            task = task.name

        return CELERY_ROUTES[task][setting_key]

    def resolve_task_routing_key(self, task):
        default_key = self.default_setting_for(task, "routing_key")
        default_queue = self.default_setting_for(task, "queue")

        if default_queue not in SCALABLE_QUEUES_CONFIG or not self.queue:
            return default_key

        return self.resolve_routing_key(default_key)

    def resolve_task_queue_name(self, task):
        default_queue = self.default_setting_for(task, "queue")

        return self.resolve_queue_name(default_queue)

    def resolve_queue_name(self, default_name):
        if not self.queue:
            return default_name

        return "{}_{}".format(self.queue, default_name)

    def resolve_routing_key(self, default_key):
        if not self.queue:
            return default_key

        return "{}_{}".format(ScalableQueues.routing_key_for(self.queue), default_key)


USER_QUEUES = []

for name, queue in ScalableQueues.queues().items():
    queue_arguments = copy.copy(queue["queue_arguments"])
    queue_arguments["x-max-priority"] = PIPELINE_MAX_PRIORITY

    for config in SCALABLE_QUEUES_CONFIG.values():
        resolver = QueueResolver(name)
        USER_QUEUES.append(
            Queue(
                resolver.resolve_queue_name(config["name"]),
                default_exchange,
                routing_key=resolver.resolve_routing_key(config["routing_key"]),
                queue_arguments=queue_arguments,
            )
        )

CELERY_QUEUES = [
    # user queues
    *USER_QUEUES,  # noqa
    # keep old queue to process message left in broker, remove on next version
    Queue("default", default_exchange, routing_key="default"),
    Queue("pipeline", default_exchange, routing_key="pipeline_push"),
    Queue("service_schedule", default_exchange, routing_key="schedule_service"),
    Queue("pipeline_additional_task", default_exchange, routing_key="additional_task"),
    # priority queues
    Queue(
        PUSH_DEFAULT_QUEUE_NAME,
        default_exchange,
        routing_key=PUSH_DEFAULT_ROUTING_KEY,
        queue_arguments={"x-max-priority": PIPELINE_MAX_PRIORITY},
    ),
    Queue(
        SCHEDULE_DEFAULT_QUEUE_NAME,
        default_exchange,
        routing_key=SCHEDULE_DEFAULT_ROUTING_KEY,
        queue_arguments={"x-max-priority": PIPELINE_MAX_PRIORITY},
    ),
    Queue(
        ADDITIONAL_DEFAULT_QUEUE_NAME,
        default_exchange,
        routing_key=ADDITIONAL_DEFAULT_ROUTING_KEY,
        queue_arguments={"x-max-priority": PIPELINE_MAX_PRIORITY},
    ),
    Queue(
        STATISTICS_PRIORITY_QUEUE_NAME,
        default_exchange,
        routing_key=STATISTICS_PRIORITY_ROUTING_KEY,
        queue_arguments={"x-max-priority": PIPELINE_MAX_PRIORITY},
    ),
]

CELERY_DEFAULT_QUEUE = "default"
CELERY_DEFAULT_EXCHANGE = "default"
CELERY_DEFAULT_ROUTING_KEY = "default"

CELERYBEAT_SCHEDULER = "django_celery_beat.schedulers.DatabaseScheduler"

CELERY_ACCEPT_CONTENT = ["json", "pickle", "msgpack", "yaml"]
