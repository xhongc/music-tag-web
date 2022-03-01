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

import importlib
import sys
import traceback
from contextlib import contextmanager

from mock import MagicMock, call, patch

from pipeline.core.data.base import DataObject
from pipeline.core.flow.io import SimpleItemSchema, ArrayItemSchema, ObjectItemSchema, ItemSchema
from pipeline.utils.uniqid import uniqid


@contextmanager
def patch_context(patchers):
    for patcher in patchers:
        patcher.start()

    yield

    for patcher in patchers:
        patcher.stop()


class ComponentTestMixin(object):
    def component_cls(self):
        raise NotImplementedError()

    def cases(self):
        raise NotImplementedError()

    def input_output_format_valid(self):
        component = self._component_cls({})
        bound_service = component.service()
        inputs_format = bound_service.inputs()
        self._format_valid(inputs_format, ["name", "key", "type", "schema", "required"])
        outputs_format = bound_service.outputs()
        self._format_valid(outputs_format, ["name", "key", "type", "schema"])

    @property
    def _cases(self):
        return self.cases()

    @property
    def _component_cls(self):
        return self.component_cls()

    @property
    def _component_cls_name(self):
        return self._component_cls.__name__

    @property
    def _failed_cases(self):
        return getattr(self, "__failed_cases", None)

    def _format_valid(self, component_format, format_keys):
        assert isinstance(component_format, list)
        for item in component_format:
            assert set(item.as_dict().keys()) == set(
                format_keys
            ), "item {} is expected to contain attributes {} but {} obtained".format(
                item.key, str(format_keys), str(item.as_dict().keys())
            )
            if item.schema is not None:
                assert item.type == item.schema.type, "type of {} is expected to be {} but {} obtained".format(
                    item.key, item.schema.type, item.type
                )
                self._item_schema_valid(item.schema)

    def _item_schema_valid(self, item_schema):
        common_keys = {"type", "description", "enum"}
        assert common_keys.issubset(
            set(item_schema.as_dict().keys())
        ), "ItemSchema should contain attributes type, description and enum"

        if isinstance(item_schema, SimpleItemSchema):
            return
        if isinstance(item_schema, ArrayItemSchema):
            assert hasattr(item_schema, "item_schema") and isinstance(
                item_schema.item_schema, ItemSchema
            ), "ArrayItemSchema should contain attribute item_schema"
            self._item_schema_valid(item_schema.item_schema)
            return
        if isinstance(item_schema, ObjectItemSchema):
            assert hasattr(item_schema, "property_schemas") and isinstance(
                item_schema.property_schemas, dict
            ), "ObjectItemSchema should contain attribute property_schemas with type dict"
            for child_item_schema in item_schema.property_schemas.values():
                self._item_schema_valid(child_item_schema)
            return
        raise AssertionError("item_schema type error: {}".format(item_schema.description))

    def _format_failure_message(self, no, name, msg):
        return "[{component_cls} case {no}] - [{name}] fail: {msg}".format(
            component_cls=self._component_cls_name, no=no + 1, name=name, msg=msg
        )

    def _do_case_assert(self, service, method, assertion, no, name, args=None, kwargs=None):

        args = args or [service]
        kwargs = kwargs or {}

        data = kwargs.get("data") or args[0]

        result = getattr(service, method)(*args, **kwargs)

        assert_success = result in [None, True]  # return none will consider as success
        do_continue = not assert_success

        assert_method = "assertTrue" if assert_success else "assertFalse"

        getattr(self, assert_method)(
            assertion.success,
            msg=self._format_failure_message(
                no=no,
                name=name,
                msg="{method} success assertion failed, {method} execute success".format(method=method),
            ),
        )

        self.assertDictEqual(
            data.outputs,
            assertion.outputs,
            msg=self._format_failure_message(
                no=no,
                name=name,
                msg="{method} outputs assertion failed,\nexcept: {e}\nactual: {a}".format(
                    method=method, e=assertion.outputs, a=data.outputs
                ),
            ),
        )

        return do_continue

    def _do_call_assertion(self, name, no, assertion):
        try:
            assertion.do_assert()
        except AssertionError as e:
            self.assertTrue(
                False,
                msg=self._format_failure_message(
                    no=no, name=name, msg="{func} call assert failed: {e}".format(func=assertion.func, e=e)
                ),
            )

    def _case_pass(self, case):
        sys.stdout.write(
            "\n[√] <{component}> - [{case_name}]\n".format(
                component=self._component_cls_name,
                case_name=case.name,
            )
        )

    def _case_fail(self, case):
        sys.stdout.write(
            "\n[×] <{component}> - [{case_name}]\n".format(
                component=self._component_cls_name,
                case_name=case.name,
            )
        )

        if not hasattr(self, "__failed_cases"):
            setattr(self, "__failed_cases", [])

        self._failed_cases.append(case)

    def _test_fail(self):
        raise AssertionError("{} cases fail".format([case.name for case in self._failed_cases]))

    def test_component(self):
        self.input_output_format_valid()

        component = self._component_cls({})

        for no, case in enumerate(self._cases):
            try:

                patchers = [patcher.mock_patcher() for patcher in case.patchers]

                with patch_context(patchers):

                    bound_service = component.service()

                    setattr(bound_service, "root_pipeline_id", case.root_pipeline_id)
                    setattr(bound_service, "id", case.service_id)
                    setattr(bound_service, "logger", MagicMock())

                    data = DataObject(inputs=case.inputs)
                    parent_data = DataObject(inputs=case.parent_data)

                    # execute result check
                    do_continue = self._do_case_assert(
                        service=bound_service,
                        method="execute",
                        args=(data, parent_data),
                        assertion=case.execute_assertion,
                        no=no,
                        name=case.name,
                    )

                    for call_assertion in case.execute_call_assertion:
                        self._do_call_assertion(name=case.name, no=no, assertion=call_assertion)

                    if do_continue:
                        self._case_pass(case)
                        continue

                    if bound_service.need_schedule():

                        if bound_service.interval is None:
                            # callback case
                            self._do_case_assert(
                                service=bound_service,
                                method="schedule",
                                args=(data, parent_data, case.schedule_assertion.callback_data),
                                assertion=case.schedule_assertion,
                                no=no,
                                name=case.name,
                            )

                        else:
                            # schedule case
                            assertions = case.schedule_assertion
                            assertions = assertions if isinstance(assertions, list) else [assertions]

                            for assertion in assertions:
                                do_continue = self._do_case_assert(
                                    service=bound_service,
                                    method="schedule",
                                    args=(data, parent_data),
                                    assertion=assertion,
                                    no=no,
                                    name=case.name,
                                )

                                self.assertEqual(
                                    assertion.schedule_finished,
                                    bound_service.is_schedule_finished(),
                                    msg=self._format_failure_message(
                                        no=no,
                                        name=case.name,
                                        msg="schedule_finished assertion failed:"
                                        "\nexpected: {expected}\nactual: {actual}".format(
                                            expected=assertion.schedule_finished,  # noqa
                                            actual=bound_service.is_schedule_finished(),
                                        ),
                                    ),
                                )  # noqa

                                if do_continue:
                                    break

                        for call_assertion in case.schedule_call_assertion:
                            self._do_call_assertion(name=case.name, no=no, assertion=call_assertion)

                    self._case_pass(case)

            except Exception:
                self._case_fail(case)
                sys.stdout.write("{}\n".format(traceback.format_exc()))

        if self._failed_cases:
            self._test_fail()


