from django.db import models
from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.forms.models import modelform_factory
import copy
from xadmin.sites import site
from xadmin.util import get_model_from_relation, vendor
from xadmin.views import BaseAdminPlugin, ModelFormAdminView
from xadmin.layout import Layout


class QuickFormPlugin(BaseAdminPlugin):

    def init_request(self, *args, **kwargs):
        if self.request.method == 'GET' and self.request.is_ajax() or self.request.GET.get('_ajax'):
            self.admin_view.add_form_template = 'xadmin/views/quick_form.html'
            self.admin_view.change_form_template = 'xadmin/views/quick_form.html'
            return True
        return False

    def get_model_form(self, __, **kwargs):
        if '_field' in self.request.GET:
            defaults = {
                "form": self.admin_view.form,
                "fields": self.request.GET['_field'].split(','),
                "formfield_callback": self.admin_view.formfield_for_dbfield,
            }
            return modelform_factory(self.model, **defaults)
        return __()

    def get_form_layout(self, __):
        if '_field' in self.request.GET:
            return Layout(*self.request.GET['_field'].split(','))
        return __()

    def get_context(self, context):
        context['form_url'] = self.request.path
        return context


class RelatedFieldWidgetWrapper(forms.Widget):
    """
    This class is a wrapper to a given widget to add the add icon for the
    admin interface.
    """

    def __init__(self, widget, rel, add_url, rel_add_url):
        self.needs_multipart_form = widget.needs_multipart_form
        self.attrs = widget.attrs
        self.choices = widget.choices
        self.is_required = widget.is_required
        self.widget = widget
        self.rel = rel

        self.add_url = add_url
        self.rel_add_url = rel_add_url

        if hasattr(self, 'input_type'):
            self.input_type = widget.input_type

    def __deepcopy__(self, memo):
        obj = copy.copy(self)
        obj.widget = copy.deepcopy(self.widget, memo)
        obj.attrs = self.widget.attrs
        memo[id(self)] = obj
        return obj

    @property
    def media(self):
        media = self.widget.media + vendor('xadmin.plugin.quick-form.js')
        return media

    def render(self, name, value, renderer=None, *args, **kwargs):
        self.widget.choices = self.choices
        output = []
        if self.add_url:
            output.append(u'<a href="%s" title="%s" class="btn btn-primary btn-sm btn-ajax pull-right" data-for-id="id_%s" data-refresh-url="%s"><i class="fa fa-plus"></i></a>'
                          % (
                              self.add_url, (_('Create New %s') % self.rel.model._meta.verbose_name), name,
                              "%s?_field=%s&%s=" % (self.rel_add_url, name, name)))
        output.extend(['<div class="control-wrap" id="id_%s_wrap_container">' % name,
                       self.widget.render(name, value, *args, **kwargs), '</div>'])
        return mark_safe(u''.join(output))

    def build_attrs(self, extra_attrs=None, **kwargs):
        "Helper function for building an attribute dictionary."
        self.attrs = self.widget.build_attrs(extra_attrs=None, **kwargs)
        return self.attrs

    def value_from_datadict(self, data, files, name):
        return self.widget.value_from_datadict(data, files, name)

    def id_for_label(self, id_):
        return self.widget.id_for_label(id_)


class QuickAddBtnPlugin(BaseAdminPlugin):

    def formfield_for_dbfield(self, formfield, db_field, **kwargs):
        if formfield and self.model in self.admin_site._registry and isinstance(db_field, (models.ForeignKey, models.ManyToManyField)):
            rel_model = get_model_from_relation(db_field)
            if rel_model in self.admin_site._registry and self.has_model_perm(rel_model, 'add'):
                add_url = self.get_model_url(rel_model, 'add')
                formfield.widget = RelatedFieldWidgetWrapper(
                    formfield.widget, db_field.remote_field, add_url, self.get_model_url(self.model, 'add'))
        return formfield

site.register_plugin(QuickFormPlugin, ModelFormAdminView)
site.register_plugin(QuickAddBtnPlugin, ModelFormAdminView)
