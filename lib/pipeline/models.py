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

import copy
import hashlib
import logging
import queue
import zlib

import ujson as json
from django.db import models, transaction
from django.utils import timezone
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _

from pipeline.conf import settings
from pipeline.constants import PIPELINE_DEFAULT_PRIORITY
from pipeline.core.constants import PE
from pipeline.signals import post_pipeline_finish, post_pipeline_revoke
from pipeline.engine.utils import ActionResult, calculate_elapsed_time
from pipeline.exceptions import SubprocessRefError
from pipeline.parser.context import get_pipeline_context
from pipeline.parser.utils import replace_all_id
from pipeline.service import task_service
from pipeline.utils.graph import Graph
from pipeline.utils.uniqid import node_uniqid, uniqid

MAX_LEN_OF_NAME = 128
logger = logging.getLogger("root")


class CompressJSONField(models.BinaryField):
    def __init__(self, compress_level=6, *args, **kwargs):
        super(CompressJSONField, self).__init__(*args, **kwargs)
        self.compress_level = compress_level

    def get_prep_value(self, value):
        value = super(CompressJSONField, self).get_prep_value(value)
        return zlib.compress(json.dumps(value).encode("utf-8"), self.compress_level)

    def to_python(self, value):
        value = super(CompressJSONField, self).to_python(value)
        return json.loads(zlib.decompress(value).decode("utf-8"))

    def from_db_value(self, value, expression, connection, context=None):
        return self.to_python(value)


class SnapshotManager(models.Manager):
    def create_snapshot(self, data):
        h = hashlib.md5()
        h.update(json.dumps(data).encode("utf-8"))
        snapshot = self.create(md5sum=h.hexdigest(), data=data)
        return snapshot

    def data_for_snapshot(self, snapshot_id):
        return self.get(id=snapshot_id).data


class Snapshot(models.Model):
    """
    数据快照
    """

    md5sum = models.CharField(_("快照字符串的md5sum"), max_length=32, db_index=True)
    create_time = models.DateTimeField(_("创建时间"), auto_now_add=True)
    data = CompressJSONField(null=True, blank=True)

    objects = SnapshotManager()

    class Meta:
        verbose_name = _("模板快照")
        verbose_name_plural = _("模板快照")
        ordering = ["-id"]
        app_label = "pipeline"

    def __unicode__(self):
        return str(self.md5sum)

    def has_change(self, data):
        """
        检测 data 的 md5 是否和当前存储的不一致
        @param data:
        @return: 新的 md5，md5 是否有变化
        """
        h = hashlib.md5()
        h.update(json.dumps(data).encode("utf-8"))
        md5 = h.hexdigest()
        return md5, self.md5sum != md5


class TreeInfo(models.Model):
    """
    pipeline 数据信息
    """

    data = CompressJSONField(null=True, blank=True)


def get_subprocess_act_list(pipeline_data):
    """
    获取 pipeline 结构中所有的子流程节点
    @param pipeline_data: 流程结构数据
    @return: 子流程节点
    """
    activities = pipeline_data[PE.activities]
    act_ids = [act_id for act_id in activities if activities[act_id][PE.type] == PE.SubProcess]
    return [activities[act_id] for act_id in act_ids]


def _act_id_in_graph(act):
    """
    获取子流程节点引用的模板 ID
    @param act: 子流程节点
    @return: 模板 ID:版本 或 模板ID
    """
    return "{}:{}".format(act["template_id"], act["version"]) if act.get("version") else act["template_id"]


