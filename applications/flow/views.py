from bamboo_engine import api
from bamboo_engine.builder import *
from django.http import JsonResponse
from pipeline.eri.runtime import BambooDjangoRuntime
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from applications.flow.models import Process, Node
from applications.flow.serializers import ProcessViewSetsSerializer, ListProcessViewSetsSerializer, \
    RetrieveProcessViewSetsSerializer, ExecuteProcessSerializer
from applications.utils.dag_helper import DAG
from component.drf.viewsets import GenericViewSet


class ProcessViewSets(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      GenericViewSet):
    serializer_class = ProcessViewSetsSerializer
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
        process = Process.objects.filter(id=process_id).first()
        node_map = Node.objects.filter(process_id=process_id).in_bulk(field_name="uuid")
        dag_obj = DAG()
        dag_obj.from_dict(process.dag)
        topological_sort = dag_obj.topological_sort()
        start = pipeline_tree = EmptyStartEvent()

        for pipeline_id in topological_sort[1:]:
            if node_map[pipeline_id].node_type == 0:
                act = EmptyStartEvent()
            elif node_map[pipeline_id].node_type == 1:
                act = EmptyEndEvent()
            else:
                act = ServiceActivity(component_code="http_request")
            pipeline_tree = getattr(pipeline_tree, "extend")(act)

        pipeline_data = Data()
        pipeline = builder.build_tree(start, data=pipeline_data)
        print(pipeline)
        runtime = BambooDjangoRuntime()
        api.run_pipeline(runtime=runtime, pipeline=pipeline)
        return Response({})


# Create your views here.
def flow(request):
    # 使用 builder 构造出流程描述结构
    start = EmptyStartEvent()
    act = ServiceActivity(component_code="http_request")

    act2 = ServiceActivity(component_code="fac_cal_comp")
    act2.component.inputs.n = Var(type=Var.PLAIN, value=50)

    act3 = ServiceActivity(component_code="fac_cal_comp")
    act3.component.inputs.n = Var(type=Var.PLAIN, value=5)

    act4 = ServiceActivity(component_code="fast_execute_job")
    act5 = ServiceActivity(component_code="fast_execute_job")
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

    start.extend(act).extend(eg).connect(act2, act3).to(eg).converge(pg).connect(act4, act5).to(pg).converge(cg).extend(
        end)
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
