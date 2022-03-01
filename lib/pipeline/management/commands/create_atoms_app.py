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

import os
import sys

from django.core.management import base, call_command
from django.template import Template, Context

from pipeline.templates.create_plugins_app import js_file, plugins, py_file

PY_COPYRIGHT = '''# -*- coding: utf-8 -*-
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
'''


class Command(base.BaseCommand):
    help = "Create an application for atoms development"

    def add_arguments(self, parser):
        parser.add_argument("app_name", nargs=1, type=str)

    def handle(self, *args, **options):

        app_name = options["app_name"][0]
        if os.path.isdir(app_name):
            sys.stdout.write("the directory [%s] already exists, please try another name.\n")
            return

        call_command("startapp", app_name)

        collection_path = "%s/components/collections" % app_name
        tests_path = "%s/tests/components/collections/plugins_test" % app_name
        static_collection_path = "{}/static/{}".format(app_name, app_name)
        init_file_info = {
            "%s/components/collections/__init__.py" % app_name: py_file.TEMPLATE,
            "%s/components/__init__.py" % app_name: py_file.TEMPLATE,
            "%s/components/collections/plugins.py" % app_name: plugins.TEMPLATE,
            "%s/tests/__init__.py" % app_name: py_file.TEMPLATE,
            "%s/tests/components/__init__.py" % app_name: py_file.TEMPLATE,
            "%s/tests/components/collections/__init__.py" % app_name: py_file.TEMPLATE,
            "%s/tests/components/collections/plugins_test/__init__.py" % app_name: py_file.TEMPLATE,
            "{}/static/{}/plugins.js".format(app_name, app_name): js_file.TEMPLATE,
        }
        exist_file_path = [
            "%s/migrations/__init__.py" % app_name,
            "%s/__init__.py" % app_name,
            "%s/apps.py" % app_name,
        ]
        useless_file_path = [
            "%s/admin.py" % app_name,
            "%s/models.py" % app_name,
            "%s/tests.py" % app_name,
            "%s/views.py" % app_name,
        ]
        os.makedirs(collection_path)
        os.makedirs(tests_path)
        os.makedirs(static_collection_path)

        empty_context = Context()
        for p, tmpl in list(init_file_info.items()):
            with open(p, "w+") as f:
                f.write(Template(tmpl).render(empty_context))

        for p in exist_file_path:
            with open(p, "r") as f:
                content = f.readlines()

            if content and content[0].startswith("# -*- coding: utf-8 -*-"):
                content = content[1:]

            content.insert(0, PY_COPYRIGHT)

            with open(p, "w") as f:
                f.writelines(content)

        for p in useless_file_path:
            os.remove(p)
