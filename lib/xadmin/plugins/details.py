

from django.utils.translation import ugettext as _
from django.urls.base import reverse, NoReverseMatch
from django.db import models

from xadmin.sites import site
from xadmin.views import BaseAdminPlugin, ListAdminView


class DetailsPlugin(BaseAdminPlugin):

    show_detail_fields = []
    show_all_rel_details = True

    def result_item(self, item, obj, field_name, row):
        if (self.show_all_rel_details or (field_name in self.show_detail_fields)):
            rel_obj = None
            if hasattr(item.field, 'remote_field') and isinstance(item.field.remote_field, models.ManyToOneRel):
                rel_obj = getattr(obj, field_name)
            elif field_name in self.show_detail_fields:
                rel_obj = obj

            if rel_obj:
                if rel_obj.__class__ in site._registry:
                    try:
                        model_admin = site._registry[rel_obj.__class__]
                        has_view_perm = model_admin(self.admin_view.request).has_view_permission(rel_obj)
                        has_change_perm = model_admin(self.admin_view.request).has_change_permission(rel_obj)
                    except:
                        has_view_perm = self.admin_view.has_model_perm(rel_obj.__class__, 'view')
                        has_change_perm = self.has_model_perm(rel_obj.__class__, 'change')
                else:
                    has_view_perm = self.admin_view.has_model_perm(rel_obj.__class__, 'view')
                    has_change_perm = self.has_model_perm(rel_obj.__class__, 'change')

            if rel_obj and has_view_perm:
                opts = rel_obj._meta
                try:
                    item_res_uri = reverse(
                        '%s:%s_%s_detail' % (self.admin_site.app_name,
                                             opts.app_label, opts.model_name),
                        args=(getattr(rel_obj, opts.pk.attname),))
                    if item_res_uri:
                        if has_change_perm:
                            edit_url = reverse(
                                '%s:%s_%s_change' % (self.admin_site.app_name, opts.app_label, opts.model_name),
                                args=(getattr(rel_obj, opts.pk.attname),))
                        else:
                            edit_url = ''
                        item.btns.append('<a data-res-uri="%s" data-edit-uri="%s" class="details-handler" rel="tooltip" title="%s"><i class="fa fa-info-circle"></i></a>'
                                         % (item_res_uri, edit_url, _(u'Details of %s') % str(rel_obj)))
                except NoReverseMatch:
                    pass
        return item

    # Media
    def get_media(self, media):
        if self.show_all_rel_details or self.show_detail_fields:
            media = media + self.vendor('xadmin.plugin.details.js', 'xadmin.form.css')
        return media

site.register_plugin(DetailsPlugin, ListAdminView)
