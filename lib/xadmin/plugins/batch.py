
import copy
from django import forms
from django.db import models
from django.core.exceptions import PermissionDenied
from django.forms.models import modelform_factory
from django.template.response import TemplateResponse
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _, ugettext_lazy
from xadmin.layout import FormHelper, Layout, Fieldset, Container, Col
from xadmin.plugins.actions import BaseActionView, ACTION_CHECKBOX_NAME
from xadmin.util import model_ngettext, vendor
from xadmin.views.base import filter_hook
from xadmin.views.edit import ModelFormAdminView

BATCH_CHECKBOX_NAME = '_batch_change_fields'


class ChangeFieldWidgetWrapper(forms.Widget):

    def __init__(self, widget):
        self.needs_multipart_form = widget.needs_multipart_form
        self.attrs = widget.attrs
        self.widget = widget

    def __deepcopy__(self, memo):
        obj = copy.copy(self)
        obj.widget = copy.deepcopy(self.widget, memo)
        obj.attrs = self.widget.attrs
        memo[id(self)] = obj
        return obj

    @property
    def media(self):
        media = self.widget.media + vendor('xadmin.plugin.batch.js')
        return media

    def render(self, name, value, attrs=None):
        output = []
        is_required = self.widget.is_required
        output.append(u'<label class="btn btn-info btn-xs">'
            '<input type="checkbox" class="batch-field-checkbox" name="%s" value="%s"%s/> %s</label>' %
            (BATCH_CHECKBOX_NAME, name, (is_required and ' checked="checked"' or ''), _('Change this field')))
        output.extend([('<div class="control-wrap" style="margin-top: 10px;%s" id="id_%s_wrap_container">' %
            ((not is_required and 'display: none;' or ''), name)),
            self.widget.render(name, value, attrs), '</div>'])
        return mark_safe(u''.join(output))

    def build_attrs(self, extra_attrs=None, **kwargs):
        "Helper function for building an attribute dictionary."
        self.attrs = self.widget.build_attrs(extra_attrs=None, **kwargs)
        return self.attrs

    def value_from_datadict(self, data, files, name):
        return self.widget.value_from_datadict(data, files, name)

    def id_for_label(self, id_):
        return self.widget.id_for_label(id_)

class BatchChangeAction(BaseActionView):

    action_name = "change_selected"
    description = ugettext_lazy(
        u'Batch Change selected %(verbose_name_plural)s')

    batch_change_form_template = None

    model_perm = 'change'

    batch_fields = []

    def change_models(self, queryset, cleaned_data):
        n = queryset.count()

        data = {}
        fields = self.opts.fields + self.opts.many_to_many
        for f in fields:
            if not f.editable or isinstance(f, models.AutoField) \
                    or not f.name in cleaned_data:
                continue
            data[f] = cleaned_data[f.name]

        if n:
            for obj in queryset:
                for f, v in data.items():
                    f.save_form_data(obj, v)
                obj.save()
            self.message_user(_("Successfully change %(count)d %(items)s.") % {
                "count": n, "items": model_ngettext(self.opts, n)
            }, 'success')

    def get_change_form(self, is_post, fields):
        edit_view = self.get_model_view(ModelFormAdminView, self.model)

        def formfield_for_dbfield(db_field, **kwargs):
            formfield = edit_view.formfield_for_dbfield(db_field, required=is_post, **kwargs)
            formfield.widget = ChangeFieldWidgetWrapper(formfield.widget)
            return formfield

        defaults = {
            "form": edit_view.form,
            "fields": fields,
            "formfield_callback": formfield_for_dbfield,
        }
        return modelform_factory(self.model, **defaults)

    def do_action(self, queryset):
        if not self.has_change_permission():
            raise PermissionDenied

        change_fields = [f for f in self.request.POST.getlist(BATCH_CHECKBOX_NAME) if f in self.batch_fields]

        if change_fields and self.request.POST.get('post'):
            self.form_obj = self.get_change_form(True, change_fields)(
                data=self.request.POST, files=self.request.FILES)
            if self.form_obj.is_valid():
                self.change_models(queryset, self.form_obj.cleaned_data)
                return None
        else:
            self.form_obj = self.get_change_form(False, self.batch_fields)()

        helper = FormHelper()
        helper.form_tag = False
        helper.include_media = False
        helper.add_layout(Layout(Container(Col('full',
            Fieldset("", *self.form_obj.fields.keys(), css_class="unsort no_title"), horizontal=True, span=12)
        )))
        self.form_obj.helper = helper
        count = len(queryset)
        if count == 1:
            objects_name = force_text(self.opts.verbose_name)
        else:
            objects_name = force_text(self.opts.verbose_name_plural)

        context = self.get_context()
        context.update({
            "title": _("Batch change %s") % objects_name,
            'objects_name': objects_name,
            'form': self.form_obj,
            'queryset': queryset,
            'count': count,
            "opts": self.opts,
            "app_label": self.app_label,
            'action_checkbox_name': ACTION_CHECKBOX_NAME,
        })

        return TemplateResponse(self.request, self.batch_change_form_template or
                                self.get_template_list('views/batch_change_form.html'), context)

    @filter_hook
    def get_media(self):
        media = super(BatchChangeAction, self).get_media()
        media = media + self.form_obj.media + self.vendor(
            'xadmin.page.form.js', 'xadmin.form.css')
        return media
