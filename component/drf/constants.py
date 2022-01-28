# -*- coding: utf-8 -*-

from component.utils import choices_to_namedtuple, tuple_choices

# 返回状态码
CODE_STATUS_TUPLE = (
    "OK",
    "UNAUTHORIZED",
    "VALIDATE_ERROR",
    "METHOD_NOT_ALLOWED",
    "PERMISSION_DENIED",
    "SERVER_500_ERROR",
    "OBJECT_NOT_EXIST",
)
CODE_STATUS_CHOICES = tuple_choices(CODE_STATUS_TUPLE)
ResponseCodeStatus = choices_to_namedtuple(CODE_STATUS_CHOICES)

# 常规字段长度定义
LEN_SHORT = 32
LEN_NORMAL = 64
LEN_MIDDLE = 128
LEN_LONG = 255
LEN_X_LONG = 1000
LEN_XX_LONG = 10000
LEN_XXX_LONG = 20000

# 字段默认值
EMPTY_INT = 0
EMPTY_STRING = ""
EMPTY_LIST = []
EMPTY_DICT = {}
