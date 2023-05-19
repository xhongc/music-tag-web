# coding=utf-8
from django.template import loader

from xadmin.plugins.utils import get_context_dict
from xadmin.sites import site
from xadmin.views import BaseAdminPlugin, ListAdminView

REFRESH_VAR = '_refresh'


class RefreshPlugin(BaseAdminPlugin):

    refresh_times = []

    # Media
    def get_media(self, media):
        if self.refresh_times and self.request.GET.get(REFRESH_VAR):
            media = media + self.vendor('xadmin.plugin.refresh.js')
        return media

    # Block Views
    def block_top_toolbar(self, context, nodes):
        if self.refresh_times:
            current_refresh = self.request.GET.get(REFRESH_VAR)
            context.update({
                'has_refresh': bool(current_refresh),
                'clean_refresh_url': self.admin_view.get_query_string(remove=(REFRESH_VAR,)),
                'current_refresh': current_refresh,
                'refresh_times': [{
                    'time': r,
                    'url': self.admin_view.get_query_string({REFRESH_VAR: r}),
                    'selected': str(r) == current_refresh,
                } for r in self.refresh_times],
            })
            nodes.append(loader.render_to_string('xadmin/blocks/model_list.top_toolbar.refresh.html',
                                                 get_context_dict(context)))


site.register_plugin(RefreshPlugin, ListAdminView)
