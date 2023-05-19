import copy
import functools
import datetime
import decimal
from functools import update_wrapper
from inspect import getfullargspec

from django import forms
from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_permission_codename
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.urls.base import reverse
from django.http import HttpResponse
from django.template import Context, Template
from django.template.response import TemplateResponse
from django.utils import six
from django.utils.decorators import method_decorator, classonlymethod
from django.utils.encoding import force_text, smart_text, smart_str
from django.utils.functional import Promise
from django.utils.http import urlencode
from django.utils.itercompat import is_iterable
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from django.views.generic import View
from collections import OrderedDict
from xadmin.util import static, json, vendor, sortkeypicker

from xadmin.models import Log

csrf_protect_m = method_decorator(csrf_protect)


class IncorrectPluginArg(Exception):
    pass


def get_content_type_for_model(obj):
    from django.contrib.contenttypes.models import ContentType
    return ContentType.objects.get_for_model(obj, for_concrete_model=False)


def filter_chain(filters, token, func, *args, **kwargs):
    if token == -1:
        return func()
    else:
        def _inner_method():
            fm = filters[token]
            fargs = getfullargspec(fm)[0]
            if len(fargs) == 1:
                # Only self arg
                result = func()
                if result is None:
                    return fm()
                else:
                    raise IncorrectPluginArg(u'Plugin filter method need a arg to receive parent method result.')
            else:
                return fm(func if fargs[1] == '__' else func(), *args, **kwargs)

        return filter_chain(filters, token - 1, _inner_method, *args, **kwargs)


def filter_hook(func):
    tag = func.__name__
    func.__doc__ = "``filter_hook``\n\n" + (func.__doc__ or "")

    @functools.wraps(func)
    def method(self, *args, **kwargs):

        def _inner_method():
            return func(self, *args, **kwargs)

        if self.plugins:
            filters = [(getattr(getattr(p, tag), 'priority', 10), getattr(p, tag))
                       for p in self.plugins if callable(getattr(p, tag, None))]
            filters = [f for p, f in sorted(filters, key=lambda x: x[0])]
            return filter_chain(filters, len(filters) - 1, _inner_method, *args, **kwargs)
        else:
            return _inner_method()

    return method


def inclusion_tag(file_name, context_class=Context, takes_context=False):
    def wrap(func):
        @functools.wraps(func)
        def method(self, context, nodes, *arg, **kwargs):
            _dict = func(self, context, nodes, *arg, **kwargs)
            from django.template.loader import get_template, select_template
            cls_str = str if six.PY3 else basestring
            if isinstance(file_name, Template):
                t = file_name
            elif not isinstance(file_name, cls_str) and is_iterable(file_name):
                t = select_template(file_name)
            else:
                t = get_template(file_name)

            _dict['autoescape'] = context.autoescape
            _dict['use_l10n'] = context.use_l10n
            _dict['use_tz'] = context.use_tz
            _dict['admin_view'] = context['admin_view']

            csrf_token = context.get('csrf_token', None)
            if csrf_token is not None:
                _dict['csrf_token'] = csrf_token
            nodes.append(t.render(_dict))

        return method

    return wrap


class JSONEncoder(DjangoJSONEncoder):

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, datetime.date):
            return o.strftime('%Y-%m-%d')
        elif isinstance(o, decimal.Decimal):
            return str(o)
        elif isinstance(o, Promise):
            return force_text(o)
        else:
            try:
                return super(JSONEncoder, self).default(o)
            except Exception:
                return smart_text(o)


