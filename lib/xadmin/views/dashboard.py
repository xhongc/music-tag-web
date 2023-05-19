from django import forms
from django.apps import apps
from django.core.exceptions import PermissionDenied
from django.urls.base import reverse, NoReverseMatch
from django.template.context_processors import csrf
from django.db.models.base import ModelBase
from django.forms.forms import DeclarativeFieldsMetaclass
from django.forms.utils import flatatt
from django.template import loader
from django.http import Http404
from django.test.client import RequestFactory
from django.utils.encoding import force_text, smart_text
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.utils.http import urlencode, urlquote
from django.views.decorators.cache import never_cache
from xadmin import widgets as exwidgets
from xadmin.layout import FormHelper
from xadmin.models import UserSettings, UserWidget
from xadmin.plugins.utils import get_context_dict
from xadmin.sites import site
from xadmin.views.base import CommAdminView, ModelAdminView, filter_hook, csrf_protect_m
from xadmin.views.edit import CreateAdminView
from xadmin.views.list import ListAdminView
from xadmin.util import unquote
import copy


class WidgetTypeSelect(forms.Widget):

    def __init__(self, widgets, attrs=None):
        super(WidgetTypeSelect, self).__init__(attrs)
        self._widgets = widgets

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, extra_attrs={'name': name})
        final_attrs['class'] = 'nav nav-pills nav-stacked'
        output = [u'<ul%s>' % flatatt(final_attrs)]
        options = self.render_options(force_text(value), final_attrs['id'])
        if options:
            output.append(options)
        output.append(u'</ul>')
        output.append('<input type="hidden" id="%s_input" name="%s" value="%s"/>' %
                      (final_attrs['id'], name, force_text(value)))
        return mark_safe(u'\n'.join(output))

    def render_option(self, selected_choice, widget, id):
        if widget.widget_type == selected_choice:
            selected_html = u' class="active"'
        else:
            selected_html = ''
        return (u'<li%s><a onclick="' +
                'javascript:$(this).parent().parent().find(\'>li\').removeClass(\'active\');$(this).parent().addClass(\'active\');' +
                '$(\'#%s_input\').attr(\'value\', \'%s\')' % (id, widget.widget_type) +
                '"><h4><i class="%s"></i> %s</h4><p>%s</p></a></li>') % (
                    selected_html,
                    widget.widget_icon,
                    widget.widget_title or widget.widget_type,
                    widget.description)

    def render_options(self, selected_choice, id):
        # Normalize to strings.
        output = []
        for widget in self._widgets:
            output.append(self.render_option(selected_choice, widget, id))
        return u'\n'.join(output)


