# -*- coding: utf-8 -*-

from rest_framework import status
from rest_framework.response import Response

from component.drf.constants import ResponseCodeStatus


class ApiGenericMixin(object):
    """API视图类通用函数"""

    # TODO 权限部分加载基类中
    permission_classes = ()

    def finalize_response(self, request, response, *args, **kwargs):
        """统一数据返回格式"""
        # 文件导出时response {HttpResponse}
        if not isinstance(response, Response):
            return response
        if response.data is None:
            response.data = {"result": True, "code": ResponseCodeStatus.OK, "message": "success", "data": []}
        elif isinstance(response.data, (list, tuple)):
            response.data = {
                "result": True,
                "code": ResponseCodeStatus.OK,
                "message": "success",
                "data": response.data,
            }
        elif isinstance(response.data, dict):
            if not ("result" in response.data):
                response.data = {
                    "result": True,
                    "code": ResponseCodeStatus.OK,
                    "message": "success",
                    "data": response.data,
                }
            else:
                response.data = {
                    "result": response.data["result"],
                    "code": ResponseCodeStatus.OK,
                    "message": response.data.get("message"),
                    "data": response.data,
                }
        if response.status_code == status.HTTP_204_NO_CONTENT and request.method == "DELETE":
            response.status_code = status.HTTP_200_OK

        return super(ApiGenericMixin, self).finalize_response(request, response, *args, **kwargs)


class ApiGatewayMixin(object):
    """对外开放API返回格式统一
    错误码返回规范为数字：
        正确：0
        错误：39XXXXX
    """

    permission_classes = ()

    def finalize_response(self, request, response, *args, **kwargs):
        """统一数据返回格式"""

        if not isinstance(response, Response):
            return response

        if response.data is None:
            response.data = {"result": True, "code": 0, "message": "success", "data": []}
        elif isinstance(response.data, (list, tuple)):
            response.data = {
                "result": True,
                "code": 0,
                "message": "success",
                "data": response.data,
            }
        elif isinstance(response.data, dict) and not ("code" in response.data and "result" in response.data):
            response.data = {
                "result": True,
                "code": 0,
                "message": "success",
                "data": response.data,
            }

        return super(ApiGatewayMixin, self).finalize_response(request, response, *args, **kwargs)
