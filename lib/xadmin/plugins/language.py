
from django.conf import settings
from django.template import loader
from django.views.i18n import set_language
from xadmin.plugins.utils import get_context_dict
from xadmin.sites import site
from xadmin.views import BaseAdminPlugin, CommAdminView, BaseAdminView


class SetLangNavPlugin(BaseAdminPlugin):

    def block_top_navmenu(self, context, nodes):
        context = get_context_dict(context)
        context['redirect_to'] = self.request.get_full_path()
        nodes.append(loader.render_to_string('xadmin/blocks/comm.top.setlang.html', context=context))


class SetLangView(BaseAdminView):

    def post(self, request, *args, **kwargs):
        if 'nav_menu' in request.session:
            del request.session['nav_menu']
        return set_language(request)

if settings.LANGUAGES and 'django.middleware.locale.LocaleMiddleware' in settings.MIDDLEWARE:
    site.register_plugin(SetLangNavPlugin, CommAdminView)
    site.register_view(r'^i18n/setlang/$', SetLangView, 'set_language')
