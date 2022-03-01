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

from abc import ABCMeta, abstractmethod
from copy import deepcopy

from django.utils.translation import ugettext_lazy as _

from pipeline.conf import settings
from pipeline.core.flow.activity.base import Activity
from pipeline.core.flow.io import BooleanItemSchema, InputItem, IntItemSchema, OutputItem
from pipeline.utils.utils import convert_bytes_to_str


class Service(object, metaclass=ABCMeta):
    schedule_result_attr = "__schedule_finish__"
    schedule_determine_attr = "__need_schedule__"
    multi_callback_determine_attr = "__multi_callback_enabled__"
    InputItem = InputItem
    OutputItem = OutputItem
    interval = None
    default_outputs = [
        OutputItem(
            name=_("执行结果"),
            key="_result",
            type="boolean",
            schema=BooleanItemSchema(description=_("执行结果的布尔值，True or False")),
        ),
        OutputItem(name=_("循环次数"), key="_loop", type="int", schema=IntItemSchema(description=_("循环执行次数"))),
        OutputItem(
            name=_("当前流程循环次数"),
            key="_inner_loop",
            type="int",
            schema=IntItemSchema(description=_("在当前流程节点循环执行次数，由父流程重新进入时会重置（仅支持新版引擎）")),
        ),
    ]

    def __init__(self, name=None):
        self.name = name
        self.interval = deepcopy(self.interval)
        self._runtime_attrs = {}

    def __getattr__(self, name):
        if name not in self.__dict__.get("_runtime_attrs", {}):
            raise AttributeError()

        return self._runtime_attrs[name]

    def __getstate__(self):
        if "logger" in self.__dict__:
            del self.__dict__["logger"]
        # compatible with old version pickle obj
        if "_runtime_attrs" in self.__dict__:
            if "logger" in self._runtime_attrs:
                del self._runtime_attrs["logger"]

        return self.__dict__

    @abstractmethod
    def execute(self, data, parent_data):
        # get params from data
        pass

    def outputs_format(self):
        return []

    def inputs_format(self):
        return []

    def inputs(self):
        return self.inputs_format()

    def outputs(self):
        custom_format = self.outputs_format()
        assert isinstance(custom_format, list)
        custom_format += self.default_outputs
        return custom_format

    def need_schedule(self):
        return getattr(self, Service.schedule_determine_attr, False)

    def schedule(self, data, parent_data, callback_data=None):
        return True

    def finish_schedule(self):
        setattr(self, self.schedule_result_attr, True)

    def is_schedule_finished(self):
        return getattr(self, self.schedule_result_attr, False)

    def multi_callback_enabled(self):
        return getattr(self, self.multi_callback_determine_attr, False)

    def clean_status(self):
        setattr(self, self.schedule_result_attr, False)

    def setup_runtime_attrs(self, **kwargs):
        # compatible with old version pickle obj
        if "_runtime_attrs" not in self.__dict__:
            self._runtime_attrs = {}
        self._runtime_attrs.update(**kwargs)


class ServiceActivity(Activity):
    result_bit = "_result"
    loop = "_loop"
    ON_RETRY = "_on_retry"

    def __init__(
        self,
        id,
        service,
        name=None,
        data=None,
        error_ignorable=False,
        failure_handler=None,
        skippable=True,
        retryable=True,
        timeout=None,
    ):
        super(ServiceActivity, self).__init__(id, name, data, failure_handler)
        self.service = service
        self.error_ignorable = error_ignorable
        self.skippable = skippable
        self.retryable = retryable
        self.timeout = timeout

        if data:
            self._prepared_inputs = self.data.inputs_copy()
            self._prepared_outputs = self.data.outputs_copy()

    def __setstate__(self, state):

        for attr, obj in list(state.items()):
            # py2 pickle dumps data compatible
            if isinstance(attr, bytes):
                attr = attr.decode("utf-8")
                obj = convert_bytes_to_str(obj)

            setattr(self, attr, obj)

        if "timeout" not in state:
            self.timeout = None

    def execute_pre_process(self, parent_data):
        # return True if the plugin does not complete execute_pre_process function
        if not (hasattr(self.service, "execute_pre_process") and callable(self.service.execute_pre_process)):
            return True

        result = self.service.execute_pre_process(self.data, parent_data)

        # set result
        self.set_result_bit(result)

        if self.error_ignorable:
            return True
        return result

    def execute(self, parent_data):
        self.setup_logger()
        try:
            result = self.service.execute(self.data, parent_data)
        except settings.PLUGIN_SPECIFIC_EXCEPTIONS as e:
            self.data.set_outputs("ex_data", e)
            result = False

        # set result
        self.set_result_bit(result)

        if self.error_ignorable:
            return True
        return result

    def set_result_bit(self, result):
        if result is False:
            self.data.set_outputs(self.result_bit, False)
        else:
            self.data.set_outputs(self.result_bit, True)

    def get_result_bit(self):
        return self.data.get_one_of_outputs(self.result_bit, False)

    def skip(self):
        self.set_result_bit(True)
        return True

    def ignore_error(self):
        self.set_result_bit(False)
        return True

    def clear_outputs(self):
        self.data.reset_outputs({})

    def need_schedule(self):
        return self.service.need_schedule()

    def schedule(self, parent_data, callback_data=None):
        self.setup_logger()
        try:
            result = self.service.schedule(self.data, parent_data, callback_data)
        except settings.PLUGIN_SPECIFIC_EXCEPTIONS as e:
            self.data.set_outputs("ex_data", e)
            result = False
        self.set_result_bit(result)

        if result is False:
            if self.error_ignorable:
                self.service.finish_schedule()
                return True

        return result

    def is_schedule_done(self):
        return self.service.is_schedule_finished()

    def finish_schedule(self):
        self.service.finish_schedule()

    def shell(self):
        shell = ServiceActivity(
            id=self.id,
            service=self.service,
            name=self.name,
            data=self.data,
            error_ignorable=self.error_ignorable,
            timeout=self.timeout,
        )
        return shell

    def schedule_fail(self):
        return

    def schedule_success(self):
        return

    def prepare_rerun_data(self):
        self.data.override_inputs(deepcopy(self._prepared_inputs))
        self.data.override_outputs(deepcopy(self._prepared_outputs))

    def setup_runtime_attrs(self, **kwargs):
        self.service.setup_runtime_attrs(**kwargs)

    def setup_logger(self):
        self.service.setup_runtime_attrs(logger=self.logger)


class AbstractIntervalGenerator(object, metaclass=ABCMeta):
    def __init__(self):
        self.count = 0

    def next(self):
        self.count += 1


class DefaultIntervalGenerator(AbstractIntervalGenerator):
    def next(self):
        super(DefaultIntervalGenerator, self).next()
        return self.count ** 2


class SquareIntervalGenerator(AbstractIntervalGenerator):
    def next(self):
        super(SquareIntervalGenerator, self).next()
        return self.count ** 2


class NullIntervalGenerator(AbstractIntervalGenerator):
    pass


class LinearIntervalGenerator(AbstractIntervalGenerator):
    pass


class StaticIntervalGenerator(AbstractIntervalGenerator):
    def __init__(self, interval):
        super(StaticIntervalGenerator, self).__init__()
        self.interval = interval

    def next(self):
        super(StaticIntervalGenerator, self).next()
        return self.interval
