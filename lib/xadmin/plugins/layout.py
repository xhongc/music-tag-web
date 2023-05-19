# coding=utf-8
from django.template import loader
from django.utils.translation import ugettext_lazy as _

from xadmin.plugins.utils import get_context_dict
from xadmin.sites import site
from xadmin.views import BaseAdminPlugin, ListAdminView
from xadmin.util import label_for_field

LAYOUT_VAR = '_layout'

DEFAULT_LAYOUTS = {
    'table': {
        'key': 'table',
        'icon': 'fa fa-table',
        'name': _(u'Table'),
        'template': 'views/model_list.html',
    },
    'thumbnails': {
        'key': 'thumbnails',
        'icon': 'fa fa-th-large',
        'name': _(u'Thumbnails'),
        'template': 'grids/thumbnails.html',
    },
}


class GridLayoutPlugin(BaseAdminPlugin):

    grid_layouts = []

    _active_layouts = []
    _current_layout = None
    _current_icon = 'table'

    def get_layout(self, l):
        item = (type(l) is dict) and l or DEFAULT_LAYOUTS[l]
        return dict({'url': self.admin_view.get_query_string({LAYOUT_VAR: item['key']}), 'selected': False}, **item)

    def init_request(self, *args, **kwargs):
        active = bool(self.request.method == 'GET' and self.grid_layouts)
        if active:
            layouts = (type(self.grid_layouts) in (list, tuple)) and self.grid_layouts or (self.grid_layouts,)
            self._active_layouts = [self.get_layout(l) for l in layouts]
            self._current_layout = self.request.GET.get(LAYOUT_VAR, self._active_layouts[0]['key'])
            for layout in self._active_layouts:
                if self._current_layout == layout['key']:
                    self._current_icon = layout['icon']
                    layout['selected'] = True
                    self.admin_view.object_list_template = self.admin_view.get_template_list(layout['template'])
        return active

    def result_item(self, item, obj, field_name, row):
        if self._current_layout == 'thumbnails':
            if getattr(item.attr, 'is_column', True):
                item.field_label = label_for_field(
                    field_name, self.model,
                    model_admin=self.admin_view,
                    return_attr=False
                )
            if getattr(item.attr, 'thumbnail_img', False):
                setattr(item, 'thumbnail_hidden', True)
                row['thumbnail_img'] = item
            elif item.is_display_link:
                setattr(item, 'thumbnail_hidden', True)
                row['thumbnail_label'] = item

        return item

    # Block Views
    def block_top_toolbar(self, context, nodes):
        if len(self._active_layouts) > 1:
            context.update({
                'layouts': self._active_layouts,
                'current_icon': self._current_icon,
            })
            nodes.append(loader.render_to_string('xadmin/blocks/model_list.top_toolbar.layouts.html',
                                                 context=get_context_dict(context)))


site.register_plugin(GridLayoutPlugin, ListAdminView)