class TemplateManager(models.Manager):
    def subprocess_ref_validate(self, data, root_id=None, root_name=None):
        """
        验证子流程引用是否合法
        @param data:
        @param root_id:
        @param root_name:
        @return: 引用是否合法，相关信息
        """
        try:
            sub_refs, name_map = self.construct_subprocess_ref_graph(data, root_id=root_id, root_name=root_name)
        except PipelineTemplate.DoesNotExist as e:
            return False, str(e)

        nodes = list(sub_refs.keys())
        flows = []
        for node in nodes:
            for ref in sub_refs[node]:
                if ref in nodes:
                    flows.append([node, ref])
        graph = Graph(nodes, flows)
        # circle reference check
        trace = graph.get_cycle()
        if trace:
            name_trace = " → ".join([name_map[proc_id] for proc_id in trace])
            return False, _("子流程引用链中存在循环引用：%s") % name_trace

        return True, ""

    def create_model(self, structure_data, **kwargs):
        """
        创建流程模板对象
        @param structure_data: pipeline 结构数据
        @param kwargs: 其他参数
        @return: 流程模板
        """
        result, msg = self.subprocess_ref_validate(structure_data)

        if not result:
            raise SubprocessRefError(msg)

        snapshot = Snapshot.objects.create_snapshot(structure_data)
        kwargs["snapshot"] = snapshot
        kwargs["template_id"] = node_uniqid()
        obj = self.create(**kwargs)
        # version track
        # TemplateVersion.objects.track(obj)

        return obj

    def delete_model(self, template_ids):
        """
        删除模板对象
        @param template_ids: 模板对象 ID 列表或 ID
        @return:
        """
        if not isinstance(template_ids, list):
            template_ids = [template_ids]
        qs = self.filter(template_id__in=template_ids)
        for template in qs:
            template.is_deleted = True
            template.name = uniqid()
            template.save()

    def construct_subprocess_ref_graph(self, pipeline_data, root_id=None, root_name=None):
        """
        构造子流程引用图
        @param pipeline_data: pipeline 结构数据
        @param root_id: 所有引用开始的根流程 ID
        @param root_name: 根流程名
        @return: 子流程引用图，模板 ID -> 模板姓名映射字典
        """
        subprocess_act = get_subprocess_act_list(pipeline_data)
        tid_queue = queue.Queue()
        graph = {}
        version = {}
        name_map = {}

        if root_id:
            graph[root_id] = [_act_id_in_graph(act) for act in subprocess_act]
            name_map[root_id] = root_name

        for act in subprocess_act:
            tid_queue.put(_act_id_in_graph(act))
            version[_act_id_in_graph(act)] = act.get("version")

        while not tid_queue.empty():
            tid = tid_queue.get()
            template = self.get(template_id=tid.split(":")[0])
            name_map[tid] = template.name
            subprocess_act = get_subprocess_act_list(template.data_for_version(version[tid]))

            for act in subprocess_act:
                ref_tid = _act_id_in_graph(act)
                graph.setdefault(tid, []).append(ref_tid)
                version[_act_id_in_graph(act)] = act.get("version")
                if ref_tid not in graph:
                    tid_queue.put(ref_tid)
            if not subprocess_act:
                graph[tid] = []

        return graph, name_map

    def unfold_subprocess(self, pipeline_data):
        """
        展开 pipeline 数据中所有的子流程
        @param pipeline_data: pipeline 数据
        @return:
        """
        id_maps = replace_all_id(pipeline_data)
        activities = pipeline_data[PE.activities]
        for act_id, act in list(activities.items()):
            if act[PE.type] == PE.SubProcess:
                subproc_data = self.get(template_id=act[PE.template_id]).data_for_version(act.get(PE.version))

                sub_id_maps = self.unfold_subprocess(subproc_data)
                # act_id is new id
                id_maps[PE.subprocess_detail].update({act_id: sub_id_maps})

                subproc_data[PE.id] = act_id
                act[PE.pipeline] = subproc_data
        return id_maps

    def replace_id(self, pipeline_data):
        """
        替换 pipeline 中所有 ID
        @param pipeline_data: pipeline 数据
        @return:
        """
        id_maps = replace_all_id(pipeline_data)
        activities = pipeline_data[PE.activities]
        for act_id, act in list(activities.items()):
            if act[PE.type] == PE.SubProcess:
                subproc_data = act[PE.pipeline]
                sub_id_maps = self.replace_id(subproc_data)
                # act_id is new id
                id_maps[PE.subprocess_detail].update({act_id: sub_id_maps})

                subproc_data[PE.id] = act_id
                act[PE.pipeline] = subproc_data
        return id_maps


