#coding:utf-8
from xadmin.sites import site
from xadmin.models import UserSettings
from xadmin.views import BaseAdminPlugin, ModelFormAdminView, DetailAdminView
from xadmin.layout import Fieldset, Column


class BasePortalPlugin(BaseAdminPlugin):

    # Media
    def get_media(self, media):
        return media + self.vendor('xadmin.plugin.portal.js')


def get_layout_objects(layout, clz, objects):
    for i, layout_object in enumerate(layout.fields):
        if layout_object.__class__ is clz or issubclass(layout_object.__class__, clz):
            objects.append(layout_object)
        elif hasattr(layout_object, 'get_field_names'):
            get_layout_objects(layout_object, clz, objects)


class ModelFormPlugin(BasePortalPlugin):

    def _portal_key(self):
        return '%s_%s_editform_portal' % (self.opts.app_label, self.opts.model_name)

    def get_form_helper(self, helper):
        cs = []
        layout = helper.layout
        get_layout_objects(layout, Column, cs)
        for i, c in enumerate(cs):
            if not getattr(c, 'css_id', None):
                c.css_id = 'column-%d' % i

        # make fieldset index
        fs = []
        get_layout_objects(layout, Fieldset, fs)
        fs_map = {}
        for i, f in enumerate(fs):
            if not getattr(f, 'css_id', None):
                f.css_id = 'box-%d' % i
            fs_map[f.css_id] = f

        try:
            layout_pos = UserSettings.objects.get(
                user=self.user, key=self._portal_key()).value
            layout_cs = layout_pos.split('|')
            for i, c in enumerate(cs):
                c.fields = [fs_map.pop(j) for j in layout_cs[i].split(
                    ',') if j in fs_map] if len(layout_cs) > i else []
            if fs_map and cs:
                cs[0].fields.extend(fs_map.values())
        except Exception:
            pass

        return helper

    def block_form_top(self, context, node):
        # put portal key and submit url to page
        return "<input type='hidden' id='_portal_key' value='%s' />" % self._portal_key()


class ModelDetailPlugin(ModelFormPlugin):

    def _portal_key(self):
        return '%s_%s_detail_portal' % (self.opts.app_label, self.opts.model_name)

    def block_after_fieldsets(self, context, node):
        # put portal key and submit url to page
        return "<input type='hidden' id='_portal_key' value='%s' />" % self._portal_key()

site.register_plugin(ModelFormPlugin, ModelFormAdminView)
site.register_plugin(ModelDetailPlugin, DetailAdminView)