class BaseAdminObject(object):

    def get_view(self, view_class, option_class=None, *args, **kwargs):
        opts = kwargs.pop('opts', {})
        return self.admin_site.get_view_class(view_class, option_class, **opts)(self.request, *args, **kwargs)

    def get_model_view(self, view_class, model, *args, **kwargs):
        return self.get_view(view_class, self.admin_site._registry.get(model), *args, **kwargs)

    def get_admin_url(self, name, *args, **kwargs):
        return reverse('%s:%s' % (self.admin_site.app_name, name), args=args, kwargs=kwargs)

    def get_model_url(self, model, name, *args, **kwargs):
        return reverse(
            '%s:%s_%s_%s' % (self.admin_site.app_name, model._meta.app_label,
                             model._meta.model_name, name),
            args=args, kwargs=kwargs, current_app=self.admin_site.name)

    def get_model_perm(self, model, name):
        return '%s.%s_%s' % (model._meta.app_label, name, model._meta.model_name)

    def has_model_perm(self, model, name, user=None):
        user = user or self.user
        return user.has_perm(self.get_model_perm(model, name)) or (
                    name == 'view' and self.has_model_perm(model, 'change', user))

    def get_query_string(self, new_params=None, remove=None):
        if new_params is None:
            new_params = {}
        if remove is None:
            remove = []
        p = dict(self.request.GET.items()).copy()
        arr_keys = list(p.keys())
        for r in remove:
            for k in arr_keys:
                if k.startswith(r):
                    del p[k]
        for k, v in new_params.items():
            if v is None:
                if k in p:
                    del p[k]
            else:
                p[k] = v
        return '?%s' % urlencode(p)

    def get_form_params(self, new_params=None, remove=None):
        if new_params is None:
            new_params = {}
        if remove is None:
            remove = []
        p = dict(self.request.GET.items()).copy()
        arr_keys = list(p.keys())
        for r in remove:
            for k in arr_keys:
                if k.startswith(r):
                    del p[k]
        for k, v in new_params.items():
            if v is None:
                if k in p:
                    del p[k]
            else:
                p[k] = v
        return mark_safe(''.join(
            '<input type="hidden" name="%s" value="%s"/>' % (k, v) for k, v in p.items() if v))

    def render_response(self, content, response_type='json'):
        if response_type == 'json':
            response = HttpResponse(content_type="application/json; charset=UTF-8")
            response.write(
                json.dumps(content, cls=JSONEncoder, ensure_ascii=False))
            return response
        return HttpResponse(content)

    def template_response(self, template, context):
        return TemplateResponse(self.request, template, context)

    def message_user(self, message, level='info'):
        """
        Send a message to the user. The default implementation
        posts a message using the django.contrib.messages backend.
        """
        if hasattr(messages, level) and callable(getattr(messages, level)):
            getattr(messages, level)(self.request, message)

    def static(self, path):
        return static(path)

    def vendor(self, *tags):
        return vendor(*tags)

    def log(self, flag, message, obj=None):
        log = Log(
            user=self.user,
            ip_addr=self.request.META['REMOTE_ADDR'],
            action_flag=flag,
            message=message
        )
        if obj:
            log.content_type = get_content_type_for_model(obj)
            log.object_id = obj.pk
            log.object_repr = force_text(obj)
        log.save()


class BaseAdminPlugin(BaseAdminObject):

    def __init__(self, admin_view):
        self.admin_view = admin_view
        self.admin_site = admin_view.admin_site

        if hasattr(admin_view, 'model'):
            self.model = admin_view.model
            self.opts = admin_view.model._meta

    def init_request(self, *args, **kwargs):
        pass


