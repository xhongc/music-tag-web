# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def format_validation_message(e):
    """格式化drf校验错误信息"""

    if isinstance(e.detail, list):
        message = "; ".join(["{}:{}".format(k, v) for k, v in enumerate(e.detail)])
    elif isinstance(e.detail, dict):
        messages = []
        for k, v in e.detail.items():
            if isinstance(v, list):
                try:
                    messages.append("{}:{}".format(k, ",".join(v)))
                except TypeError:
                    messages.append("{}:{}".format(k, "部分列表元素的参数不合法，请检查"))
            else:
                messages.append("{}:{}".format(k, v))
        message = ";".join(messages)
    else:
        message = e.detail

    return message
