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

from copy import deepcopy

from django.utils.module_loading import import_string

from pipeline import exceptions
from pipeline.component_framework.library import ComponentLibrary
from pipeline.core.constants import PE
from pipeline.core.data.base import DataObject
from pipeline.core.data.context import Context
from pipeline.core.data.converter import get_variable
from pipeline.core.data.hydration import hydrate_node_data, hydrate_subprocess_context
from pipeline.core.flow import (
    Condition,
    ConditionalParallelGateway,
    ConvergeGateway,
    ExclusiveGateway,
    FlowNodeClsFactory,
    ParallelGateway,
    SequenceFlow,
)
from pipeline.core.pipeline import Pipeline, PipelineSpec
from pipeline.validators.base import validate_pipeline_tree


def classify_inputs(pipeline_inputs, params, is_subprocess, root_pipeline_params=None):
    """
    @summary: classify pipeline inputs into different parts
    @param pipeline_inputs: pipeline or subprocess inputs
    @param params: pipeline or subprocess params, which can cover item whose is_param is True in inputs
    @param is_subprocess: whether pipeline is root or subprocess
    @param root_pipeline_params: root pipeline params which should deliver to all subprocess
    @return:
    """
    # data from activity outputs
    act_outputs = {}
    # params should deliver to son subprocess
    subprocess_params = {}
    # context scope to resolving inputs
    scope_info = deepcopy(root_pipeline_params)
    for key, info in list(pipeline_inputs.items()):
        source_act = info.get(PE.source_act)
        if isinstance(source_act, str):
            act_outputs.setdefault(info[PE.source_act], {}).update({info[PE.source_key]: key})
            continue
        elif isinstance(source_act, list):
            for source_info in source_act:
                act_outputs.setdefault(source_info[PE.source_act], {}).update({source_info[PE.source_key]: key})

        is_param = info.get(PE.is_param, False)
        info = params.get(key, info) if is_param else info
        if is_subprocess and is_param:
            subprocess_params.update({key: info})
            continue

        scope_info.update({key: info})
    result = {"act_outputs": act_outputs, "scope_info": scope_info, "subprocess_params": subprocess_params}
    return result


