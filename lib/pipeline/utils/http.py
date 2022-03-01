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

import requests
import ujson as module_json

logger = logging.getLogger("root")


def http_post_request(url, data=None, json=None, **kwargs):
    response = requests.post(url, data=data, json=json, **kwargs)
    if response.status_code == 200:
        try:
            content_dict = module_json.loads(response.content)
            return content_dict
        except Exception as e:
            message = "the format of HTTP request result is valid: %s" % e
            logger.exception(message)
            return {"result": False, "code": 1, "message": message}
    message = "HTTP request failed，Http status code is：%s" % response.status_code
    logger.error(message)
    return {"result": False, "code": response.status_code, "message": message}


def http_get_request(url, params=None, **kwargs):
    response = requests.get(url, params=params, **kwargs)
    if response.status_code == 200:
        try:
            content_dict = module_json.loads(response.content)
            return content_dict
        except Exception as e:
            message = "the format of HTTP request result is valid: %s" % e
            logger.exception(message)
            return {"result": False, "code": 1, "message": message}
    message = "HTTP request failed，Http status code is：%s" % response.status_code
    logger.error(message)
    return {"result": False, "code": response.status_code, "message": message}
