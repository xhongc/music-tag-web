from __future__ import absolute_import
import copy

from crispy_forms.utils import TEMPLATE_PACK
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.db import models
from django.forms.models import modelform_factory
from django.http import Http404
from django.template import loader
from django.template.response import TemplateResponse
from django.utils import six
from django.utils.encoding import force_text, smart_text
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.utils.html import conditional_escape
from xadmin.layout import FormHelper, Layout, Fieldset, Container, Column, Field, Col, TabHolder
from xadmin.util import unquote, lookup_field, display_for_field, boolean_icon, label_for_field

from .base import ModelAdminView, filter_hook, csrf_protect_m

# Text to display within change-list table cells if the value is blank.
EMPTY_CHANGELIST_VALUE = _('Null')


class ShowField(Field):
    template = "xadmin/layout/field_value.html"

    def __init__(self, callback, *args, **kwargs):
        super(ShowField, self).__init__(*args, **kwargs)
        self.results = [(field, callback(field)) for field in self.fields]

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, extra_context=None, **kwargs):
        super(ShowField, self).render(form, form_style, context, template_pack, extra_context, **kwargs)
        if extra_context is None:
            extra_context = {}
        if hasattr(self, 'wrapper_class'):
            extra_context['wrapper_class'] = self.wrapper_class

        if self.attrs:
            if 'detail-class' in self.attrs:
                extra_context['input_class'] = self.attrs['detail-class']
            elif 'class' in self.attrs:
                extra_context['input_class'] = self.attrs['class']

        html = ''
        for field, result in self.results:
            extra_context['result'] = result
            if field in form.fields:
                if form.fields[field].widget != forms.HiddenInput:
                    extra_context['field'] = form[field]
                    html += loader.render_to_string(self.template, extra_context)
            else:
                extra_context['field'] = field
                html += loader.render_to_string(self.template, extra_context)
        return html


class ResultField(object):

    def __init__(self, obj, field_name, admin_view=None):
        self.text = '&nbsp;'
        self.wraps = []
        self.allow_tags = False
        self.obj = obj
        self.admin_view = admin_view
        self.field_name = field_name
        self.field = None
        self.attr = None
        self.label = None
        self.value = None

        self.init()

    def init(self):
        self.label = label_for_field(self.field_name, self.obj.__class__,
                                     model_admin=self.admin_view,
                                     return_attr=False
                                     )
        try:
            f, attr, value = lookup_field(
                self.field_name, self.obj, self.admin_view)
        except (AttributeError, ObjectDoesNotExist):
            self.text
        else:
            if f is None:
                self.allow_tags = getattr(attr, 'allow_tags', False)
                boolean = getattr(attr, 'boolean', False)
                if boolean:
                    self.allow_tags = True
                    self.text = boolean_icon(value)
                else:
                    self.text = smart_text(value)
            else:
                if isinstance(f.remote_field, models.ManyToOneRel):
                    self.text = getattr(self.obj, f.name)
                else:
                    self.text = display_for_field(value, f)
            self.field = f
            self.attr = attr
            self.value = value

    @property
    def val(self):
        text = mark_safe(
            self.text) if self.allow_tags else conditional_escape(self.text)
        if force_text(text) == '' or text == 'None' or text == EMPTY_CHANGELIST_VALUE:
            text = mark_safe(
                '<span class="text-muted">%s</span>' % EMPTY_CHANGELIST_VALUE)
        for wrap in self.wraps:
            text = mark_safe(wrap % text)
        return text


def replace_field_to_value(layout, cb):
    cls_str = str if six.PY3 else basestring
    for i, lo in enumerate(layout.fields):
        if isinstance(lo, Field) or issubclass(lo.__class__, Field):
            layout.fields[i] = ShowField(
                cb, *lo.fields, attrs=lo.attrs, wrapper_class=lo.wrapper_class)
        elif isinstance(lo, cls_str):
            layout.fields[i] = ShowField(cb, lo)
        elif hasattr(lo, 'get_field_names'):
            replace_field_to_value(lo, cb)