class PipelineTemplate(models.Model):
    """
    流程模板
    """

    template_id = models.CharField(_("模板ID"), max_length=32, unique=True)
    name = models.CharField(_("模板名称"), max_length=MAX_LEN_OF_NAME, default="default_template", db_index=True)
    create_time = models.DateTimeField(_("创建时间"), auto_now_add=True, db_index=True)
    creator = models.CharField(_("创建者"), max_length=32)
    description = models.TextField(_("描述"), null=True, blank=True)
    editor = models.CharField(_("修改者"), max_length=32, null=True, blank=True)
    edit_time = models.DateTimeField(_("修改时间"), auto_now=True, db_index=True)
    snapshot = models.ForeignKey(
        Snapshot, verbose_name=_("模板结构数据"), related_name="snapshot_templates", on_delete=models.DO_NOTHING
    )
    has_subprocess = models.BooleanField(_("是否含有子流程"), default=False)
    is_deleted = models.BooleanField(_("是否删除"), default=False, help_text=_("表示当前模板是否删除"))

    objects = TemplateManager()

    class Meta:
        verbose_name = _("Pipeline模板")
        verbose_name_plural = _("Pipeline模板")
        ordering = ["-edit_time"]
        app_label = "pipeline"

    def __unicode__(self):
        return "{}-{}".format(self.template_id, self.name)

    @property
    def data(self):
        return self.snapshot.data

    @property
    def version(self):
        return self.snapshot.md5sum

    @property
    def subprocess_version_info(self):
        # 1. get all subprocess
        subprocess_info = TemplateRelationship.objects.get_subprocess_info(self.template_id).values(
            "descendant_template_id", "subprocess_node_id", "version", "always_use_latest"
        )
        info = {"subproc_has_update": False, "details": []}
        if not subprocess_info:
            return info

        # 2. check whether subprocess is expired
        temp_current_versions = {
            item.template_id: item
            for item in TemplateCurrentVersion.objects.filter(
                template_id__in=[item["descendant_template_id"] for item in subprocess_info]
            )
        }

        expireds = []
        for item in subprocess_info:
            item["expired"] = (
                False
                if item["version"] is None
                or item["descendant_template_id"] not in temp_current_versions
                or item["always_use_latest"]
                else (item["version"] != temp_current_versions[item["descendant_template_id"]].current_version)
            )
            info["details"].append(item)
            expireds.append(item["expired"])

        info["subproc_has_update"] = any(expireds)

        # 3. return
        return info

    @property
    def subprocess_has_update(self):
        return self.subprocess_version_info["subproc_has_update"]

    def data_for_version(self, version):
        """
        获取某个版本的模板数据
        @param version: 版本号
        @return: 模板数据
        """
        if not version:
            return self.data
        return Snapshot.objects.filter(md5sum=version).order_by("-id").first().data

    def referencer(self):
        """
        获取引用了该模板的其他模板
        @return: 引用了该模板的其他模板 ID 列表
        """
        referencer = TemplateRelationship.objects.referencer(self.template_id)
        template_id = self.__class__.objects.filter(template_id__in=referencer, is_deleted=False).values_list(
            "template_id", flat=True
        )
        return list(template_id)

    def clone_data(self):
        """
        获取该模板数据的克隆
        @return: ID 替换过后的模板数据
        """
        data = self.data
        replace_all_id(self.data)
        return data

    def update_template(self, structure_data, **kwargs):
        """
        更新当前模板的模板数据
        @param structure_data: pipeline 结构数据
        @param kwargs: 其他参数
        @return:
        """
        result, msg = PipelineTemplate.objects.subprocess_ref_validate(structure_data, self.template_id, self.name)
        if not result:
            raise SubprocessRefError(msg)

        snapshot = Snapshot.objects.create_snapshot(structure_data)
        kwargs["snapshot"] = snapshot
        kwargs["edit_time"] = timezone.now()
        exclude_keys = ["template_id", "creator", "create_time", "is_deleted"]
        for key in exclude_keys:
            kwargs.pop(key, None)
        for key, value in list(kwargs.items()):
            setattr(self, key, value)
        self.save()

    def gen_instance(self, inputs=None, **kwargs):
        """
        使用该模板创建实例
        @param inputs: 自定义输入
        @param kwargs: 其他参数
        @return: 实例对象
        """
        instance, _ = PipelineInstance.objects.create_instance(
            template=self, exec_data=copy.deepcopy(self.data), inputs=inputs, **kwargs
        )
        return instance

    def set_has_subprocess_bit(self):
        acts = list(self.data[PE.activities].values())
        self.has_subprocess = any([act["type"] == PE.SubProcess for act in acts])


