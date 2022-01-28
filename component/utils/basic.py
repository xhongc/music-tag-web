# -*- coding: utf-8 -*-

from collections import namedtuple


def tuple_choices(tupl):
    """从django-model的choices转换到namedtuple"""
    return [(t, t) for t in tupl]


def dict_to_namedtuple(dic):
    """从dict转换到namedtuple"""
    return namedtuple("AttrStore", list(dic.keys()))(**dic)


def choices_to_namedtuple(choices):
    """从django-model的choices转换到namedtuple"""
    return dict_to_namedtuple(dict(choices))
