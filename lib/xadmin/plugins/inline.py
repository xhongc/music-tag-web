import copy
import inspect
from django import forms
from django.forms.formsets import all_valid, DELETION_FIELD_NAME
from django.forms.models import inlineformset_factory, BaseInlineFormSet, modelform_defines_fields
from django.contrib.contenttypes.forms import BaseGenericInlineFormSet, generic_inlineformset_factory
from django.template import loader
from django.template.loader import render_to_string
from django.contrib.auth import get_permission_codename
from django.utils import six
from django.utils.encoding import smart_text
from crispy_forms.utils import TEMPLATE_PACK

from xadmin.layout import FormHelper, Layout, flatatt, Container, Column, Field, Fieldset
from xadmin.plugins.utils import get_context_dict
from xadmin.sites import site
from xadmin.views import BaseAdminPlugin, ModelFormAdminView, DetailAdminView, filter_hook


class ShowField(Field):
    template = "xadmin/layout/field_value.html"

    def __init__(self, admin_view, *args, **kwargs):
        super(ShowField, self).__init__(*args, **kwargs)
        self.admin_view = admin_view
        if admin_view.style == 'table':
            self.template = "xadmin/layout/field_value_td.html"

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        html = ''
        detail = form.detail
        for field in self.fields:
            if not isinstance(form.fields[field].widget, forms.HiddenInput):
                result = detail.get_field_result(field)
                html += loader.render_to_string(
                    self.template, context={'field': form[field], 'result': result})
        return html


class DeleteField(Field):

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        if form.instance.pk:
            self.attrs['type'] = 'hidden'
            return super(DeleteField, self).render(form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs)
        else:
            return ""


class TDField(Field):
    template = "xadmin/layout/td-field.html"


class InlineStyleManager(object):
    inline_styles = {}

    def register_style(self, name, style):
        self.inline_styles[name] = style

    def get_style(self, name='stacked'):
        return self.inline_styles.get(name)

style_manager = InlineStyleManager()


class InlineStyle(object):
    template = 'xadmin/edit_inline/stacked.html'

    def __init__(self, view, formset):
        self.view = view
        self.formset = formset

    def update_layout(self, helper):
        pass

    def get_attrs(self):
        return {}
style_manager.register_style('stacked', InlineStyle)


class OneInlineStyle(InlineStyle):
    template = 'xadmin/edit_inline/one.html'
style_manager.register_style("one", OneInlineStyle)


class AccInlineStyle(InlineStyle):
    template = 'xadmin/edit_inline/accordion.html'
style_manager.register_style("accordion", AccInlineStyle)


class TabInlineStyle(InlineStyle):
    template = 'xadmin/edit_inline/tab.html'
style_manager.register_style("tab", TabInlineStyle)


class TableInlineStyle(InlineStyle):
    template = 'xadmin/edit_inline/tabular.html'

    def update_layout(self, helper):
        helper.add_layout(
            Layout(*[TDField(f) for f in self.formset[0].fields.keys()]))

    def get_attrs(self):
        fields = []
        readonly_fields = []
        if len(self.formset):
            fields = [f for k, f in self.formset[0].fields.items() if k != DELETION_FIELD_NAME]
            readonly_fields = [f for f in getattr(self.formset[0], 'readonly_fields', [])]
        return {
            'fields': fields,
            'readonly_fields': readonly_fields
        }
style_manager.register_style("table", TableInlineStyle)


def replace_field_to_value(layout, av):
    if layout:
        cls_str = str if six.PY3 else basestring
        for i, lo in enumerate(layout.fields):
            if isinstance(lo, Field) or issubclass(lo.__class__, Field):
                layout.fields[i] = ShowField(av, *lo.fields, **lo.attrs)
            elif isinstance(lo, cls_str):
                layout.fields[i] = ShowField(av, lo)
            elif hasattr(lo, 'get_field_names'):
                replace_field_to_value(lo, av)