class DetailAdminView(ModelAdminView):

    form = forms.ModelForm
    detail_layout = None
    detail_show_all = True
    detail_template = None
    form_layout = None

    def init_request(self, object_id, *args, **kwargs):
        self.obj = self.get_object(unquote(object_id))

        if not self.has_view_permission(self.obj):
            raise PermissionDenied

        if self.obj is None:
            raise Http404(
                _('%(name)s object with primary key %(key)r does not exist.') %
                {'name': force_text(self.opts.verbose_name), 'key': escape(object_id)})
        self.org_obj = self.obj

    @filter_hook
    def get_form_layout(self):
        layout = copy.deepcopy(self.detail_layout or self.form_layout)

        if layout is None:
            layout = Layout(Container(Col('full',
                                          Fieldset(
                                              "", *self.form_obj.fields.keys(),
                                              css_class="unsort no_title"), horizontal=True, span=12)
                                      ))
        elif type(layout) in (list, tuple) and len(layout) > 0:
            if isinstance(layout[0], Column):
                fs = layout
            elif isinstance(layout[0], (Fieldset, TabHolder)):
                fs = (Col('full', *layout, horizontal=True, span=12),)
            else:
                fs = (
                    Col('full', Fieldset("", *layout, css_class="unsort no_title"), horizontal=True, span=12),)

            layout = Layout(Container(*fs))

            if self.detail_show_all:
                rendered_fields = [i[1] for i in layout.get_field_names()]
                container = layout[0].fields
                other_fieldset = Fieldset(_(u'Other Fields'), *[
                                          f for f in self.form_obj.fields.keys() if f not in rendered_fields])

                if len(other_fieldset.fields):
                    if len(container) and isinstance(container[0], Column):
                        container[0].fields.append(other_fieldset)
                    else:
                        container.append(other_fieldset)

        return layout

    @filter_hook
    def get_model_form(self, **kwargs):
        """
        Returns a Form class for use in the admin add view. This is used by
        add_view and change_view.
        """
        if self.exclude is None:
            exclude = []
        else:
            exclude = list(self.exclude)
        if self.exclude is None and hasattr(self.form, '_meta') and self.form._meta.exclude:
            # Take the custom ModelForm's Meta.exclude into account only if the
            # ModelAdmin doesn't define its own.
            exclude.extend(self.form._meta.exclude)
        # if exclude is an empty list we pass None to be consistant with the
        # default on modelform_factory
        exclude = exclude or None
        defaults = {
            "form": self.form,
            "fields": self.fields and list(self.fields) or '__all__',
            "exclude": exclude,
        }
        defaults.update(kwargs)
        return modelform_factory(self.model, **defaults)

    @filter_hook
    def get_form_helper(self):
        helper = FormHelper()
        helper.form_tag = False
        helper.include_media = False
        layout = self.get_form_layout()
        replace_field_to_value(layout, self.get_field_result)
        helper.add_layout(layout)
        cls_str = str if six.PY3 else basestring
        helper.filter(cls_str, max_level=20).wrap(ShowField, admin_view=self)
        return helper

    @csrf_protect_m
    @filter_hook
    def get(self, request, *args, **kwargs):
        form = self.get_model_form()
        self.form_obj = form(instance=self.obj)
        helper = self.get_form_helper()
        if helper:
            self.form_obj.helper = helper

        return self.get_response()

    @filter_hook
    def get_context(self):
        new_context = {
            'title': _('%s Detail') % force_text(self.opts.verbose_name),
            'form': self.form_obj,

            'object': self.obj,

            'has_change_permission': self.has_change_permission(self.obj),
            'has_delete_permission': self.has_delete_permission(self.obj),

            'content_type_id': ContentType.objects.get_for_model(self.model).id,
        }

        context = super(DetailAdminView, self).get_context()
        context.update(new_context)
        return context

    @filter_hook
    def get_breadcrumb(self):
        bcs = super(DetailAdminView, self).get_breadcrumb()
        item = {'title': force_text(self.obj)}
        if self.has_view_permission():
            item['url'] = self.model_admin_url('detail', self.obj.pk)
        bcs.append(item)
        return bcs

    @filter_hook
    def get_media(self):
        return super(DetailAdminView, self).get_media() + self.form_obj.media + \
            self.vendor('xadmin.page.form.js', 'xadmin.form.css')

    @filter_hook
    def get_field_result(self, field_name):
        return ResultField(self.obj, field_name, self)

    @filter_hook
    def get_response(self, *args, **kwargs):
        context = self.get_context()
        context.update(kwargs or {})
        self.request.current_app = self.admin_site.name
        response = TemplateResponse(self.request, self.detail_template or
                                    self.get_template_list('views/model_detail.html'),
                                    context)
        return response


class DetailAdminUtil(DetailAdminView):

    def init_request(self, obj):
        self.obj = obj
        self.org_obj = obj
