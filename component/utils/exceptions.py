# -*- coding: utf-8 -*-
import logging

from django.utils.translation import ugettext as _


class BlueException(Exception):
    ERROR_CODE = "0000000"
    MESSAGE = _("APP异常")
    STATUS_CODE = 500
    LOG_LEVEL = logging.ERROR

    def __init__(self, message=None, data=None, *args):
        """
        :param message: 错误消息
        :param data: 其他数据
        :param context: 错误消息 format dict
        :param args: 其他参数
        """
        super(BlueException, self).__init__(*args)
        self.message = self.MESSAGE if message is None else message
        self.data = data

    def render_data(self):
        return self.data

    def response_data(self):
        return {
            "result": False,
            "code": self.ERROR_CODE,
            "message": self.message,
            "data": self.render_data()
        }


class ClientBlueException(BlueException):
    MESSAGE = _("客户端请求异常")
    ERROR_CODE = "40000"
    STATUS_CODE = 400


class ServerBlueException(BlueException):
    MESSAGE = _("服务端服务异常")
    ERROR_CODE = "50000"
    STATUS_CODE = 500


class AuthenticationError(ClientBlueException):
    MESSAGE = _("认证失败")
    ERROR_CODE = "40100"
    STATUS_CODE = 401


class NotAuthenticatedError(ClientBlueException):
    MESSAGE = _("未提供身份验证凭据")
    ERROR_CODE = "40101"
    STATUS_CODE = 401


class PermissionDeniedError(ClientBlueException):
    MESSAGE = _("您无权执行此操作")
    ERROR_CODE = "40302"
    STATUS_CODE = 403


class MethodNotAllowedError(ClientBlueException):
    MESSAGE = _("请求方法不被允许")
    ERROR_CODE = "40504"
    STATUS_CODE = 405


class NotAcceptableError(ClientBlueException):
    MESSAGE = _("无法满足请求Accept头")
    ERROR_CODE = "40600"
    STATUS_CODE = 406


class UnsupportedMediaTypeError(ClientBlueException):
    MESSAGE = _("不支持的媒体类型")
    ERROR_CODE = "41500"
    STATUS_CODE = 415


class ThrottledError(ClientBlueException):
    MESSAGE = _("请求被限制")
    ERROR_CODE = "42900"
    STATUS_CODE = 429


class DeleteError(ServerBlueException):
    MESSAGE = _("数据删除失败")
    ERROR_CODE = "50001"
    STATUS_CODE = 500


class UpdateError(ServerBlueException):
    MESSAGE = _("数据更新失败")
    ERROR_CODE = "50002"
    STATUS_CODE = 500


class BkEsbReturnError(ServerBlueException):
    MESSAGE = _("ESB调用返回错误")
    ERROR_CODE = "50302"
    STATUS_CODE = 503


class ParamValidationError(ClientBlueException):
    MESSAGE = _("参数验证失败")
    ERROR_CODE = "40000"
    STATUS_CODE = 400


class ResourceNotFound(ClientBlueException):
    MESSAGE = _("找不到请求的资源")
    ERROR_CODE = "40400"
    STATUS_CODE = 404
