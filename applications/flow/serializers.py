from django.db import transaction
from rest_framework import serializers

from applications.flow.models import Process, Node


class ProcessViewSetsSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    description = serializers.CharField(required=False, allow_blank=True)
    category = serializers.ListField(default="null")
    run_type = serializers.CharField(default="null")
    pipeline_tree = serializers.JSONField(required=True)

    def save(self, **kwargs):
        node_map = {}
        for node in self.validated_data["pipeline_tree"]["nodes"]:
            node_map[node["uuid"]] = node
        dag = {k: [] for k in node_map.keys()}
        for line in self.validated_data["pipeline_tree"]["lines"]:
            dag[line["from"]].append(line["to"])
        with transaction.atomic():
            process = Process.objects.create(name=self.validated_data["name"],
                                             description=self.validated_data["description"],
                                             run_type=self.validated_data["run_type"],
                                             dag=dag)
            bulk_nodes = []
            for node in node_map.values():
                node_data = node["node_data"]
                bulk_nodes.append(Node(process=process,
                                       name=node_data["node_name"],
                                       uuid=node["uuid"],
                                       description=node_data["description"],
                                       fail_retry_count=node_data.get("fail_retry_count", 0) or 0,
                                       fail_offset=node_data.get("fail_offset", 0) or 0,
                                       fail_offset_unit=node_data.get("fail_offset_unit", "seconds"),
                                       node_type=node.get("type", 3),
                                       is_skip_fail=node_data["is_skip_fail"],
                                       is_timeout_alarm=node_data["is_skip_fail"],
                                       inputs=node_data["inputs"],
                                       show=node["show"],
                                       top=node["top"],
                                       left=node["left"],
                                       ico=node["ico"],
                                       outputs={},
                                       component_code="http_request"
                                       ))
            Node.objects.bulk_create(bulk_nodes, batch_size=500)


class ListProcessViewSetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = "__all__"


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
        for node in node_list:
            nodes.append({"show": node["show"],
                          "top": node["top"],
                          "left": node["left"],
                          "ico": node["ico"],
                          "type": node["node_type"],
                          "name": node["name"],
                          "node_data": {
                              "inputs": node["inputs"],
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


class ExecuteProcessSerializer(serializers.Serializer):
    process_id = serializers.IntegerField(required=True)