class UserWidgetAdmin(object):

    model_icon = 'fa fa-dashboard'
    list_display = ('widget_type', 'page_id', 'user')
    list_filter = ['user', 'widget_type', 'page_id']
    list_display_links = ('widget_type',)
    user_fields = ['user']
    hidden_menu = True

    wizard_form_list = (
        (_(u"Widget Type"), ('page_id', 'widget_type')),
        (_(u"Widget Params"), {'callback':
                               "get_widget_params_form", 'convert': "convert_widget_params"})
    )

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'widget_type':
            widgets = widget_manager.get_widgets(self.request.GET.get('page_id', ''))
            form_widget = WidgetTypeSelect(widgets)
            return forms.ChoiceField(choices=[(w.widget_type, w.description) for w in widgets],
                                     widget=form_widget, label=_('Widget Type'))
        if 'page_id' in self.request.GET and db_field.name == 'page_id':
            kwargs['widget'] = forms.HiddenInput
        field = super(
            UserWidgetAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        return field

    def get_widget_params_form(self, wizard):
        data = wizard.get_cleaned_data_for_step(wizard.steps.first)
        widget_type = data['widget_type']
        widget = widget_manager.get(widget_type)
        fields = copy.deepcopy(widget.base_fields)
        if 'id' in fields:
            del fields['id']
        return DeclarativeFieldsMetaclass("WidgetParamsForm", (forms.Form,), fields)

    def convert_widget_params(self, wizard, cleaned_data, form):
        widget = UserWidget()
        value = dict([(f.name, f.value()) for f in form])
        widget.set_value(value)
        cleaned_data['value'] = widget.value
        cleaned_data['user'] = self.user

    def get_list_display(self):
        list_display = super(UserWidgetAdmin, self).get_list_display()
        if not self.user.is_superuser:
            list_display.remove('user')
        return list_display

    def queryset(self):
        if self.user.is_superuser:
            return super(UserWidgetAdmin, self).queryset()
        return UserWidget.objects.filter(user=self.user)

    def update_dashboard(self, obj):
        try:
            portal_pos = UserSettings.objects.get(
                user=obj.user, key="dashboard:%s:pos" % obj.page_id)
        except UserSettings.DoesNotExist:
            return
        pos = [[w for w in col.split(',') if w != str(
            obj.id)] for col in portal_pos.value.split('|')]
        portal_pos.value = '|'.join([','.join(col) for col in pos])
        portal_pos.save()

    def delete_model(self):
        self.update_dashboard(self.obj)
        super(UserWidgetAdmin, self).delete_model()

    def delete_models(self, queryset):
        for obj in queryset:
            self.update_dashboard(obj)
        super(UserWidgetAdmin, self).delete_models(queryset)


site.register(UserWidget, UserWidgetAdmin)


class WidgetManager(object):
    _widgets = None

    def __init__(self):
        self._widgets = {}

    def register(self, widget_class):
        self._widgets[widget_class.widget_type] = widget_class
        return widget_class

    def get(self, name):
        return self._widgets[name]

    def get_widgets(self, page_id):
        return self._widgets.values()

widget_manager = WidgetManager()


class WidgetDataError(Exception):

    def __init__(self, widget, errors):
        super(WidgetDataError, self).__init__(str(errors))
        self.widget = widget
        self.errors = errors


class BaseWidget(forms.Form):

    template = 'xadmin/widgets/base.html'
    description = 'Base Widget, don\'t use it.'
    widget_title = None
    widget_icon = 'fa fa-plus-square'
    widget_type = 'base'
    base_title = None

    id = forms.IntegerField(label=_('Widget ID'), widget=forms.HiddenInput)
    title = forms.CharField(label=_('Widget Title'), required=False, widget=exwidgets.AdminTextInputWidget)

    def __init__(self, dashboard, data):
        self.dashboard = dashboard
        self.admin_site = dashboard.admin_site
        self.request = dashboard.request
        self.user = dashboard.request.user
        self.convert(data)
        super(BaseWidget, self).__init__(data)

        if not self.is_valid():
            raise WidgetDataError(self, self.errors.as_text())

        self.setup()

    def setup(self):
        helper = FormHelper()
        helper.form_tag = False
        helper.include_media = False
        self.helper = helper

        self.id = self.cleaned_data['id']
        self.title = self.cleaned_data['title'] or self.base_title

        if not (self.user.is_superuser or self.has_perm()):
            raise PermissionDenied

    @property
    def widget(self):
        context = {'widget_id': self.id, 'widget_title': self.title, 'widget_icon': self.widget_icon,
                   'widget_type': self.widget_type, 'form': self, 'widget': self}
        context.update(csrf(self.request))
        self.context(context)
        return loader.render_to_string(self.template, context)

    def context(self, context):
        pass

    def convert(self, data):
        pass

    def has_perm(self):
        return False

    def save(self):
        value = dict([(f.name, f.value()) for f in self])
        user_widget = UserWidget.objects.get(id=self.id)
        user_widget.set_value(value)
        user_widget.save()

    def static(self, path):
        return self.dashboard.static(path)

    def vendor(self, *tags):
        return self.dashboard.vendor(*tags)

    def media(self):
        return forms.Media()


@widget_manager.register
class HtmlWidget(BaseWidget):
    widget_type = 'html'
    widget_icon = 'fa fa-file-o'
    description = _(
        u'Html Content Widget, can write any html content in widget.')

    content = forms.CharField(label=_(
        'Html Content'), widget=exwidgets.AdminTextareaWidget, required=False)

    def has_perm(self):
        return True

    def context(self, context):
        context['content'] = self.cleaned_data['content']


class ModelChoiceIterator(object):

    def __init__(self, field):
        self.field = field

    def __iter__(self):
        from xadmin import site as g_admin_site
        for m, ma in g_admin_site._registry.items():
            yield ('%s.%s' % (m._meta.app_label, m._meta.model_name),
                   m._meta.verbose_name)


class ModelChoiceField(forms.ChoiceField):

    def __init__(self, *, required=True, widget=None, label=None, initial=None,
                 help_text=None, **kwargs):
        # Call Field instead of ChoiceField __init__() because we don't need
        # ChoiceField.__init__().
        forms.Field.__init__(self, **kwargs)
        self.widget.choices = self.choices

    def __deepcopy__(self, memo):
        result = forms.Field.__deepcopy__(self, memo)
        return result

    def _get_choices(self):
        return ModelChoiceIterator(self)

    choices = property(_get_choices, forms.ChoiceField._set_choices)

    def to_python(self, value):
        if isinstance(value, ModelBase):
            return value
        app_label, model_name = value.lower().split('.')
        return apps.get_model(app_label, model_name)

    def prepare_value(self, value):
        if isinstance(value, ModelBase):
            value = '%s.%s' % (value._meta.app_label, value._meta.model_name)
        return value

    def valid_value(self, value):
        value = self.prepare_value(value)
        for k, v in self.choices:
            if value == smart_text(k):
                return True
        return False


class ModelBaseWidget(BaseWidget):

    app_label = None
    model_name = None
    model_perm = 'change'
    model = ModelChoiceField(label=_(u'Target Model'), widget=exwidgets.AdminSelectWidget)

    def __init__(self, dashboard, data):
        self.dashboard = dashboard
        super(ModelBaseWidget, self).__init__(dashboard, data)

    def setup(self):
        self.model = self.cleaned_data['model']
        self.app_label = self.model._meta.app_label
        self.model_name = self.model._meta.model_name

        super(ModelBaseWidget, self).setup()

    def has_perm(self):
        return self.dashboard.has_model_perm(self.model, self.model_perm)

    def filte_choices_model(self, model, modeladmin):
        return self.dashboard.has_model_perm(model, self.model_perm)

    def model_admin_url(self, name, *args, **kwargs):
        return reverse(
            "%s:%s_%s_%s" % (self.admin_site.app_name, self.app_label,
                             self.model_name, name), args=args, kwargs=kwargs)


class PartialBaseWidget(BaseWidget):

    def get_view_class(self, view_class, model=None, **opts):
        admin_class = self.admin_site._registry.get(model) if model else None
        return self.admin_site.get_view_class(view_class, admin_class, **opts)

    def get_factory(self):
        return RequestFactory()

    def setup_request(self, request):
        request.user = self.user
        request.session = self.request.session
        return request

    def make_get_request(self, path, data={}, **extra):
        req = self.get_factory().get(path, data, **extra)
        return self.setup_request(req)

    def make_post_request(self, path, data={}, **extra):
        req = self.get_factory().post(path, data, **extra)
        return self.setup_request(req)


@widget_manager.register
class QuickBtnWidget(BaseWidget):
    widget_type = 'qbutton'
    description = _(u'Quick button Widget, quickly open any page.')
    template = "xadmin/widgets/qbutton.html"
    base_title = _(u"Quick Buttons")
    widget_icon = 'fa fa-caret-square-o-right'

    def convert(self, data):
        self.q_btns = data.pop('btns', [])

    def get_model(self, model_or_label):
        if isinstance(model_or_label, ModelBase):
            return model_or_label
        else:
            return apps.get_model(*model_or_label.lower().split('.'))

    def context(self, context):
        btns = []
        for b in self.q_btns:
            btn = {}
            if 'model' in b:
                model = self.get_model(b['model'])
                if not self.user.has_perm("%s.view_%s" % (model._meta.app_label, model._meta.model_name)):
                    continue
                btn['url'] = reverse("%s:%s_%s_%s" % (self.admin_site.app_name, model._meta.app_label,
                                                      model._meta.model_name, b.get('view', 'changelist')))
                btn['title'] = model._meta.verbose_name
                btn['icon'] = self.dashboard.get_model_icon(model)
            else:
                try:
                    btn['url'] = reverse(b['url'])
                except NoReverseMatch:
                    btn['url'] = b['url']

            if 'title' in b:
                btn['title'] = b['title']
            if 'icon' in b:
                btn['icon'] = b['icon']
            btns.append(btn)

        context.update({'btns': btns})

    def has_perm(self):
        return True


@widget_manager.register
class ListWidget(ModelBaseWidget, PartialBaseWidget):
    widget_type = 'list'
    description = _(u'Any Objects list Widget.')
    template = "xadmin/widgets/list.html"
    model_perm = 'view'
    widget_icon = 'fa fa-align-justify'

    def convert(self, data):
        self.list_params = data.pop('params', {})
        self.list_count = data.pop('count', 10)

    def setup(self):
        super(ListWidget, self).setup()

        if not self.title:
            self.title = self.model._meta.verbose_name_plural

        req = self.make_get_request("", self.list_params)
        self.list_view = self.get_view_class(ListAdminView, self.model)(req)
        if self.list_count:
            self.list_view.list_per_page = self.list_count

    def context(self, context):
        list_view = self.list_view
        list_view.make_result_list()

        base_fields = list_view.base_list_display
        if len(base_fields) > 5:
            base_fields = base_fields[0:5]

        context['result_headers'] = [c for c in list_view.result_headers(
        ).cells if c.field_name in base_fields]
        context['results'] = [[o for i, o in
                               enumerate(filter(lambda c:c.field_name in base_fields, r.cells))]
                              for r in list_view.results()]
        context['result_count'] = list_view.result_count
        context['page_url'] = self.model_admin_url('changelist') + "?" + urlencode(self.list_params)


@widget_manager.register
class AddFormWidget(ModelBaseWidget, PartialBaseWidget):
    widget_type = 'addform'
    description = _(u'Add any model object Widget.')
    template = "xadmin/widgets/addform.html"
    model_perm = 'add'
    widget_icon = 'fa fa-plus'

    def setup(self):
        super(AddFormWidget, self).setup()

        if self.title is None:
            self.title = _('Add %s') % self.model._meta.verbose_name

        req = self.make_get_request("")
        self.add_view = self.get_view_class(
            CreateAdminView, self.model, list_per_page=10)(req)
        self.add_view.instance_forms()

    def context(self, context):
        helper = FormHelper()
        helper.form_tag = False
        helper.include_media = False

        context.update({
            'addform': self.add_view.form_obj,
            'addhelper': helper,
            'addurl': self.add_view.model_admin_url('add'),
            'model': self.model
        })

    def media(self):
        return self.add_view.media + self.add_view.form_obj.media + self.vendor('xadmin.plugin.quick-form.js')


class Dashboard(CommAdminView):

    widget_customiz = True
    widgets = []
    title = _(u"Dashboard")
    icon = None

    def get_page_id(self):
        return self.request.path

    def get_portal_key(self):
        return "dashboard:%s:pos" % self.get_page_id()

    @filter_hook
    def get_widget(self, widget_or_id, data=None):
        try:
            if isinstance(widget_or_id, UserWidget):
                widget = widget_or_id
            else:
                widget = UserWidget.objects.get(user=self.user, page_id=self.get_page_id(), id=widget_or_id)
            wid = widget_manager.get(widget.widget_type)

            class widget_with_perm(wid):

                def context(self, context):
                    super(widget_with_perm, self).context(context)
                    context.update({'has_change_permission': self.request.user.has_perm('xadmin.change_userwidget')})
            wid_instance = widget_with_perm(self, data or widget.get_value())
            return wid_instance
        except UserWidget.DoesNotExist:
            return None

    @filter_hook
    def get_init_widget(self):
        portal = []
        widgets = self.widgets
        for col in widgets:
            portal_col = []
            for opts in col:
                try:
                    widget = UserWidget(user=self.user, page_id=self.get_page_id(), widget_type=opts['type'])
                    widget.set_value(opts)
                    widget.save()
                    portal_col.append(self.get_widget(widget))
                except (PermissionDenied, WidgetDataError):
                    widget.delete()
                    continue
            portal.append(portal_col)

        UserSettings(
            user=self.user, key="dashboard:%s:pos" % self.get_page_id(),
            value='|'.join([','.join([str(w.id) for w in col]) for col in portal])).save()

        return portal

    @filter_hook
    def get_widgets(self):

        if self.widget_customiz:
            portal_pos = UserSettings.objects.filter(
                user=self.user, key=self.get_portal_key())
            if len(portal_pos):
                portal_pos = portal_pos[0].value
                widgets = []

                if portal_pos:
                    user_widgets = dict([(uw.id, uw) for uw in UserWidget.objects.filter(user=self.user, page_id=self.get_page_id())])
                    for col in portal_pos.split('|'):
                        ws = []
                        for wid in col.split(','):
                            try:
                                widget = user_widgets.get(int(wid))
                                if widget:
                                    ws.append(self.get_widget(widget))
                            except Exception as e:
                                import logging
                                logging.error(e, exc_info=True)
                        widgets.append(ws)

                return widgets

        return self.get_init_widget()

    @filter_hook
    def get_title(self):
        return self.title

    @filter_hook
    def get_context(self):
        new_context = {
            'title': self.get_title(),
            'icon': self.icon,
            'portal_key': self.get_portal_key(),
            'columns': [('col-sm-%d' % int(12 / len(self.widgets)), ws) for ws in self.widgets],
            'has_add_widget_permission': self.has_model_perm(UserWidget, 'add') and self.widget_customiz,
            'add_widget_url': self.get_admin_url('%s_%s_add' % (UserWidget._meta.app_label, UserWidget._meta.model_name)) +
            "?user=%s&page_id=%s&_redirect=%s" % (self.user.id, self.get_page_id(), urlquote(self.request.get_full_path()))
        }
        context = super(Dashboard, self).get_context()
        context.update(new_context)
        return context

    @never_cache
    def get(self, request, *args, **kwargs):
        self.widgets = self.get_widgets()
        return self.template_response('xadmin/views/dashboard.html', self.get_context())

    @csrf_protect_m
    def post(self, request, *args, **kwargs):
        if 'id' in request.POST:
            widget_id = request.POST['id']
            if request.POST.get('_delete', None) != 'on':
                widget = self.get_widget(widget_id, request.POST.copy())
                widget.save()
            else:
                try:
                    widget = UserWidget.objects.get(
                        user=self.user, page_id=self.get_page_id(), id=widget_id)
                    widget.delete()
                    try:
                        portal_pos = UserSettings.objects.get(user=self.user, key="dashboard:%s:pos" % self.get_page_id())
                        pos = [[w for w in col.split(',') if w != str(
                            widget_id)] for col in portal_pos.value.split('|')]
                        portal_pos.value = '|'.join([','.join(col) for col in pos])
                        portal_pos.save()
                    except Exception:
                        pass
                except UserWidget.DoesNotExist:
                    pass

        return self.get(request)

    @filter_hook
    def get_media(self):
        media = super(Dashboard, self).get_media() + \
            self.vendor('xadmin.page.dashboard.js', 'xadmin.page.dashboard.css')
        if self.widget_customiz:
            media = media + self.vendor('xadmin.plugin.portal.js')
        for ws in self.widgets:
            for widget in ws:
                media = media + widget.media()
        return media


class ModelDashboard(Dashboard, ModelAdminView):

    title = _(u"%s Dashboard")

    def get_page_id(self):
        return 'model:%s/%s' % self.model_info

    @filter_hook
    def get_title(self):
        return self.title % force_text(self.obj)

    def init_request(self, object_id, *args, **kwargs):
        self.obj = self.get_object(unquote(object_id))

        if not self.has_view_permission(self.obj):
            raise PermissionDenied

        if self.obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') %
                          {'name': force_text(self.opts.verbose_name), 'key': escape(object_id)})

    @filter_hook
    def get_context(self):
        new_context = {
            'has_change_permission': self.has_change_permission(self.obj),
            'object': self.obj,
        }
        context = Dashboard.get_context(self)
        context.update(ModelAdminView.get_context(self))
        context.update(new_context)
        return context

    @never_cache
    def get(self, request, *args, **kwargs):
        self.widgets = self.get_widgets()
        return self.template_response(self.get_template_list('views/model_dashboard.html'), self.get_context())