class PipelineParser(object):
    def __init__(self, pipeline_tree, cycle_tolerate=False):
        validate_pipeline_tree(pipeline_tree, cycle_tolerate=cycle_tolerate)
        self.pipeline_tree = deepcopy(pipeline_tree)
        self.cycle_tolerate = cycle_tolerate

    def parse(self, root_pipeline_data=None, root_pipeline_context=None):
        """
        @summary: parse pipeline json tree to object with root data
        @param root_pipeline_data: like business info or operator, which can be accessed by parent_data in
            Component.execute
        @param root_pipeline_context: params for pipeline to resolving inputs data
        @return:
        """
        return self._parse(root_pipeline_data, root_pipeline_context)

    def _parse(
        self, root_pipeline_data=None, root_pipeline_params=None, params=None, is_subprocess=False, parent_context=None
    ):
        """
        @summary: parse pipeline and subprocess recursively
        @param root_pipeline_data: root data from root pipeline parsing, witch will be passed to subprocess recursively
        @param root_pipeline_params: params from root pipeline for all subprocess
        @param params: params from parent for son subprocess
        @param is_subprocess: whither is subprocess
        @param parent_context: parent context for activity of subprocess to resolving inputs
        @return: Pipeline object
        """
        if root_pipeline_data is None:
            root_pipeline_data = {}
        if root_pipeline_params is None:
            root_pipeline_params = {}
        if params is None:
            params = {}

        pipeline_inputs = self.pipeline_tree[PE.data][PE.inputs]
        classification = classify_inputs(pipeline_inputs, params, is_subprocess, root_pipeline_params)

        output_keys = self.pipeline_tree[PE.data][PE.outputs]
        context = Context(classification["act_outputs"], output_keys)
        for key, info in list(classification["scope_info"].items()):
            var = get_variable(key, info, context, root_pipeline_data)
            context.set_global_var(key, var)

        pipeline_data = deepcopy(root_pipeline_data)
        if is_subprocess:
            if parent_context is None:
                raise exceptions.DataTypeErrorException("parent context of subprocess cannot be none")
            for key, info in list(classification["subprocess_params"].items()):
                var = get_variable(key, info, parent_context, pipeline_data)
                pipeline_data.update({key: var})

        start = self.pipeline_tree[PE.start_event]
        start_cls = FlowNodeClsFactory.get_node_cls(start[PE.type])
        if "pre_render_keys" in self.pipeline_tree[PE.data]:
            start_event = start_cls(
                id=start[PE.id],
                name=start[PE.name],
                data=DataObject({"pre_render_keys": self.pipeline_tree[PE.data][PE.pre_render_keys]}),
            )
        else:
            start_event = start_cls(id=start[PE.id], name=start[PE.name])

        end = self.pipeline_tree[PE.end_event]
        end_cls = FlowNodeClsFactory.get_node_cls(end[PE.type])
        end_event = end_cls(id=end[PE.id], name=end[PE.name], data=DataObject({}))

        acts = self.pipeline_tree[PE.activities]
        act_objs = []
        for act in list(acts.values()):
            act_cls = FlowNodeClsFactory.get_node_cls(act[PE.type])
            if act[PE.type] == PE.ServiceActivity:
                component = ComponentLibrary.get_component(
                    component_code=act[PE.component][PE.code],
                    data_dict=act[PE.component][PE.inputs],
                    version=act[PE.component].get(PE.version),
                )
                service = component.service()
                data = component.data_for_execution(context, pipeline_data)
                handler_path = act.get("failure_handler")
                failure_handler = import_string(handler_path) if handler_path else None
                act_objs.append(
                    act_cls(
                        id=act[PE.id],
                        service=service,
                        name=act[PE.name],
                        data=data,
                        error_ignorable=act.get(PE.error_ignorable, False),
                        skippable=act[PE.skippable] if PE.skippable in act else act.get(PE.skippable_old, True),
                        retryable=act[PE.retryable] if PE.retryable in act else act.get(PE.retryable_old, True),
                        timeout=act.get(PE.timeout),
                        failure_handler=failure_handler,
                    )
                )
            elif act[PE.type] == PE.SubProcess:
                sub_tree = act[PE.pipeline]
                params = act[PE.params]
                sub_parser = PipelineParser(pipeline_tree=sub_tree, cycle_tolerate=self.cycle_tolerate)
                act_objs.append(
                    act_cls(
                        id=act[PE.id],
                        pipeline=sub_parser._parse(
                            root_pipeline_data=root_pipeline_data,
                            root_pipeline_params=root_pipeline_params,
                            params=params,
                            is_subprocess=True,
                            parent_context=context,
                        ),
                        name=act[PE.name],
                    )
                )
            else:
                raise exceptions.FlowTypeError("Unknown Activity type: %s" % act[PE.type])

        gateways = self.pipeline_tree[PE.gateways]
        flows = self.pipeline_tree[PE.flows]
        gateway_objs = []
        for gw in list(gateways.values()):
            gw_cls = FlowNodeClsFactory.get_node_cls(gw[PE.type])
            if gw[PE.type] in {PE.ParallelGateway, PE.ConditionalParallelGateway}:
                gateway_objs.append(
                    gw_cls(id=gw[PE.id], converge_gateway_id=gw[PE.converge_gateway_id], name=gw[PE.name])
                )
            elif gw[PE.type] in {PE.ExclusiveGateway, PE.ConvergeGateway}:
                gateway_objs.append(gw_cls(id=gw[PE.id], name=gw[PE.name]))
            else:
                raise exceptions.FlowTypeError("Unknown Gateway type: %s" % gw[PE.type])

        flow_objs_dict = {}
        for fl in list(flows.values()):
            flow_nodes = act_objs + gateway_objs
            if fl[PE.source] == start[PE.id]:
                source = start_event
            else:
                source = [x for x in flow_nodes if x.id == fl[PE.source]][0]
            if fl[PE.target] == end[PE.id]:
                target = end_event
            else:
                target = [x for x in flow_nodes if x.id == fl[PE.target]][0]
            flow_objs_dict[fl[PE.id]] = SequenceFlow(fl[PE.id], source, target)
        flow_objs = list(flow_objs_dict.values())

        # add incoming and outgoing flow to acts
        if not isinstance(start[PE.outgoing], list):
            start[PE.outgoing] = [start[PE.outgoing]]
        for outgoing_id in start[PE.outgoing]:
            start_event.outgoing.add_flow(flow_objs_dict[outgoing_id])

        if not isinstance(end[PE.incoming], list):
            end[PE.incoming] = [end[PE.incoming]]
        for incoming_id in end[PE.incoming]:
            end_event.incoming.add_flow(flow_objs_dict[incoming_id])

        for act in act_objs:
            incoming = acts[act.id][PE.incoming]
            if isinstance(incoming, list):
                for s in incoming:
                    act.incoming.add_flow(flow_objs_dict[s])
            else:
                act.incoming.add_flow(flow_objs_dict[incoming])

            act.outgoing.add_flow(flow_objs_dict[acts[act.id][PE.outgoing]])

        for gw in gateway_objs:
            if isinstance(gw, ExclusiveGateway) or isinstance(gw, ConditionalParallelGateway):
                for flow_id, con in list(gateways[gw.id][PE.conditions].items()):
                    con_obj = Condition(con[PE.evaluate], flow_objs_dict[flow_id])
                    gw.add_condition(con_obj)

                if isinstance(gateways[gw.id][PE.incoming], list):
                    for incoming_id in gateways[gw.id][PE.incoming]:
                        gw.incoming.add_flow(flow_objs_dict[incoming_id])
                else:
                    gw.incoming.add_flow(flow_objs_dict[gateways[gw.id][PE.incoming]])

                for outgoing_id in gateways[gw.id][PE.outgoing]:
                    gw.outgoing.add_flow(flow_objs_dict[outgoing_id])

            elif isinstance(gw, ParallelGateway):
                if isinstance(gateways[gw.id][PE.incoming], list):
                    for incoming_id in gateways[gw.id][PE.incoming]:
                        gw.incoming.add_flow(flow_objs_dict[incoming_id])
                else:
                    gw.incoming.add_flow(flow_objs_dict[gateways[gw.id][PE.incoming]])

                for outgoing_id in gateways[gw.id][PE.outgoing]:
                    gw.outgoing.add_flow(flow_objs_dict[outgoing_id])

            elif isinstance(gw, ConvergeGateway):
                for incoming_id in gateways[gw.id][PE.incoming]:
                    gw.incoming.add_flow(flow_objs_dict[incoming_id])
                gw.outgoing.add_flow(flow_objs_dict[gateways[gw.id][PE.outgoing]])

            else:
                raise exceptions.FlowTypeError("Unknown Gateway type: %s" % type(gw))

        context.duplicate_variables()
        pipeline_data = DataObject(pipeline_data)
        pipeline_spec = PipelineSpec(start_event, end_event, flow_objs, act_objs, gateway_objs, pipeline_data, context)
        return Pipeline(self.pipeline_tree[PE.id], pipeline_spec)

    def get_act(self, act_id, subprocess_stack=None, root_pipeline_data=None, root_pipeline_context=None):
        if subprocess_stack is None:
            subprocess_stack = []
        pipeline = self.parse(root_pipeline_data, root_pipeline_context)
        for sub_id in subprocess_stack:
            subprocess_act = [x for x in pipeline.spec.activities if x.id == sub_id][0]
            hydrate_subprocess_context(subprocess_act)
            pipeline = subprocess_act.pipeline
        act = [x for x in pipeline.spec.activities if x.id == act_id][0]
        return act

    def get_act_inputs(self, act_id, subprocess_stack=None, root_pipeline_data=None, root_pipeline_context=None):
        act = self.get_act(act_id, subprocess_stack, root_pipeline_data, root_pipeline_context)
        hydrate_node_data(act)
        inputs = act.data.inputs
        return inputs
