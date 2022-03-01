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


from django.db import migrations
from django.db.models.signals import post_save


def reverse_func(apps, schema_editor):
    pass


def forward_func(apps, schema_editor):
    PipelineTemplate = apps.get_model("pipeline", "PipelineTemplate")
    TemplateRelationship = apps.get_model("pipeline", "TemplateRelationship")
    TemplateVersion = apps.get_model("pipeline", "TemplateVersion")
    TemplateCurrentVersion = apps.get_model("pipeline", "TemplateCurrentVersion")
    db_alias = schema_editor.connection.alias
    template_list = PipelineTemplate.objects.using(db_alias).filter(is_deleted=False)

    for template in template_list:
        TemplateRelationship.objects.using(db_alias).filter(ancestor_template_id=template.template_id).delete()
        acts = list(template.snapshot.data["activities"].values())
        subprocess_nodes = [act for act in acts if act["type"] == "SubProcess"]
        rs = []
        for sp in subprocess_nodes:
            version = (
                sp.get("version")
                or PipelineTemplate.objects.using(db_alias).get(template_id=sp["template_id"]).snapshot.md5sum
            )
            rs.append(
                TemplateRelationship(
                    ancestor_template_id=template.template_id,
                    descendant_template_id=sp["template_id"],
                    subprocess_node_id=sp["id"][:32],
                    version=version,
                )
            )
        TemplateRelationship.objects.bulk_create(rs)

        versions = TemplateVersion.objects.using(db_alias).filter(template_id=template.id).order_by("-id")
        if not (versions and versions[0].md5 == template.snapshot.md5sum):
            TemplateVersion.objects.create(template=template, snapshot=template.snapshot, md5=template.snapshot.md5sum)
        TemplateCurrentVersion.objects.update_or_create(
            template_id=template.template_id, defaults={"current_version": template.snapshot.md5sum}
        )


class Migration(migrations.Migration):
    dependencies = [
        ("pipeline", "0012_templatecurrentversion"),
    ]

    operations = [migrations.RunPython(forward_func, reverse_func)]
