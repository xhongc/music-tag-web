# -*- coding: utf-8 -*-
import math
from pipeline.core.flow.activity import Service, StaticIntervalGenerator
from pipeline.component_framework.component import Component
import json
import eventlet

requests = eventlet.import_patched('requests')


class HttpRequestService(Service):
    __need_schedule__ = False

    def execute(self, data, parent_data):
        print("执行了")
        return True


class HttpRequestComponent(Component):
    name = "HttpRequestComponent"
    code = "http_request"
    bound_service = HttpRequestService
