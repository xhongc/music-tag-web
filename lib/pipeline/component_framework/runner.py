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

import logging
import time

from pipeline.core.data.base import DataObject
from pipeline.utils.uniqid import uniqid


def get_console_logger():
    # create logger
    logger = logging.getLogger("simple_example")
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    return logger


logger = get_console_logger()


class ComponentRunner:
    def __init__(self, component_cls):
        self.component_cls = component_cls

    def run(self, data, parent_data, callback_data=None):

        service = self.component_cls.bound_service()

        setattr(service, "id", uniqid())
        setattr(service, "logger", logger)

        data_object = DataObject(inputs=data)
        parent_data_object = DataObject(inputs=parent_data)

        logger.info(
            "Start to run component [{}] with data: {}, parent_data: {}".format(
                self.component_cls.code, data_object, parent_data_object
            )
        )

        result = service.execute(data_object, parent_data_object)

        if result is False:
            logger.info("Execute return [{}], stop running.".format(result))
            return

        if not service.need_schedule():
            logger.info("Execute return [{}], and component do not need schedule, finish running".format(result))
            return

        if service.interval is None:
            logger.info("Start to callback component with callbackdata: {}".format(callback_data))
            result = service.schedule(data_object, parent_data_object, callback_data)

            if result is False:
                logger.info("Schedule return [{}], stop running.".format(result))
                return
            else:
                logger.info("Schedule return [{}], finish running".format(result))
        else:

            schedue_times = 0

            while not service.is_schedule_finished():

                schedue_times += 1

                logger.info(
                    "Schedule {} with data: {}, parent_data: {}".format(schedue_times, data_object, parent_data_object)
                )

                result = service.schedule(data_object, parent_data_object, None)

                if result is False:
                    logger.info("Schedule return [{}], stop running.".format(result))
                    return

                interval = service.interval.next()
                logger.info("Schedule return [{}], wait for next schedule in {}s".format(result, interval))
                time.sleep(interval)

            logger.info("Schedule finished")