class TemplateRelationShipManager(models.Manager):
    def get_subprocess_info(self, template_id):
        """
        获取某个模板中所有的子流程信息
        @param template_id: 模板 ID
        @return: 该模板所引用的子流程相关信息
        """
        return self.filter(ancestor_template_id=template_id)

    def referencer(self, template_id):
        """
        获取引用了某个模板的其他模板
        @param template_id: 被引用的模板
        @return: 引用了该模板的其他模板 ID 列表
        """
        return list(set(self.filter(descendant_template_id=template_id).values_list("ancestor_template_id", flat=True)))


class TemplateRelationship(models.Model):
    """
    流程模板引用关系：直接引用
    """

    ancestor_template_id = models.CharField(_("根模板ID"), max_length=32, db_index=True)
    descendant_template_id = models.CharField(_("子流程模板ID"), max_length=32, null=False, db_index=True)
    subprocess_node_id = models.CharField(_("子流程节点 ID"), max_length=32, null=False)
    version = models.CharField(_("快照字符串的md5"), max_length=32, null=False)
    always_use_latest = models.BooleanField(_("是否永远使用最新版本"), default=False)

    objects = TemplateRelationShipManager()


class TemplateCurrentVersionManager(models.Manager):
    def update_current_version(self, template):
        """
        更新某个模板的当前版本
        @param template: 模板对象
        @return: 记录模板当前版本的对象
        """
        obj, __ = self.update_or_create(
            template_id=template.template_id, defaults={"current_version": template.version}
        )
        return obj


class TemplateCurrentVersion(models.Model):
    """
    记录流程模板当前版本的表
    """

    template_id = models.CharField(_("模板ID"), max_length=32, db_index=True)
    current_version = models.CharField(_("快照字符串的md5"), max_length=32, null=False)

    objects = TemplateCurrentVersionManager()


class TemplateVersionManager(models.Manager):
    def track(self, template):
        """
        记录模板的版本号
        @param template: 被记录模板
        @return: 版本跟踪对象
        """
        if not template.snapshot:
            return None

        # don't track if latest version is same as current version
        versions = self.filter(template_id=template.id).order_by("-id")
        if versions and versions[0].md5 == template.snapshot.md5sum:
            return versions[0]

        return self.create(template=template, snapshot=template.snapshot, md5=template.snapshot.md5sum)


class TemplateVersion(models.Model):
    """
    模板版本号记录节点
    """

    template = models.ForeignKey(PipelineTemplate, verbose_name=_("模板 ID"), null=False, on_delete=models.CASCADE)
    snapshot = models.ForeignKey(Snapshot, verbose_name=_("模板数据 ID"), null=False, on_delete=models.CASCADE)
    md5 = models.CharField(_("快照字符串的md5"), max_length=32, db_index=True)
    date = models.DateTimeField(_("添加日期"), auto_now_add=True)

    objects = TemplateVersionManager()


class TemplateScheme(models.Model):
    """
    模板执行方案
    """

    template = models.ForeignKey(
        PipelineTemplate, verbose_name=_("对应模板 ID"), null=False, blank=False, on_delete=models.CASCADE
    )
    unique_id = models.CharField(_("方案唯一ID"), max_length=97, unique=True, null=False, blank=True)
    name = models.CharField(_("方案名称"), max_length=64, null=False, blank=False)
    edit_time = models.DateTimeField(_("修改时间"), auto_now=True)
    data = CompressJSONField(verbose_name=_("方案数据"))

    subprocess_scheme_relation = models.ManyToManyField(verbose_name=_("子流程节点引用执行方案的关系"), to=TemplateRelationship)


