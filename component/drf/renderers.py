# -*- coding: utf-8 -*-
"""
自定义drf renderers 使返回格式和ESB接口返回格式相同
使用方法:
django settings 中添加 rest_framework配置
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ("component.drf.renderers.CustomRenderer",),
}

"""
from rest_framework import status
from rest_framework.renderers import JSONRenderer


class CustomRenderer(JSONRenderer):
    @staticmethod
    def _format_validation_message(detail):
        """格式化drf校验错误信息"""

        if isinstance(detail, list):
            message = "; ".join(["{}:{}".format(k, v) for k, v in enumerate(detail)])
        elif isinstance(detail, dict):
            messages = []
            for k, v in detail.items():
                if isinstance(v, list):
                    try:
                        messages.append("{}:{}".format(k, ",".join(v)))
                    except TypeError:
                        messages.append("{}:{}".format(k, "部分列表元素的参数不合法，请检查"))
                else:
                    messages.append("{}:{}".format(k, v))
            message = ";".join(messages)
        else:
            message = detail

        return message

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """重构render方法"""

        request = renderer_context.get("request")
        response = renderer_context.get("response")

        # 更改删除成功的状态码, 204 --> 200
        if response.status_code == status.HTTP_204_NO_CONTENT and request.method == "DELETE":
            response.status_code = status.HTTP_200_OK

        # 重新构建返回的JSON字典
        if response and status.is_success(response.status_code):
            ret = {
                "result": True,
                "code": str(response.status_code * 100),
                "message": "success",
                "data": data,
            }
        else:
            ret = {
                "result": False,
                "code": str((response.status_code if response else 500) * 100),
                "message": self._format_validation_message(detail=data.get("detail", "") or data),
                "data": data,
            }
        # 返回JSON数据
        return super(CustomRenderer, self).render(ret, accepted_media_type, renderer_context)