class InlineModelAdmin(ModelFormAdminView):

    fk_name = None
    formset = BaseInlineFormSet
    extra = 3
    max_num = None
    can_delete = True
    fields = []
    admin_view = None
    style = 'stacked'

    def init(self, admin_view):
        self.admin_view = admin_view
        self.parent_model = admin_view.model
        self.org_obj = getattr(admin_view, 'org_obj', None)
        self.model_instance = self.org_obj or admin_view.model()

        return self

    @filter_hook
    def get_formset(self, **kwargs):
        """Returns a BaseInlineFormSet class for use in admin add/change views."""
        if self.exclude is None:
            exclude = []
        else:
            exclude = list(self.exclude)
        exclude.extend(self.get_readonly_fields())
        if self.exclude is None and hasattr(self.form, '_meta') and self.form._meta.exclude:
            # Take the custom ModelForm's Meta.exclude into account only if the
            # InlineModelAdmin doesn't define its own.
            exclude.extend(self.form._meta.exclude)
        # if exclude is an empty list we use None, since that's the actual
        # default
        exclude = exclude or None
        can_delete = self.can_delete and self.has_delete_permission()
        defaults = {
            "form": self.form,
            "formset": self.formset,
            "fk_name": self.fk_name,
            'fields': forms.ALL_FIELDS,
            "exclude": exclude,
            "formfield_callback": self.formfield_for_dbfield,
            "extra": self.extra,
            "max_num": self.max_num,
            "can_delete": can_delete,
        }
        defaults.update(kwargs)

        return inlineformset_factory(self.parent_model, self.model, **defaults)

    @filter_hook
    def instance_form(self, **kwargs):
        formset = self.get_formset(**kwargs)
        attrs = {
            'instance': self.model_instance,
            'queryset': self.queryset()
        }
        if self.request_method == 'post':
            attrs.update({
                'data': self.request.POST, 'files': self.request.FILES,
                'save_as_new': "_saveasnew" in self.request.POST
            })
        instance = formset(**attrs)
        instance.view = self

        helper = FormHelper()
        helper.form_tag = False
        helper.include_media = False
        # override form method to prevent render csrf_token in inline forms, see template 'bootstrap/whole_uni_form.html'
        helper.form_method = 'get'

        style = style_manager.get_style(
            'one' if self.max_num == 1 else self.style)(self, instance)
        style.name = self.style

        if len(instance):
            layout = copy.deepcopy(self.form_layout)

            if layout is None:
                layout = Layout(*instance[0].fields.keys())
            elif type(layout) in (list, tuple) and len(layout) > 0:
                layout = Layout(*layout)

                rendered_fields = [i[1] for i in layout.get_field_names()]
                layout.extend([f for f in instance[0]
                               .fields.keys() if f not in rendered_fields])

            helper.add_layout(layout)
            style.update_layout(helper)

            # replace delete field with Dynamic field, for hidden delete field when instance is NEW.
            helper[DELETION_FIELD_NAME].wrap(DeleteField)

        instance.helper = helper
        instance.style = style

        readonly_fields = self.get_readonly_fields()
        if readonly_fields:
            for form in instance:
                form.readonly_fields = []
                inst = form.save(commit=False)
                if inst:
                    meta_field_names = [field.name for field in inst._meta.get_fields()]
                    for readonly_field in readonly_fields:
                        value = None
                        label = None
                        if readonly_field in meta_field_names:
                            label = inst._meta.get_field(readonly_field).verbose_name
                            value = smart_text(getattr(inst, readonly_field))
                        elif inspect.ismethod(getattr(inst, readonly_field, None)):
                            value = getattr(inst, readonly_field)()
                            label = getattr(getattr(inst, readonly_field), 'short_description', readonly_field)
                        elif inspect.ismethod(getattr(self, readonly_field, None)):
                            value = getattr(self, readonly_field)(inst)
                            label = getattr(getattr(self, readonly_field), 'short_description', readonly_field)
                        if value:
                            form.readonly_fields.append({'label': label, 'contents': value})
        return instance

    def has_auto_field(self, form):
        if form._meta.model._meta.has_auto_field:
            return True
        for parent in form._meta.model._meta.get_parent_list():
            if parent._meta.has_auto_field:
                return True
        return False

    def queryset(self):
        queryset = super(InlineModelAdmin, self).queryset()
        if not self.has_change_permission() and not self.has_view_permission():
            queryset = queryset.none()
        return queryset

    def has_add_permission(self):
        if self.opts.auto_created:
            return self.has_change_permission()

        codename = get_permission_codename('add', self.opts)
        return self.user.has_perm("%s.%s" % (self.opts.app_label, codename))

    def has_change_permission(self):
        opts = self.opts
        if opts.auto_created:
            for field in opts.fields:
                if field.remote_field and field.remote_field.model != self.parent_model:
                    opts = field.remote_field.model._meta
                    break

        codename = get_permission_codename('change', opts)
        return self.user.has_perm("%s.%s" % (opts.app_label, codename))

    def has_delete_permission(self):
        if self.opts.auto_created:
            return self.has_change_permission()

        codename = get_permission_codename('delete', self.opts)
        return self.user.has_perm("%s.%s" % (self.opts.app_label, codename))


class GenericInlineModelAdmin(InlineModelAdmin):
    ct_field = "content_type"
    ct_fk_field = "object_id"

    formset = BaseGenericInlineFormSet

    def get_formset(self, **kwargs):
        if self.exclude is None:
            exclude = []
        else:
            exclude = list(self.exclude)
        exclude.extend(self.get_readonly_fields())
        if self.exclude is None and hasattr(self.form, '_meta') and self.form._meta.exclude:
            # Take the custom ModelForm's Meta.exclude into account only if the
            # GenericInlineModelAdmin doesn't define its own.
            exclude.extend(self.form._meta.exclude)
        exclude = exclude or None
        can_delete = self.can_delete and self.has_delete_permission()
        defaults = {
            "ct_field": self.ct_field,
            "fk_field": self.ct_fk_field,
            "form": self.form,
            "formfield_callback": self.formfield_for_dbfield,
            "formset": self.formset,
            "extra": self.extra,
            "can_delete": can_delete,
            "can_order": False,
            "max_num": self.max_num,
            "exclude": exclude,
            'fields': forms.ALL_FIELDS
        }
        defaults.update(kwargs)

        return generic_inlineformset_factory(self.model, **defaults)


