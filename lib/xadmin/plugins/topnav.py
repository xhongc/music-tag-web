
from django.template import loader
from django.utils.text import capfirst
from django.urls.base import reverse, NoReverseMatch
from django.utils.translation import ugettext as _

from xadmin.sites import site
from xadmin.filters import SEARCH_VAR
from xadmin.views import BaseAdminPlugin, CommAdminView


class TopNavPlugin(BaseAdminPlugin):

    global_search_models = None
    global_add_models = None

    def get_context(self, context):
        return context

    # Block Views
    def block_top_navbar(self, context, nodes):
        search_models = []

        site_name = self.admin_site.name
        if self.global_search_models == None:
            models = self.admin_site._registry.keys()
        else:
            models = self.global_search_models

        for model in models:
            app_label = model._meta.app_label

            if self.has_model_perm(model, "view"):
                info = (app_label, model._meta.model_name)
                if getattr(self.admin_site._registry[model], 'search_fields', None):
                    try:
                        search_models.append({
                            'title': _('Search %s') % capfirst(model._meta.verbose_name_plural),
                            'url': reverse('xadmin:%s_%s_changelist' % info, current_app=site_name),
                            'model': model
                        })
                    except NoReverseMatch:
                        pass
        return nodes.append(loader.render_to_string('xadmin/blocks/comm.top.topnav.html', {'search_models': search_models, 'search_name': SEARCH_VAR}))

    def block_top_navmenu(self, context, nodes):
        add_models = []

        site_name = self.admin_site.name

        if self.global_add_models == None:
            models = self.admin_site._registry.keys()
        else:
            models = self.global_add_models
        for model in models:
            app_label = model._meta.app_label

            if self.has_model_perm(model, "add"):
                info = (app_label, model._meta.model_name)
                try:
                    add_models.append({
                        'title': _('Add %s') % capfirst(model._meta.verbose_name),
                        'url': reverse('xadmin:%s_%s_add' % info, current_app=site_name),
                        'model': model
                    })
                except NoReverseMatch:
                    pass

        nodes.append(
            loader.render_to_string('xadmin/blocks/comm.top.topnav.html', {'add_models': add_models}))


site.register_plugin(TopNavPlugin, CommAdminView)
