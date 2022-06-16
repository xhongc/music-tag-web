from datetime import datetime
import random
from django.db.models import F

from applications.flow.utils import build_and_create_process
from bamboo_engine import api
from bamboo_engine.builder import *
from django.http import JsonResponse
from pipeline.eri.runtime import BambooDjangoRuntime
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from applications.flow.filters import NodeTemplateFilter
from applications.flow.models import Process, Node, ProcessRun, NodeRun, NodeTemplate, SubProcessRun
from applications.flow.serializers import ProcessViewSetsSerializer, ListProcessViewSetsSerializer, \
    RetrieveProcessViewSetsSerializer, ExecuteProcessSerializer, ListProcessRunViewSetsSerializer, \
    RetrieveProcessRunViewSetsSerializer, NodeTemplateSerializer, ListSubProcessRunViewSetsSerializer, \
    RetrieveSubProcessRunViewSetsSerializer
from applications.utils.dag_helper import DAG, instance_dag, PipelineBuilder
from component.drf.viewsets import GenericViewSet


class ProcessViewSets(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.UpdateModelMixin,
                      GenericViewSet):
    queryset = Process.objects.order_by("-update_time")

    def get_serializer_class(self):
        if self.action == "list":
            return ListProcessViewSetsSerializer
        elif self.action == "retrieve":
            return RetrieveProcessViewSetsSerializer
        elif self.action == "execute":
            return ExecuteProcessSerializer
        return ProcessViewSetsSerializer

    @action(methods=["POST"], detail=False)
    def execute(self, request, *args, **kwargs):
        validated_data = self.is_validated_data(request.data)
        process_id = validated_data["process_id"]
        pipeline = build_and_create_process(process_id)
        # 执行
        runtime = BambooDjangoRuntime()
        api.run_pipeline(runtime=runtime, pipeline=pipeline)

        Process.objects.filter(id=process_id).update(total_run_count=F("total_run_count") + 1)

        return Response({})


class ProcessRunViewSets(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         GenericViewSet):
    queryset = ProcessRun.objects.order_by("-update_time")

    def get_serializer_class(self):
        if self.action == "list":
            return ListProcessRunViewSetsSerializer
        elif self.action == "retrieve":
            return RetrieveProcessRunViewSetsSerializer
        elif self.action == "execute":
            return ExecuteProcessSerializer


class SubProcessRunViewSets(mixins.ListModelMixin,
                            mixins.RetrieveModelMixin,
                            GenericViewSet):
    queryset = SubProcessRun.objects.order_by("-update_time")

    def get_serializer_class(self):
        if self.action == "list":
            return ListSubProcessRunViewSetsSerializer
        elif self.action == "retrieve":
            return RetrieveSubProcessRunViewSetsSerializer


class TestViewSets(GenericViewSet):
    def list(self, request, *args, **kwargs):
        random_list = [1, 1, 1, 1, 1, 1, 1, 1, 1, 0]
        sign = random.choice(random_list)
        if sign:
            return Response({"now": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "data": request.query_params})
        else:
            raise Exception("随机抛出异常")


class NodeTemplateViewSet(mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          mixins.RetrieveModelMixin,
                          GenericViewSet):
    queryset = NodeTemplate.objects.order_by("-id")
    serializer_class = NodeTemplateSerializer
    filterset_class = NodeTemplateFilter


# Create your views here.
def flow(request):
    # 使用 builder 构造出流程描述结构
    start = EmptyStartEvent()
    act = ServiceActivity(component_code="http_request")

    act2 = ServiceActivity(component_code="http_request")
    act2.component.inputs.n = Var(type=Var.PLAIN, value=50)

    act3 = ServiceActivity(component_code="http_request")
    act3.component.inputs.n = Var(type=Var.PLAIN, value=5)

    act4 = ServiceActivity(component_code="http_request")
    act5 = ServiceActivity(component_code="http_request")
    eg = ExclusiveGateway(
        conditions={
            0: '${exe_res} >= 0',
            1: '${exe_res} < 0'
        },
        name='act_2 or act_3'
    )
    pg = ParallelGateway()
    cg = ConvergeGateway()

    end = EmptyEndEvent()

    start.extend(act).extend(eg).connect(act2, act3).to(act2).extend(act4).extend(act5).to(eg).converge(end)
    # 全局变量
    pipeline_data = Data()
    pipeline_data.inputs['${exe_res}'] = NodeOutput(type=Var.PLAIN, source_act=act.id, source_key='exe_res')

    pipeline = builder.build_tree(start, data=pipeline_data)
    print(pipeline)
    # 执行流程对象
    runtime = BambooDjangoRuntime()

    api.run_pipeline(runtime=runtime, pipeline=pipeline)

    result = api.get_pipeline_states(runtime=runtime, root_id=pipeline["id"])

    result_output = api.get_execution_data_outputs(runtime, act.id).data
    # api.pause_pipeline(runtime=runtime, pipeline_id=pipeline["id"])
    return JsonResponse({})
