from applications.flow.models import ProcessRun, NodeRun, Process, Node, SubProcessRun, SubNodeRun
from applications.utils.dag_helper import PipelineBuilder, instance_dag


def build_and_create_process(process_id):
    """构建pipeline和创建运行时数据"""
    p_builder = PipelineBuilder(process_id)
    pipeline = p_builder.build()

    process = p_builder.process
    node_map = p_builder.node_map
    process_run_uuid = p_builder.instance

    # 保存的实例数据
    process_run_data = process.clone_data
    process_run_data["dag"] = instance_dag(process_run_data["dag"], process_run_uuid)
    process_run = ProcessRun.objects.create(process_id=process.id, root_id=pipeline["id"], **process_run_data)
    node_run_bulk = []
    for pipeline_id, node in node_map.items():
        _node = {k: v for k, v in node.__dict__.items() if k in NodeRun.field_names()}
        _node["uuid"] = process_run_uuid[pipeline_id].id
        node_run_bulk.append(NodeRun(process_run=process_run, **_node))
        if node.node_type == Node.SUB_PROCESS_NODE:
            create_subprocess(node.content, process_run.id, process_run_uuid, pipeline["id"])
    NodeRun.objects.bulk_create(node_run_bulk, batch_size=500)
    return pipeline


def create_subprocess(process_id, process_run_id, process_run_uuid, root_id):
    process = Process.objects.filter(id=process_id).first()
    process_run_data = process.clone_data
    process_run_data["dag"] = instance_dag(process_run_data["dag"], process_run_uuid)
    process_run = SubProcessRun.objects.create(process_id=process_id, process_run_id=process_run_id, root_id=root_id,
                                               **process_run_data)
    subprocess_node_map = Node.objects.filter(process_id=process_id).in_bulk(field_name="uuid")
    node_run_bulk = []
    for pipeline_id, node in subprocess_node_map.items():
        _node = {k: v for k, v in node.__dict__.items() if k in NodeRun.field_names()}
        _node["uuid"] = process_run_uuid[pipeline_id].id
        node_run_bulk.append(SubNodeRun(subprocess_run=process_run, **_node))
        if node.node_type == Node.SUB_PROCESS_NODE:
            create_subprocess(node.content, process_run_id, process_run_uuid, root_id)
    SubNodeRun.objects.bulk_create(node_run_bulk, batch_size=500)
