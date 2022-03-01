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


def hydrate_node_data(node):
    """
    替换当前节点的 data 中的变量
    :param node:
    :return:
    """
    data = node.data
    hydrated = hydrate_data(data.get_inputs())
    data.get_inputs().update(hydrated)


def hydrate_data(data):
    hydrated = {}
    for k, v in list(data.items()):
        from pipeline.core.data import var

        if issubclass(v.__class__, var.Variable):
            hydrated[k] = v.get()
        else:
            hydrated[k] = v
    return hydrated


def hydrate_subprocess_context(subprocess_act):
    # hydrate data
    hydrate_node_data(subprocess_act)

    # context injection
    data = subprocess_act.pipeline.data
    context = subprocess_act.pipeline.context
    for k, v in list(data.get_inputs().items()):
        context.set_global_var(k, v)

    hydrated = hydrate_data(context.variables)
    context.update_global_var(hydrated)
