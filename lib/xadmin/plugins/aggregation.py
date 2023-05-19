from django.db.models import FieldDoesNotExist, Avg, Max, Min, Count, Sum
from django.utils.translation import ugettext as _
from django.forms import Media

from xadmin.sites import site
from xadmin.views import BaseAdminPlugin, ListAdminView

from xadmin.views.list import ResultRow, ResultItem
from xadmin.util import display_for_field

AGGREGATE_METHODS = {
    'min': Min, 'max': Max, 'avg': Avg, 'sum': Sum, 'count': Count
}
AGGREGATE_TITLE = {
    'min': _('Min'), 'max': _('Max'), 'avg': _('Avg'), 'sum': _('Sum'), 'count': _('Count')
}


class AggregationPlugin(BaseAdminPlugin):

    aggregate_fields = {}

    def init_request(self, *args, **kwargs):
        return bool(self.aggregate_fields)

    def _get_field_aggregate(self, field_name, obj, row):
        item = ResultItem(field_name, row)
        item.classes = ['aggregate', ]
        if field_name not in self.aggregate_fields:
            item.text = ""
        else:
            try:
                f = self.opts.get_field(field_name)
                agg_method = self.aggregate_fields[field_name]
                key = '%s__%s' % (field_name, agg_method)
                if key not in obj:
                    item.text = ""
                else:
                    item.text = display_for_field(obj[key], f)
                    item.wraps.append('%%s<span class="aggregate_title label label-info">%s</span>' % AGGREGATE_TITLE[agg_method])
                    item.classes.append(agg_method)
            except FieldDoesNotExist:
                item.text = ""

        return item

    def _get_aggregate_row(self):
        queryset = self.admin_view.list_queryset._clone()
        obj = queryset.aggregate(*[AGGREGATE_METHODS[method](field_name) for field_name, method in
                                   self.aggregate_fields.items() if method in AGGREGATE_METHODS])

        row = ResultRow()
        row['is_display_first'] = False
        row.cells = [self._get_field_aggregate(field_name, obj, row) for field_name in self.admin_view.list_display]
        row.css_class = 'info aggregate'
        return row

    def results(self, rows):
        if rows:
            rows.append(self._get_aggregate_row())
        return rows

    # Media
    def get_media(self, media):
        return media + Media(css={'screen': [self.static('xadmin/css/xadmin.plugin.aggregation.css'), ]})


site.register_plugin(AggregationPlugin, ListAdminView)
