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

from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from pipeline.core.constants import PE
from pipeline.core.pipeline import Pipeline
from pipeline.engine.signals import pipeline_end, pipeline_revoke
from pipeline.models import (
    PipelineInstance,
    PipelineTemplate,
    TemplateCurrentVersion,
    TemplateRelationship,
    TemplateVersion,
)


@receiver(pre_save, sender=PipelineTemplate)
def pipeline_template_pre_save_handler(sender, instance, **kwargs):
    template = instance

    if template.is_deleted:
        return

    template.set_has_subprocess_bit()


@receiver(post_save, sender=PipelineTemplate)
def pipeline_template_post_save_handler(sender, instance, created, **kwargs):
    template = instance

    if template.is_deleted:
        TemplateRelationship.objects.filter(ancestor_template_id=template.template_id).delete()
        return

    with transaction.atomic():
        TemplateRelationship.objects.filter(ancestor_template_id=template.template_id).delete()
        acts = list(template.data[PE.activities].values())
        subprocess_nodes = [act for act in acts if act["type"] == PE.SubProcess]
        rs = []
        template_scheme_dict = {}
        for sp in subprocess_nodes:
            version = sp.get("version") or PipelineTemplate.objects.get(template_id=sp["template_id"]).version
            always_use_latest = sp.get("always_use_latest", False)

            template_scheme_dict.update({
                sp["template_id"]: sp.get("scheme_id_list", [])
            })

            rs.append(
                TemplateRelationship(
                    ancestor_template_id=template.template_id,
                    descendant_template_id=sp["template_id"],
                    subprocess_node_id=sp["id"],
                    version=version,
                    always_use_latest=always_use_latest
                )
            )
        if rs:
            TemplateRelationship.objects.bulk_create(rs)

            relation_queryset = TemplateRelationship.objects.filter(ancestor_template_id=template.template_id)
            for relation in relation_queryset:
                scheme_id_list = template_scheme_dict[relation.descendant_template_id]
                relation.templatescheme_set.add(*scheme_id_list)

        TemplateVersion.objects.track(template)
        TemplateCurrentVersion.objects.update_current_version(template)


@receiver(pipeline_end, sender=Pipeline)
def pipeline_end_handler(sender, root_pipeline_id, **kwargs):
    try:
        PipelineInstance.objects.set_finished(root_pipeline_id)
    except PipelineInstance.DoesNotExist:  # task which do not belong to any instance
        pass


@receiver(pipeline_revoke, sender=Pipeline)
def pipeline_revoke_handler(sender, root_pipeline_id, **kwargs):
    try:
        PipelineInstance.objects.set_revoked(root_pipeline_id)
    except PipelineInstance.DoesNotExist:  # task which do not belong to any instance
        pass