class BaseAdminView(BaseAdminObject, View):
    """ Base Admin view, support some comm attrs."""

    base_template = 'xadmin/base.html'
    need_site_permission = True

    def __init__(self, request, *args, **kwargs):
        self.request = request
        self.request_method = request.method.lower()
        self.user = request.user

        self.base_plugins = [p(self) for p in getattr(self,
                                                      "plugin_classes", [])]

        self.args = args
        self.kwargs = kwargs
        self.init_plugin(*args, **kwargs)
        self.init_request(*args, **kwargs)

    @classonlymethod
    def as_view(cls):
        def view(request, *args, **kwargs):
            self = cls(request, *args, **kwargs)

            if hasattr(self, 'get') and not hasattr(self, 'head'):
                self.head = self.get

            if self.request_method in self.http_method_names:
                handler = getattr(
                    self, self.request_method, self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed

            return handler(request, *args, **kwargs)

        # take name and docstring from class
        update_wrapper(view, cls, updated=())
        view.need_site_permission = cls.need_site_permission

        return view

    def init_request(self, *args, **kwargs):
        pass

    def init_plugin(self, *args, **kwargs):
        plugins = []
        for p in self.base_plugins:
            p.request = self.request
            p.user = self.user
            p.args = self.args
            p.kwargs = self.kwargs
            result = p.init_request(*args, **kwargs)
            if result is not False:
                plugins.append(p)
        self.plugins = plugins

    @filter_hook
    def get_context(self):
        return {'admin_view': self, 'media': self.media, 'base_template': self.base_template}

    @property
    def media(self):
        return self.get_media()

    @filter_hook
    def get_media(self):
        return forms.Media()


class CommAdminView(BaseAdminView):
    base_template = 'xadmin/base_site.html'
    menu_template = 'xadmin/includes/sitemenu_default.html'

    site_title = getattr(settings, "XADMIN_TITLE", _(u"Django Xadmin"))
    site_footer = getattr(settings, "XADMIN_FOOTER_TITLE", _(u"my-company.inc"))

    global_models_icon = {}
    default_model_icon = None
    apps_label_title = {}
    apps_icons = {}

    def get_site_menu(self):
        return None

    @filter_hook
    def get_nav_menu(self):
        site_menu = list(self.get_site_menu() or [])
        had_urls = []

        def get_url(menu, had_urls):
            if 'url' in menu:
                had_urls.append(menu['url'])
            if 'menus' in menu:
                for m in menu['menus']:
                    get_url(m, had_urls)

        get_url({'menus': site_menu}, had_urls)

        nav_menu = OrderedDict()

        for model, model_admin in self.admin_site._registry.items():
            if getattr(model_admin, 'hidden_menu', False):
                continue
            app_label = model._meta.app_label
            app_icon = None
            model_dict = {
                'title': smart_text(capfirst(model._meta.verbose_name_plural)),
                'url': self.get_model_url(model, "changelist"),
                'icon': self.get_model_icon(model),
                'perm': self.get_model_perm(model, 'view'),
                'order': model_admin.order,
            }
            if model_dict['url'] in had_urls:
                continue

            app_key = "app:%s" % app_label
            if app_key in nav_menu:
                nav_menu[app_key]['menus'].append(model_dict)
            else:
                # Find app title
                app_title = smart_text(app_label.title())
                if app_label.lower() in self.apps_label_title:
                    app_title = self.apps_label_title[app_label.lower()]
                else:
                    app_title = smart_text(apps.get_app_config(app_label).verbose_name)
                # find app icon
                if app_label.lower() in self.apps_icons:
                    app_icon = self.apps_icons[app_label.lower()]

                nav_menu[app_key] = {
                    'title': app_title,
                    'menus': [model_dict],
                }

            app_menu = nav_menu[app_key]
            if app_icon:
                app_menu['first_icon'] = app_icon
            elif ('first_icon' not in app_menu or
                  app_menu['first_icon'] == self.default_model_icon) and model_dict.get('icon'):
                app_menu['first_icon'] = model_dict['icon']

            if 'first_url' not in app_menu and model_dict.get('url'):
                app_menu['first_url'] = model_dict['url']

        for menu in nav_menu.values():
            menu['menus'].sort(key=sortkeypicker(['order', 'title']))

        nav_menu = list(nav_menu.values())
        nav_menu.sort(key=lambda x: x['title'])

        site_menu.extend(nav_menu)

        return site_menu

    @filter_hook
    def get_context(self):
        context = super(CommAdminView, self).get_context()

        if False:
            nav_menu = json.loads(self.request.session['nav_menu'])
        else:
            menus = copy.copy(self.get_nav_menu())

            def check_menu_permission(item):
                need_perm = item.pop('perm', None)
                if need_perm is None:
                    return True
                elif callable(need_perm):
                    return need_perm(self.user)
                elif need_perm == 'super':
                    return self.user.is_superuser
                else:
                    return self.user.has_perm(need_perm)

            def filter_item(item):
                if 'menus' in item:
                    before_filter_length = len(item['menus'])
                    item['menus'] = [filter_item(
                        i) for i in item['menus'] if check_menu_permission(i)]
                    after_filter_length = len(item['menus'])
                    if after_filter_length == 0 and before_filter_length > 0:
                        return None
                return item

            nav_menu = [filter_item(item) for item in menus if check_menu_permission(item)]
            nav_menu = list(filter(lambda x: x['title'] not in ['管理', '认证和授权'], nav_menu))
            if not settings.DEBUG:
                self.request.session['nav_menu'] = json.dumps(nav_menu, cls=JSONEncoder, ensure_ascii=False)
                self.request.session.modified = True

        def check_selected(menu, path):
            selected = False
            if 'url' in menu:
                chop_index = menu['url'].find('?')
                if chop_index == -1:
                    selected = path.startswith(menu['url'])
                else:
                    selected = path.startswith(menu['url'][:chop_index])
            if 'menus' in menu:
                for m in menu['menus']:
                    _s = check_selected(m, path)
                    if _s:
                        selected = True
            if selected:
                menu['selected'] = True
            return selected

        for menu in nav_menu:
            check_selected(menu, self.request.path)

        context.update({
            'menu_template': self.menu_template,
            'nav_menu': nav_menu,
            'site_title': self.site_title,
            'site_footer': self.site_footer,
            'breadcrumbs': self.get_breadcrumb()
        })

        return context

    @filter_hook
    def get_model_icon(self, model):
        icon = self.global_models_icon.get(model)
        if icon is None and model in self.admin_site._registry:
            icon = getattr(self.admin_site._registry[model],
                           'model_icon', self.default_model_icon)
        return icon

    @filter_hook
    def get_breadcrumb(self):
        return [{
            'url': self.get_admin_url('index'),
            'title': _('Home')
        }]


class ModelAdminView(CommAdminView):
    fields = None
    exclude = None
    ordering = None
    model = None
    remove_permissions = []

    def __init__(self, request, *args, **kwargs):
        self.opts = self.model._meta
        self.app_label = self.model._meta.app_label
        self.model_name = self.model._meta.model_name
        self.model_info = (self.app_label, self.model_name)

        super(ModelAdminView, self).__init__(request, *args, **kwargs)

    @filter_hook
    def get_context(self):
        new_context = {
            "opts": self.opts,
            "app_label": self.app_label,
            "model_name": self.model_name,
            "verbose_name": force_text(self.opts.verbose_name),
            'model_icon': self.get_model_icon(self.model),
        }
        context = super(ModelAdminView, self).get_context()
        context.update(new_context)
        return context

    @filter_hook
    def get_breadcrumb(self):
        bcs = super(ModelAdminView, self).get_breadcrumb()
        item = {'title': self.opts.verbose_name_plural}
        if self.has_view_permission():
            item['url'] = self.model_admin_url('changelist')
        bcs.append(item)
        return bcs

    @filter_hook
    def get_object(self, object_id):
        """
        Get model object instance by object_id, used for change admin view
        """
        # first get base admin view property queryset, return default model queryset
        model = self.model
        try:
            object_id = model._meta.pk.to_python(object_id)
            return model.objects.get(pk=object_id)
        except (model.DoesNotExist, ValidationError):
            return None

    @filter_hook
    def get_object_url(self, obj):
        if self.has_change_permission(obj):
            return self.model_admin_url("change", getattr(obj, self.opts.pk.attname))
        elif self.has_view_permission(obj):
            return self.model_admin_url("detail", getattr(obj, self.opts.pk.attname))
        else:
            return None

    def model_admin_url(self, name, *args, **kwargs):
        return reverse(
            "%s:%s_%s_%s" % (self.admin_site.app_name, self.opts.app_label,
                             self.model_name, name), args=args, kwargs=kwargs)

    def get_model_perms(self):
        """
        Returns a dict of all perms for this model. This dict has the keys
        ``add``, ``change``, and ``delete`` mapping to the True/False for each
        of those actions.
        """
        return {
            'view': self.has_view_permission(),
            'add': self.has_add_permission(),
            'change': self.has_change_permission(),
            'delete': self.has_delete_permission(),
        }

    def get_template_list(self, template_name):
        opts = self.opts
        return (
            "xadmin/%s/%s/%s" % (
                opts.app_label, opts.object_name.lower(), template_name),
            "xadmin/%s/%s" % (opts.app_label, template_name),
            "xadmin/%s" % template_name,
        )

    def get_ordering(self):
        """
        Hook for specifying field ordering.
        """
        return self.ordering or ()  # otherwise we might try to *None, which is bad ;)

    @filter_hook
    def queryset(self):
        """
        Returns a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view.
        """
        return self.model._default_manager.get_queryset()

    def has_view_permission(self, obj=None):
        view_codename = get_permission_codename('view', self.opts)
        change_codename = get_permission_codename('change', self.opts)

        return ('view' not in self.remove_permissions) and (
                    self.user.has_perm('%s.%s' % (self.app_label, view_codename)) or
                    self.user.has_perm('%s.%s' % (self.app_label, change_codename)))

    def has_add_permission(self):
        codename = get_permission_codename('add', self.opts)
        return ('add' not in self.remove_permissions) and self.user.has_perm('%s.%s' % (self.app_label, codename))

    def has_change_permission(self, obj=None):
        codename = get_permission_codename('change', self.opts)
        return ('change' not in self.remove_permissions) and self.user.has_perm('%s.%s' % (self.app_label, codename))

    def has_delete_permission(self, request=None, obj=None):
        codename = get_permission_codename('delete', self.opts)
        return ('delete' not in self.remove_permissions) and self.user.has_perm('%s.%s' % (self.app_label, codename))
