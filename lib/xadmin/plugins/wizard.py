import re
from collections import OrderedDict
from django import forms
from django.db import models
from django.template import loader
try:
    from formtools.wizard.storage import get_storage
    from formtools.wizard.forms import ManagementForm
    from formtools.wizard.views import StepsHelper
except:
    # work for django<1.8

    from django.contrib.formtools.wizard.storage import get_storage
    from django.contrib.formtools.wizard.forms import ManagementForm
    from django.contrib.formtools.wizard.views import StepsHelper

from django.utils import six
from django.utils.encoding import smart_text
from django.utils.module_loading import import_string
from django.forms import ValidationError
from django.forms.models import modelform_factory

from xadmin.sites import site
from xadmin.views import BaseAdminPlugin, ModelFormAdminView


def normalize_name(name):
    new = re.sub('(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))', '_\\1', name)
    return new.lower().strip('_')


class WizardFormPlugin(BaseAdminPlugin):

    wizard_form_list = None
    wizard_for_update = False

    storage_name = 'formtools.wizard.storage.session.SessionStorage'
    form_list = None
    initial_dict = None
    instance_dict = None
    condition_dict = None
    file_storage = None

    def _get_form_prefix(self, step=None):
        if step is None:
            step = self.steps.current
        obj = self.get_form_list().keys()
        if six.PY3:
            obj = [s for s in obj]
        return 'step_%d' % obj.index(step)

    def get_form_list(self):
        if not hasattr(self, '_form_list'):
            init_form_list = OrderedDict()

            assert len(
                self.wizard_form_list) > 0, 'at least one form is needed'

            for i, form in enumerate(self.wizard_form_list):
                init_form_list[smart_text(form[0])] = form[1]

            self._form_list = init_form_list

        return self._form_list

    # Plugin replace methods
    def init_request(self, *args, **kwargs):
        if self.request.is_ajax() or ("_ajax" in self.request.GET) or not hasattr(self.request, 'session') or (args and not self.wizard_for_update):
            # update view
            return False
        return bool(self.wizard_form_list)

    def prepare_form(self, __):
        # init storage and step helper
        self.prefix = normalize_name(self.__class__.__name__)
        self.storage = get_storage(
            self.storage_name, self.prefix, self.request,
            getattr(self, 'file_storage', None))
        self.steps = StepsHelper(self)
        self.wizard_goto_step = False

        if self.request.method == 'GET':
            self.storage.reset()
            self.storage.current_step = self.steps.first

            self.admin_view.model_form = self.get_step_form()
        else:
            # Look for a wizard_goto_step element in the posted data which
            # contains a valid step name. If one was found, render the requested
            # form. (This makes stepping back a lot easier).
            wizard_goto_step = self.request.POST.get('wizard_goto_step', None)
            if wizard_goto_step and int(wizard_goto_step) < len(self.get_form_list()):
                obj = self.get_form_list().keys()
                if six.PY3:
                    obj = [s for s in obj]
                self.storage.current_step = obj[int(wizard_goto_step)]
                self.admin_view.model_form = self.get_step_form()
                self.wizard_goto_step = True
                return

            # Check if form was refreshed
            management_form = ManagementForm(
                self.request.POST, prefix=self.prefix)

            if not management_form.is_valid():
                raise ValidationError(
                    'ManagementForm data is missing or has been tampered.')

            form_current_step = management_form.cleaned_data['current_step']
            if (form_current_step != self.steps.current and
                    self.storage.current_step is not None):
                # form refreshed, change current step
                self.storage.current_step = form_current_step

            # get the form for the current step
            self.admin_view.model_form = self.get_step_form()

    def get_form_layout(self, __):
        attrs = self.get_form_list()[self.steps.current]
        if type(attrs) is dict and 'layout' in attrs:
            self.admin_view.form_layout = attrs['layout']
        else:
            self.admin_view.form_layout = None
        return __()

    def get_step_form(self, step=None):
        if step is None:
            step = self.steps.current
        attrs = self.get_form_list()[step]
        if type(attrs) in (list, tuple):
            return modelform_factory(self.model, form=forms.ModelForm,
                                     fields=attrs, formfield_callback=self.admin_view.formfield_for_dbfield)
        elif type(attrs) is dict:
            if attrs.get('fields', None):
                return modelform_factory(self.model, form=forms.ModelForm,
                                         fields=attrs['fields'], formfield_callback=self.admin_view.formfield_for_dbfield)
            if attrs.get('callback', None):
                callback = attrs['callback']
                if callable(callback):
                    return callback(self)
                elif hasattr(self.admin_view, str(callback)):
                    return getattr(self.admin_view, str(callback))(self)
        elif issubclass(attrs, forms.BaseForm):
            return attrs
        return None

    def get_step_form_obj(self, step=None):
        if step is None:
            step = self.steps.current
        form = self.get_step_form(step)
        return form(prefix=self._get_form_prefix(step),
                    data=self.storage.get_step_data(step),
                    files=self.storage.get_step_files(step))

    def get_form_datas(self, datas):
        datas['prefix'] = self._get_form_prefix()
        if self.request.method == 'POST' and self.wizard_goto_step:
            datas.update({
                'data': self.storage.get_step_data(self.steps.current),
                'files': self.storage.get_step_files(self.steps.current)
            })
        return datas

    def valid_forms(self, __):
        if self.wizard_goto_step:
            # goto get_response directly
            return False
        return __()

    def _done(self):
        cleaned_data = self.get_all_cleaned_data()
        exclude = self.admin_view.exclude

        opts = self.admin_view.opts
        instance = self.admin_view.org_obj or self.admin_view.model()

        file_field_list = []
        for f in opts.fields:
            if not f.editable or isinstance(f, models.AutoField) \
                    or not f.name in cleaned_data:
                continue
            if exclude and f.name in exclude:
                continue
            # Defer saving file-type fields until after the other fields, so a
            # callable upload_to can use the values from other fields.
            if isinstance(f, models.FileField):
                file_field_list.append(f)
            else:
                f.save_form_data(instance, cleaned_data[f.name])

        for f in file_field_list:
            f.save_form_data(instance, cleaned_data[f.name])

        instance.save()

        for f in opts.many_to_many:
            if f.name in cleaned_data:
                f.save_form_data(instance, cleaned_data[f.name])

        self.admin_view.new_obj = instance

    def save_forms(self, __):
        # if the form is valid, store the cleaned data and files.
        form_obj = self.admin_view.form_obj
        self.storage.set_step_data(self.steps.current, form_obj.data)
        self.storage.set_step_files(self.steps.current, form_obj.files)

        # check if the current step is the last step
        if self.steps.current == self.steps.last:
            # no more steps, render done view
            return self._done()

    def save_models(self, __):
        pass

    def save_related(self, __):
        pass

    def get_context(self, context):
        context.update({
            "show_save": False,
            "show_save_as_new": False,
            "show_save_and_add_another": False,
            "show_save_and_continue": False,
        })
        return context

    def get_response(self, response):
        self.storage.update_response(response)
        return response

    def post_response(self, __):
        if self.steps.current == self.steps.last:
            self.storage.reset()
            return __()

        # change the stored current step
        self.storage.current_step = self.steps.next

        self.admin_view.form_obj = self.get_step_form_obj()
        self.admin_view.setup_forms()

        return self.admin_view.get_response()

    def get_all_cleaned_data(self):
        """
        Returns a merged dictionary of all step cleaned_data dictionaries.
        If a step contains a `FormSet`, the key will be prefixed with formset
        and contain a list of the formset cleaned_data dictionaries.
        """
        cleaned_data = {}
        for form_key, attrs in self.get_form_list().items():
            form_obj = self.get_step_form_obj(form_key)
            if form_obj.is_valid():
                if type(attrs) is dict and 'convert' in attrs:
                    callback = attrs['convert']
                    if callable(callback):
                        callback(self, cleaned_data, form_obj)
                    elif hasattr(self.admin_view, str(callback)):
                        getattr(self.admin_view,
                                str(callback))(self, cleaned_data, form_obj)
                elif isinstance(form_obj.cleaned_data, (tuple, list)):
                    cleaned_data.update({
                        'formset-%s' % form_key: form_obj.cleaned_data
                    })
                else:
                    cleaned_data.update(form_obj.cleaned_data)
        return cleaned_data

    def get_cleaned_data_for_step(self, step):
        """
        Returns the cleaned data for a given `step`. Before returning the
        cleaned data, the stored values are being revalidated through the
        form. If the data doesn't validate, None will be returned.
        """
        if step in self.get_form_list():
            form_obj = self.get_step_form_obj(step)
            if form_obj.is_valid():
                return form_obj.cleaned_data
        return None

    def get_next_step(self, step=None):
        """
        Returns the next step after the given `step`. If no more steps are
        available, None will be returned. If the `step` argument is None, the
        current step will be determined automatically.
        """
        if step is None:
            step = self.steps.current
        obj = self.get_form_list().keys()
        if six.PY3:
            obj = [s for s in obj]
        key = obj.index(step) + 1
        if len(obj) > key:
            return obj[key]
        return None

    def get_prev_step(self, step=None):
        """
        Returns the previous step before the given `step`. If there are no
        steps available, None will be returned. If the `step` argument is
        None, the current step will be determined automatically.
        """
        if step is None:
            step = self.steps.current
        obj = self.get_form_list().keys()
        if six.PY3:
            obj = [s for s in obj]
        key = obj.index(step) - 1
        if key >= 0:
            return obj[key]
        return None

    def get_step_index(self, step=None):
        """
        Returns the index for the given `step` name. If no step is given,
        the current step will be used to get the index.
        """
        if step is None:
            step = self.steps.current
        obj = self.get_form_list().keys()
        if six.PY3:
            obj = [s for s in obj]
        return obj.index(step)

    def block_before_fieldsets(self, context, nodes):
        context = context.update(dict(self.storage.extra_data))
        context['wizard'] = {
            'steps': self.steps,
            'management_form': ManagementForm(prefix=self.prefix, initial={
                'current_step': self.steps.current,
            }),
        }
        nodes.append(loader.render_to_string('xadmin/blocks/model_form.before_fieldsets.wizard.html', context))

    def block_submit_line(self, context, nodes):
        context = context.update(dict(self.storage.extra_data))
        context['wizard'] = {
            'steps': self.steps
        }

        nodes.append(loader.render_to_string('xadmin/blocks/model_form.submit_line.wizard.html', context))

site.register_plugin(WizardFormPlugin, ModelFormAdminView)
