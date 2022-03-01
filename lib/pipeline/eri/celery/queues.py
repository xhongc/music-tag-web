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

from typing import Any, List

from kombu import Exchange, Queue


class QueueResolver:
    def __init__(self, queue: str):
        self.queue = queue

    def resolve_task_queue_and_routing_key(self, task: Any) -> (str, str):
        task_name = task
        if not isinstance(task_name, str):
            task_name = task.name

        queue_config = self.routes_config()
        return queue_config[task_name]["queue"], queue_config[task_name]["routing_key"]

    def routes_config(self) -> dict:
        suffix = "_%s" % self.queue if self.queue else ""
        return {
            "pipeline.eri.celery.tasks.execute": {
                "queue": "er_execute%s" % suffix,
                "routing_key": "er_execute%s" % suffix,
            },
            "pipeline.eri.celery.tasks.schedule": {
                "queue": "er_schedule%s" % suffix,
                "routing_key": "er_schedule%s" % suffix,
            },
            "pipeline.eri.celery.tasks.timeout_check": {
                "queue": "er_timeout%s" % suffix,
                "routing_key": "er_timeout%s" % suffix,
            },
        }

    def queues(self) -> List[Queue]:
        exchange = Exchange("default", type="direct")
        return [
            Queue(queue_config["queue"], exchange, routing_key=queue_config["routing_key"], max_priority=255)
            for queue_config in self.routes_config().values()
        ]


CELERY_QUEUES = QueueResolver("").queues()