class InstanceManager(models.Manager):
    def create_instance(self, template, exec_data, spread=False, inputs=None, **kwargs):
        """
        创建流程实例对象
        @param template: 流程模板
        @param exec_data: 执行用流程数据
        @param spread: exec_data 是否已经展开
        @param kwargs: 其他参数
        @param inputs: 自定义输入
        @return: 实例对象
        """
        if not spread:
            id_maps = PipelineTemplate.objects.unfold_subprocess(exec_data)
        else:
            id_maps = PipelineTemplate.objects.replace_id(exec_data)

        inputs = inputs or {}

        for key, val in list(inputs.items()):
            if key in exec_data["data"]["inputs"]:
                exec_data["data"]["inputs"][key]["value"] = val

        instance_id = node_uniqid()
        exec_data["id"] = instance_id
        exec_snapshot = Snapshot.objects.create_snapshot(exec_data)
        TreeInfo.objects.create()
        if template is not None:
            kwargs["template"] = template
            kwargs["snapshot_id"] = template.snapshot.id
        kwargs["instance_id"] = instance_id
        kwargs["execution_snapshot_id"] = exec_snapshot.id
        return self.create(**kwargs), id_maps

    def delete_model(self, instance_ids):
        """
        删除流程实例对象
        @param instance_ids: 实例 ID 或 ID 列表
        @return:
        """
        if not isinstance(instance_ids, list):
            instance_ids = [instance_ids]
        qs = self.filter(instance_id__in=instance_ids)
        for instance in qs:
            instance.is_deleted = True
            instance.name = uniqid()
            instance.save()

    def set_started(self, instance_id, executor):
        """
        将实例的状态设置为已开始
        @param instance_id: 实例 ID
        @param executor: 执行者
        @return:
        """
        self.filter(instance_id=instance_id).update(start_time=timezone.now(), is_started=True, executor=executor)

    def set_finished(self, instance_id):
        """
        将实例的状态设置为已完成
        @param instance_id: 实例 ID
        @return:
        """
        self.filter(instance_id=instance_id).update(finish_time=timezone.now(), is_finished=True)
        post_pipeline_finish.send(sender=PipelineInstance, instance_id=instance_id)

    def set_revoked(self, instance_id):
        """
        将实例的状态设置为已撤销
        @param instance_id: 实例 ID
        @return:
        """
        self.filter(instance_id=instance_id).update(finish_time=timezone.now(), is_revoked=True)
        post_pipeline_revoke.send(sender=PipelineInstance, instance_id=instance_id)


