import json

from bamboo_engine import api
from django.db import transaction
from pipeline.eri.runtime import BambooDjangoRuntime
from rest_framework import serializers

from applications.flow.constants import PIPELINE_STATE_TO_FLOW_STATE
from applications.flow.models import Process, Node, ProcessRun, NodeRun, NodeTemplate
from applications.utils.uuid_helper import get_uuid


class ProcessViewSetsSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    description = serializers.CharField(required=False, allow_blank=True)
    category = serializers.ListField(default="null")
    run_type = serializers.CharField(default="null")
    pipeline_tree = serializers.JSONField(required=True)

    def save(self, **kwargs):
        if self.instance is not None:
            self.update(instance=self.instance, validated_data=self.validated_data)
        else:
            self.create(validated_data=self.validated_data)

    def create(self, validated_data):
        node_map = {}
        for node in validated_data["pipeline_tree"]["nodes"]:
            node_map[node["uuid"]] = node
        dag = {k: [] for k in node_map.keys()}
        for line in self.validated_data["pipeline_tree"]["lines"]:
            dag[line["from"]].append(line["to"])
        with transaction.atomic():
            process = Process.objects.create(name=validated_data["name"],
                                             description=validated_data["description"],
                                             run_type=validated_data["run_type"],
                                             dag=dag)
            bulk_nodes = []
            for node in node_map.values():
                node_data = node["node_data"]
                if isinstance(node_data["inputs"], dict):
                    node_inputs = node_data["inputs"]
                else:
                    node_inputs = json.loads(node_data["inputs"])
                bulk_nodes.append(Node(process=process,
                                       name=node_data["node_name"],
                                       uuid=node["uuid"],
                                       description=node_data["description"],
                                       fail_retry_count=node_data.get("fail_retry_count", 0) or 0,
                                       fail_offset=node_data.get("fail_offset", 0) or 0,
                                       fail_offset_unit=node_data.get("fail_offset_unit", "seconds"),
                                       node_type=node.get("type", 2),
                                       is_skip_fail=node_data["is_skip_fail"],
                                       is_timeout_alarm=node_data["is_skip_fail"],
                                       inputs=node_inputs,
                                       show=node["show"],
                                       top=node["top"],
                                       left=node["left"],
                                       ico=node["ico"],
                                       outputs={},
                                       component_code="http_request",
                                       content=node.get("content", 0) or 0
                                       ))
            Node.objects.bulk_create(bulk_nodes, batch_size=500)
        self._data = {}

    def update(self, instance, validated_data):
        node_map = {}
        for node in validated_data["pipeline_tree"]["nodes"]:
            node_map[node["uuid"]] = node
        dag = {k: [] for k in node_map.keys()}
        for line in self.validated_data["pipeline_tree"]["lines"]:
            dag[line["from"]].append(line["to"])
        with transaction.atomic():
            instance.name = validated_data["name"]
            instance.description = validated_data["description"]
            instance.run_type = validated_data["run_type"]
            instance.dag = dag
            instance.save()
            bulk_update_nodes = []
            bulk_create_nodes = []
            node_dict = Node.objects.filter(process_id=instance.id).in_bulk(field_name="uuid")
            for node in node_map.values():
                node_data = node["node_data"]
                node_obj = node_dict.get(node["uuid"], None)
                if isinstance(node_data["inputs"], dict):
                    node_inputs = node_data["inputs"]
                else:
                    node_inputs = json.loads(node_data["inputs"])
                if node_obj:
                    node_obj.content = node.get("content", 0) or 0
                    node_obj.name = node_data["node_name"]
                    node_obj.description = node_data["description"]
                    node_obj.fail_retry_count = node_data.get("fail_retry_count", 0) or 0
                    node_obj.fail_offset = node_data.get("fail_offset", 0) or 0
                    node_obj.fail_offset_unit = node_data.get("fail_offset_unit", "seconds")
                    node_obj.node_type = node.get("type", 3)
                    node_obj.is_skip_fail = node_data["is_skip_fail"]
                    node_obj.is_timeout_alarm = node_data["is_timeout_alarm"]
                    node_obj.inputs = node_inputs
                    node_obj.show = node["show"]
                    node_obj.top = node["top"]
                    node_obj.left = node["left"]
                    node_obj.ico = node["ico"]
                    node_obj.outputs = {}
                    node_obj.component_code = "http_request"
                    bulk_update_nodes.append(node_obj)
                else:
                    node_obj = Node()
                    node_obj.content = node.get("content", 0) or 0
                    node_obj.name = node_data["node_name"]
                    node_obj.description = node_data["description"]
                    node_obj.fail_retry_count = node_data.get("fail_retry_count", 0) or 0
                    node_obj.fail_offset = node_data.get("fail_offset", 0) or 0
                    node_obj.fail_offset_unit = node_data.get("fail_offset_unit", "seconds")
                    node_obj.node_type = node.get("type", 3)
                    node_obj.is_skip_fail = node_data["is_skip_fail"]
                    node_obj.is_timeout_alarm = node_data["is_timeout_alarm"]
                    node_obj.inputs = node_inputs
                    node_obj.show = node["show"]
                    node_obj.top = node["top"]
                    node_obj.left = node["left"]
                    node_obj.ico = node["ico"]
                    node_obj.outputs = {}
                    node_obj.component_code = "http_request"
                    node_obj.uuid = node["uuid"]
                    node_obj.process_id = instance.id
                    bulk_create_nodes.append(node_obj)
            Node.objects.bulk_update(bulk_update_nodes,
                                     fields=["name", "description", "fail_retry_count", "fail_offset",
                                             "fail_offset_unit", "node_type", "is_skip_fail",
                                             "is_timeout_alarm", "inputs", "show", "top", "left", "ico",
                                             "outputs", "component_code"], batch_size=500)
            Node.objects.bulk_create(bulk_create_nodes, batch_size=500)
        self._data = {}


class ListProcessViewSetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        # fields = "__all__"
        exclude = ("dag",)


class ListProcessRunViewSetsSerializer(serializers.ModelSerializer):
    state = serializers.SerializerMethodField()

    class Meta:
        model = ProcessRun
        fields = "__all__"

    def get_state(self, obj):
        runtime = BambooDjangoRuntime()
        process_info = api.get_pipeline_states(runtime, root_id=obj.root_id)
        try:
            process_state = PIPELINE_STATE_TO_FLOW_STATE.get(process_info.data[obj.root_id]["state"])
        except Exception:
            process_state = "error"
        return process_state


class RetrieveProcessViewSetsSerializer(serializers.ModelSerializer):
    pipeline_tree = serializers.SerializerMethodField()

    # category = serializers.SerializerMethodField()
    #
    # def get_category(self, obj):
    #     return obj.category.all()

    def get_pipeline_tree(self, obj):
        lines = []
        nodes = []
        for _from, to_list in obj.dag.items():
            for _to in to_list:
                lines.append({
                    "from": _from,
                    "to": _to
                })
        node_list = Node.objects.filter(process_id=obj.id).values()
        node_content_id = [node["content"] for node in node_list if node.get("content", 0)]
        content_map = NodeTemplate.objects.filter(id__in=node_content_id).in_bulk()
        for node in node_list:
            node_template = content_map.get(node.get("content", 0), "")
            inputs_component = ""
            if node_template:
                inputs_component = json.dumps(node_template.inputs_component)
            nodes.append({"show": node["show"],
                          "top": node["top"],
                          "left": node["left"],
                          "ico": node["ico"],
                          "type": node["node_type"],
                          "name": node["name"],
                          "content": node["content"],
                          "node_data": {
                              "inputs": json.dumps(node["inputs"]),
                              "inputs_component": inputs_component,
                              "run_mark": 0,
                              "node_name": node["name"],
                              "description": node["description"],
                              "fail_retry_count": node["fail_retry_count"],
                              "fail_offset": node["fail_offset"],
                              "fail_offset_unit": node["fail_offset_unit"],
                              "is_skip_fail": node["is_skip_fail"],
                              "is_timeout_alarm": node["is_timeout_alarm"]},
                          "uuid": node["uuid"]})
        return {"lines": lines, "nodes": nodes}

    class Meta:
        model = Process
        fields = ("id", "name", "description", "category", "run_type", "pipeline_tree")


class RetrieveProcessRunViewSetsSerializer(serializers.ModelSerializer):
    pipeline_tree = serializers.SerializerMethodField()

    def get_pipeline_tree(self, obj):
        lines = []
        nodes = []
        for _from, to_list in obj.dag.items():
            for _to in to_list:
                lines.append({
                    "from": _from,
                    "to": _to
                })
        runtime = BambooDjangoRuntime()
        process_info = api.get_pipeline_states(runtime, root_id=obj.root_id)
        process_state = PIPELINE_STATE_TO_FLOW_STATE.get(process_info.data[obj.root_id]["state"])
        state_map = process_info.data[obj.root_id]["children"]
        node_list = NodeRun.objects.filter(process_run_id=obj.id).values()
        for node in node_list:
            pipeline_state = state_map.get(node["uuid"], {}).get("state", "READY")
            flow_state = PIPELINE_STATE_TO_FLOW_STATE[pipeline_state]
            outputs = ""
            print(flow_state)
            if node["node_type"] not in [0, 1] and flow_state not in ["wait"]:
                output_data = api.get_execution_data_outputs(runtime, node_id=node["uuid"])
                outputs = output_data.data.get("outputs", "")
            # todo先简单判断node有fail，process就为fail
            if flow_state == "fail":
                process_state = "fail"
            nodes.append({"show": node["show"],
                          "top": node["top"],
                          "left": node["left"],
                          "ico": node["ico"],
                          "type": node["node_type"],
                          "name": node["name"],
                          "state": flow_state,
                          "node_data": {
                              "inputs": node["inputs"],
                              "outputs": outputs,
                              "run_mark": 0,
                              "node_name": node["name"],
                              "description": node["description"],
                              "fail_retry_count": node["fail_retry_count"],
                              "fail_offset": node["fail_offset"],
                              "fail_offset_unit": node["fail_offset_unit"],
                              "is_skip_fail": node["is_skip_fail"],
                              "is_timeout_alarm": node["is_timeout_alarm"]},
                          "uuid": node["uuid"]})
        return {"lines": lines, "nodes": nodes, "process_state": process_state}

    class Meta:
        model = ProcessRun
        fields = ("id", "name", "description", "run_type", "pipeline_tree")


class ExecuteProcessSerializer(serializers.Serializer):
    process_id = serializers.IntegerField(required=True)


class NodeTemplateSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        attrs["uuid"] = get_uuid()
        return attrs

    class Meta:
        model = NodeTemplate
        exclude = ("uuid",)