class InlineFormset(Fieldset):

    def __init__(self, formset, allow_blank=False, **kwargs):
        self.fields = []
        self.css_class = kwargs.pop('css_class', '')
        self.css_id = "%s-group" % formset.prefix
        self.template = formset.style.template
        self.inline_style = formset.style.name
        if allow_blank and len(formset) == 0:
            self.template = 'xadmin/edit_inline/blank.html'
            self.inline_style = 'blank'
        self.formset = formset
        self.model = formset.model
        self.opts = formset.model._meta
        self.flat_attrs = flatatt(kwargs)
        self.extra_attrs = formset.style.get_attrs()

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        context = get_context_dict(context)
        context.update(dict(
            formset=self,
            prefix=self.formset.prefix,
            inline_style=self.inline_style,
            **self.extra_attrs
        ))
        return render_to_string(self.template, context)


class Inline(Fieldset):

    def __init__(self, rel_model):
        self.model = rel_model
        self.fields = []
        super(Inline, self).__init__(legend="")

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        return ""


def get_first_field(layout, clz):
    for layout_object in layout.fields:
        if issubclass(layout_object.__class__, clz):
            return layout_object
        elif hasattr(layout_object, 'get_field_names'):
            gf = get_first_field(layout_object, clz)
            if gf:
                return gf


def replace_inline_objects(layout, fs):
    if not fs:
        return
    for i, layout_object in enumerate(layout.fields):
        if isinstance(layout_object, Inline) and layout_object.model in fs:
            layout.fields[i] = fs.pop(layout_object.model)
        elif hasattr(layout_object, 'get_field_names'):
            replace_inline_objects(layout_object, fs)


class InlineFormsetPlugin(BaseAdminPlugin):
    inlines = []

    @property
    def inline_instances(self):
        if not hasattr(self, '_inline_instances'):
            inline_instances = []
            for inline_class in self.inlines:
                inline = self.admin_view.get_view(
                    (getattr(inline_class, 'generic_inline', False) and GenericInlineModelAdmin or InlineModelAdmin),
                    inline_class).init(self.admin_view)
                if not (inline.has_add_permission() or
                        inline.has_change_permission() or
                        inline.has_delete_permission() or
                        inline.has_view_permission()):
                    continue
                if not inline.has_add_permission():
                    inline.max_num = 0
                inline_instances.append(inline)
            self._inline_instances = inline_instances

        return self._inline_instances

    def instance_forms(self, ret):
        self.formsets = []
        for inline in self.inline_instances:
            if inline.has_change_permission():
                self.formsets.append(inline.instance_form())
            else:
                self.formsets.append(self._get_detail_formset_instance(inline))
        self.admin_view.formsets = self.formsets

    def valid_forms(self, result):
        return all_valid(self.formsets) and result

    def save_related(self):
        for formset in self.formsets:
            formset.instance = self.admin_view.new_obj
            formset.save()

    def get_context(self, context):
        context['inline_formsets'] = self.formsets
        return context

    def get_error_list(self, errors):
        for fs in self.formsets:
            errors.extend(fs.non_form_errors())
            for errors_in_inline_form in fs.errors:
                errors.extend(errors_in_inline_form.values())
        return errors

    def get_form_layout(self, layout):
        allow_blank = isinstance(self.admin_view, DetailAdminView)
        # fixed #176 bug, change dict to list
        fs = [(f.model, InlineFormset(f, allow_blank)) for f in self.formsets]
        replace_inline_objects(layout, fs)

        if fs:
            container = get_first_field(layout, Column)
            if not container:
                container = get_first_field(layout, Container)
            if not container:
                container = layout

            # fixed #176 bug, change dict to list
            for key, value in fs:
                container.append(value)

        return layout

    def get_media(self, media):
        for fs in self.formsets:
            media = media + fs.media
        if self.formsets:
            media = media + self.vendor(
                'xadmin.plugin.formset.js', 'xadmin.plugin.formset.css')
        return media

    def _get_detail_formset_instance(self, inline):
        formset = inline.instance_form(extra=0, max_num=0, can_delete=0)
        formset.detail_page = True
        if True:
            replace_field_to_value(formset.helper.layout, inline)
            model = inline.model
            opts = model._meta
            fake_admin_class = type(str('%s%sFakeAdmin' % (opts.app_label, opts.model_name)), (object, ), {'model': model})
            for form in formset.forms:
                instance = form.instance
                if instance.pk:
                    form.detail = self.get_view(
                        DetailAdminUtil, fake_admin_class, instance)
        return formset


class DetailAdminUtil(DetailAdminView):

    def init_request(self, obj):
        self.obj = obj
        self.org_obj = obj


class DetailInlineFormsetPlugin(InlineFormsetPlugin):

    def get_model_form(self, form, **kwargs):
        self.formsets = [self._get_detail_formset_instance(
            inline) for inline in self.inline_instances]
        return form

site.register_plugin(InlineFormsetPlugin, ModelFormAdminView)
site.register_plugin(DetailInlineFormsetPlugin, DetailAdminView)