class PipelineInstance(models.Model):
    """
    流程实例对象
    """

    instance_id = models.CharField(_("实例ID"), max_length=32, unique=True, db_index=True)
    template = models.ForeignKey(
        PipelineTemplate, verbose_name=_("Pipeline模板"), null=True, blank=True, on_delete=models.SET_NULL
    )
    name = models.CharField(_("实例名称"), max_length=MAX_LEN_OF_NAME, default="default_instance")
    creator = models.CharField(_("创建者"), max_length=32, blank=True)
    create_time = models.DateTimeField(_("创建时间"), auto_now_add=True, db_index=True)
    executor = models.CharField(_("执行者"), max_length=32, blank=True)
    start_time = models.DateTimeField(_("启动时间"), null=True, blank=True)
    finish_time = models.DateTimeField(_("结束时间"), null=True, blank=True)
    description = models.TextField(_("描述"), blank=True)
    is_started = models.BooleanField(_("是否已经启动"), default=False)
    is_finished = models.BooleanField(_("是否已经完成"), default=False)
    is_revoked = models.BooleanField(_("是否已经撤销"), default=False)
    is_deleted = models.BooleanField(_("是否已经删除"), default=False, help_text=_("表示当前实例是否删除"))
    is_expired = models.BooleanField(_("是否已经过期"), default=False, help_text=_("运行时被定期清理即为过期"))
    snapshot = models.ForeignKey(
        Snapshot,
        blank=True,
        null=True,
        related_name="snapshot_instances",
        verbose_name=_("实例结构数据，指向实例对应的模板的结构数据"),
        on_delete=models.SET_NULL,
    )
    execution_snapshot = models.ForeignKey(
        Snapshot,
        blank=True,
        null=True,
        related_name="execution_snapshot_instances",
        verbose_name=_("用于实例执行的结构数据"),
        on_delete=models.SET_NULL,
    )
    tree_info = models.ForeignKey(
        TreeInfo,
        blank=True,
        null=True,
        related_name="tree_info_instances",
        verbose_name=_("提前计算好的一些流程结构数据"),
        on_delete=models.SET_NULL,
    )

    objects = InstanceManager()

    class Meta:
        verbose_name = _("Pipeline实例")
        verbose_name_plural = _("Pipeline实例")
        ordering = ["-create_time"]
        app_label = "pipeline"

    def __unicode__(self):
        return "{}-{}".format(self.instance_id, self.name)

    @property
    def data(self):
        return self.snapshot.data

    @property
    def execution_data(self):
        return self.execution_snapshot.data

    @property
    def node_id_set(self):
        if not self.tree_info:
            self.calculate_tree_info(save=True)
        return set(self.tree_info.data["node_id_set"])

    @property
    def elapsed_time(self):
        return calculate_elapsed_time(self.start_time, self.finish_time)

    def set_execution_data(self, data):
        """
        设置实例的执行用流程数据
        @param data: 执行用流程数据
        @return:
        """
        self.execution_snapshot.data = data
        self.execution_snapshot.save()

    def _replace_id(self, exec_data):
        """
        替换执行用流程数据中的所有 ID
        @param exec_data: 执行用流程数据
        @return:
        """
        replace_all_id(exec_data)
        activities = exec_data[PE.activities]
        for act_id, act in list(activities.items()):
            if act[PE.type] == PE.SubProcess:
                self._replace_id(act["pipeline"])
                act["pipeline"]["id"] = act_id

    def clone(self, creator, **kwargs):
        """
        返回当前实例对象的克隆
        @param creator: 创建者
        @param kwargs: 其他参数
        @return: 当前实例对象的克隆
        """
        name = kwargs.get("name") or timezone.localtime(timezone.now()).strftime("clone%Y%m%d%H%m%S")
        instance_id = node_uniqid()

        exec_data = self.execution_data
        self._replace_id(exec_data)
        # replace root id
        exec_data["id"] = instance_id
        new_snapshot = Snapshot.objects.create_snapshot(exec_data)

        return self.__class__.objects.create(
            template=self.template,
            instance_id=instance_id,
            name=name,
            creator=creator,
            description=self.description,
            snapshot=self.snapshot,
            execution_snapshot=new_snapshot,
        )

    def start(self, executor, check_workers=True, priority=PIPELINE_DEFAULT_PRIORITY, queue=""):
        """
        启动当前流程
        @param executor: 执行者
        @param check_workers: 是否检测 worker 的状态
        @return: 执行结果
        """

        with transaction.atomic():
            instance = self.__class__.objects.select_for_update().get(id=self.id)
            if instance.is_started:
                return ActionResult(result=False, message="pipeline instance already started.")

            pipeline_data = instance.execution_data

            try:
                parser_cls = import_string(settings.PIPELINE_PARSER_CLASS)
            except ImportError:
                return ActionResult(result=False, message="invalid parser class: %s" % settings.PIPELINE_PARSER_CLASS)

            instance.start_time = timezone.now()
            instance.is_started = True
            instance.executor = executor

            parser = parser_cls(pipeline_data)
            pipeline = parser.parse(
                root_pipeline_data=get_pipeline_context(
                    instance, obj_type="instance", data_type="data", username=executor
                ),
                root_pipeline_context=get_pipeline_context(
                    instance, obj_type="instance", data_type="context", username=executor
                ),
            )

            # calculate tree info
            instance.calculate_tree_info()

            instance.save()

        act_result = task_service.run_pipeline(pipeline, check_workers=check_workers, priority=priority, queue=queue)

        if not act_result.result:
            with transaction.atomic():
                instance = self.__class__.objects.select_for_update().get(id=self.id)
                instance.start_time = None
                instance.is_started = False
                instance.executor = ""
                instance.save()

        return act_result

    def _get_node_id_set(self, node_id_set, data):
        """
        递归获取当前实例中所有节点的 ID（包括子流程中的节点）
        @param node_id_set: 节点 ID 集合
        @param data: 流程数据
        @return:
        """
        node_id_set.add(data[PE.start_event]["id"])
        node_id_set.add(data[PE.end_event]["id"])
        for gid in data[PE.gateways]:
            node_id_set.add(gid)
        for aid, act_data in list(data[PE.activities].items()):
            node_id_set.add(aid)
            if act_data[PE.type] == PE.SubProcess:
                self._get_node_id_set(node_id_set, act_data["pipeline"])

    def calculate_tree_info(self, save=False):
        """
        计算当前流程实例执行用流程数据中的一些基本信息
        @param save: 是否在计算完后保存实例对象
        @return:
        """
        self.tree_info = TreeInfo.objects.create()
        node_id_set = set({})

        # get node id set
        self._get_node_id_set(node_id_set, self.execution_data)

        tree_info = {"node_id_set": list(node_id_set)}
        self.tree_info.data = tree_info
        self.tree_info.save()

        if save:
            self.save()