class ComponentTestCase(object):
    def __init__(
        self,
        inputs,
        parent_data,
        execute_assertion,
        schedule_assertion,
        name="",
        patchers=None,
        execute_call_assertion=None,
        schedule_call_assertion=None,
        service_id=None,
        root_pipeline_id=None,
    ):
        self.inputs = inputs
        self.parent_data = parent_data
        self.execute_assertion = execute_assertion
        self.execute_call_assertion = execute_call_assertion or []
        self.schedule_call_assertion = schedule_call_assertion or []
        self.schedule_assertion = schedule_assertion
        self.name = name
        self.patchers = patchers or []
        self.service_id = service_id or uniqid()
        self.root_pipeline_id = root_pipeline_id or uniqid()


class CallAssertion(object):
    def __init__(self, func, calls, any_order=False):
        self.func = func
        self.calls = calls
        self.any_order = any_order

    def do_assert(self):
        if not callable(self.func):
            module_and_func = self.func.rsplit(".", 1)
            mod_path = module_and_func[0]
            func_name = module_and_func[1]
            mod = importlib.import_module(mod_path)
            func = getattr(mod, func_name)
        else:
            func = self.func

        if not self.calls:
            func.assert_not_called()
        else:
            assert func.call_count == len(
                self.calls
            ), "Expected 'mock' have been called {expect} times. " "Called {actual} times".format(
                expect=len(self.calls), actual=func.call_count
            )
            func.assert_has_calls(calls=self.calls, any_order=self.any_order)

        func.reset_mock()


class Assertion(object):
    def __init__(self, success, outputs):
        self.success = success
        self.outputs = outputs


class ExecuteAssertion(Assertion):
    pass


class ScheduleAssertion(Assertion):
    def __init__(self, callback_data=None, schedule_finished=False, *args, **kwargs):
        self.callback_data = callback_data
        self.schedule_finished = schedule_finished
        super(ScheduleAssertion, self).__init__(*args, **kwargs)


class Patcher(object):
    def __init__(self, target, return_value=None, side_effect=None):
        self.target = target
        self.return_value = return_value
        self.side_effect = side_effect

    def mock_patcher(self):
        return patch(target=self.target, new=MagicMock(return_value=self.return_value, side_effect=self.side_effect))


Call = call
