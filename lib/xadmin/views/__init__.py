from __future__ import absolute_import

from .base import BaseAdminPlugin, BaseAdminView, CommAdminView, ModelAdminView, filter_hook, csrf_protect_m, BaseAdminObject

from .list import ListAdminView
from .edit import CreateAdminView, UpdateAdminView, ModelFormAdminView
from .delete import DeleteAdminView
from .detail import DetailAdminView
from .form import FormAdminView
from .dashboard import Dashboard, BaseWidget, widget_manager, ModelDashboard
from .website import IndexView, LoginView, LogoutView, UserSettingView

__all__ = (
    'BaseAdminObject',
    'BaseAdminPlugin', 'BaseAdminView', 'CommAdminView', 'ModelAdminView', 'ListAdminView',
    'ModelFormAdminView', 'CreateAdminView', 'UpdateAdminView', 'DeleteAdminView', 'DetailAdminView', 'FormAdminView',
    'Dashboard', 'BaseWidget',
    'IndexView', 'LoginView', 'LogoutView',
    'filter_hook', 'csrf_protect_m'
)

# admin site-wide views


def register_builtin_views(site):
    site.register_view(r'^$', IndexView, name='index')
    site.register_view(r'^login/$', LoginView, name='login')
    site.register_view(r'^logout/$', LogoutView, name='logout')

    site.register_view(r'^settings/user$', UserSettingView, name='user_settings')

    site.register_modelview(r'^$', ListAdminView, name='%s_%s_changelist')
    site.register_modelview(r'^add/$', CreateAdminView, name='%s_%s_add')
    site.register_modelview(
        r'^(.+)/delete/$', DeleteAdminView, name='%s_%s_delete')
    site.register_modelview(
        r'^(.+)/update/$', UpdateAdminView, name='%s_%s_change')
    site.register_modelview(
        r'^(.+)/detail/$', DetailAdminView, name='%s_%s_detail')
    site.register_modelview(
        r'^(.+)/dashboard/$', ModelDashboard, name='%s_%s_dashboard')

    site.set_loginview(LoginView)
