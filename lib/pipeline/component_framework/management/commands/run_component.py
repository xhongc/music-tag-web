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

import ujson as json
from django.core.management import BaseCommand

from pipeline.component_framework.library import ComponentLibrary
from pipeline.component_framework.runner import ComponentRunner
from pipeline.exceptions import ComponentNotExistException


class Command(BaseCommand):

    help = "Run the specified component"

    def add_arguments(self, parser):
        parser.add_argument("code", nargs=1, type=str)
        parser.add_argument("-d", dest="data", nargs="?", type=str)
        parser.add_argument("-p", dest="parent_data", nargs="?", type=str)
        parser.add_argument("-c", dest="callbackdata", nargs="?", type=str)

    def handle(self, *args, **options):
        code = options["code"][0]
        data = options["data"]
        parent_data = options["parent_data"]
        callbackdata = options["callbackdata"]

        try:
            data = json.loads(data) if data else {}
        except Exception:
            sys.stdout.write("data is not a valid json.\n")
            exit(1)

        try:
            parent_data = json.loads(parent_data) if parent_data else {}
        except Exception:
            sys.stdout.write("parent_data is not a valid json.\n")
            exit(1)

        try:
            callbackdata = json.loads(callbackdata) if callbackdata else {}
        except Exception:
            sys.stdout.write("callbackdata is not a valid json.\n")
            exit(1)

        try:
            component_cls = ComponentLibrary.get_component_class(code)
        except ComponentNotExistException:
            sys.stdout.write("component [{}] does not exist.\n".format(code))
            exit(1)

        runner = ComponentRunner(component_cls)
        runner.run(data, parent_data, callbackdata)
