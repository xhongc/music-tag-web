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

from django.test import TestCase

from django_celery_beat.models import PeriodicTask
from pipeline.contrib.periodic_task.models import PeriodicTask as PipelinePeriodicTask
from pipeline.exceptions import InvalidOperationException


class PeriodicTestCase(TestCase):
    def setUp(self):
        self.name = "test"
        self.creator = "tester"
        self.extra_info = {"extra_info": "val"}
        self.data = {
            "constants": {
                "key_1": {"value": "val_1", "show_type": "show"},
                "key_2": {"value": "val_2", "show_type": "hide"},
            }
        }
        self.task = self.create_a_task()

    def tearDown(self):
        if self.task:
            self.task = self.task.delete()

    def create_a_task(self):
        return PipelinePeriodicTask.objects.create_task(
            name=self.name, template=None, cron={}, data=self.data, creator=self.creator, extra_info=self.extra_info,
        )

    def test_create_task(self):
        self.assertIsInstance(self.task, PipelinePeriodicTask)
        self.assertIsInstance(self.task.celery_task, PeriodicTask)
        self.assertEqual(self.task.name, self.name)
        self.assertEqual(self.task.template, None)
        self.assertEqual(self.task.creator, self.creator)
        self.assertEqual(self.task.extra_info, self.extra_info)
        self.assertEqual(self.task.cron, self.task.celery_task.crontab.__str__())
        self.assertEqual(self.task.snapshot.data, self.data)
        self.assertEqual(self.task.total_run_count, 0)
        self.assertEqual(self.task.last_run_at, None)

    def test_enabled(self):
        self.assertEqual(self.task.enabled, self.task.celery_task.enabled)

    def test_set_enabled(self):
        self.task.set_enabled(True)
        self.assertTrue(self.task.enabled)
        self.assertTrue(self.task.celery_task.enabled)
        self.task.set_enabled(False)
        self.assertFalse(self.task.enabled)
        self.assertFalse(self.task.celery_task.enabled)

    def test_execution_data(self):
        self.assertEqual(self.task.execution_data, self.data)

    def test_delete(self):
        celery_task_id = self.task.celery_task.id
        self.task.delete()
        self.assertRaises(PeriodicTask.DoesNotExist, PeriodicTask.objects.get, id=celery_task_id)
        self.task = None

    def test_modify_cron(self):
        self.task.set_enabled(True)
        self.assertRaises(InvalidOperationException, self.task.modify_cron, {})
        self.task.set_enabled(False)
        self.task.modify_cron({"minite": "*/1"})
        self.assertEqual(self.task.cron, self.task.celery_task.crontab.__str__())

    def test_modify_constants(self):
        expect_constants = copy.deepcopy(self.task.execution_data["constants"])
        expect_constants["key_1"]["value"] = "val_3"
        new_constants = self.task.modify_constants({"key_1": "val_3"})
        self.assertEqual(self.task.execution_data["constants"], expect_constants)
        self.assertEqual(new_constants, expect_constants)

        self.task.set_enabled(True)
        self.assertRaises(InvalidOperationException, self.task.modify_constants, {})

    def test_form(self):
        expect_form = {k: v for k, v in list(self.data["constants"].items()) if v["show_type"] == "show"}
        self.assertEqual(self.task.form, expect_form)
