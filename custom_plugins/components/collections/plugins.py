# -*- coding: utf-8 -*-
import math
from pipeline.core.flow.activity import Service, StaticIntervalGenerator
from pipeline.component_framework.component import Component
import json
import eventlet
import time

requests = eventlet.import_patched('requests')


class HttpRequestService(Service):
    __need_schedule__ = False

    def execute(self, data, parent_data):
        try:
            inputs = data.get_one_of_inputs("inputs")
            headers = self.parse_headers(inputs["header"])
            inputs["body"] = json.loads(inputs["body"])
            req_data = [{"params": inputs["body"]}, {"json": inputs["body"]}][inputs["method"] != "get"]
            res = requests.request(inputs["method"], url=inputs["url"], headers=headers, timeout=inputs["timeout"],
                                   **req_data).content
            print("执行了", res)
            try:
                res = json.loads(res)
            except Exception:
                res = res
            data.outputs.outputs = res
            time.sleep(5)
            if res.get("result"):
                return True
            else:
                return False

        except Exception as e:
            data.outputs.outputs = str(e)
            return False

    def parse_headers(self, headers):
        return {header["key"]: header["value"] for header in headers if header["key"]}

    def inputs_format(self):
        return [
            Service.InputItem(name="输入参数", key="inputs", type="dict", required=True)
        ]

    def outputs_format(self):
        return [
            Service.OutputItem(name="输出参数", key="outputs", type="dict", required=True)
        ]


class HttpRequestComponent(Component):
    name = "HttpRequestComponent"
    code = "http_request"
    bound_service = HttpRequestService
