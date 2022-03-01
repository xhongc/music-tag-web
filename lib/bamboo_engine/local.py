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


# 引擎执行 local


from typing import Optional

from werkzeug.local import Local

from .utils.object import Representable

_local = Local()


class CurrentNodeInfo(Representable):
    def __init__(self, node_id: str, version: str, loop: int):
        self.node_id = node_id
        self.version = version
        self.loop = loop


def set_node_info(node_info: CurrentNodeInfo):
    """
    设置当前进程/线程/协程 Local 中的当前节点信息

    :param node_id: 节点 ID
    :type node_id: str
    :param version: 节点版本
    :type version: str
    :param loop: 重入次数
    :type loop: int
    """
    _local.current_node_info = node_info


def get_node_info() -> Optional[CurrentNodeInfo]:
    """
    获取当前进程/线程/协程正在处理的节点 ID，版本及重入次数

    :return: 节点 ID
    :rtype: [type]
    """
    return getattr(_local, "current_node_info", None)


def clear_node_info():
    """
    清理当前进程/线程/协程 Local 中的当前节点信息
    """
    _local.current_node_info = None
