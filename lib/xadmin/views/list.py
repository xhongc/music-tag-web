from __future__ import absolute_import
from collections import OrderedDict
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.core.paginator import InvalidPage, Paginator
from django.urls.base import NoReverseMatch
from django.db import models
from django.http import HttpResponseRedirect
from django.template.response import SimpleTemplateResponse, TemplateResponse
from django.utils import six
from django.utils.encoding import force_text, smart_text
from django.utils.html import escape, conditional_escape
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.translation import ugettext as _

from xadmin.util import lookup_field, display_for_field, label_for_field, boolean_icon

from .base import ModelAdminView, filter_hook, inclusion_tag, csrf_protect_m

# List settings
ALL_VAR = 'all'
ORDER_VAR = 'o'
PAGE_VAR = 'p'
TO_FIELD_VAR = 't'
COL_LIST_VAR = '_cols'
ERROR_FLAG = 'e'

DOT = '.'

# Text to display within change-list table cells if the value is blank.
EMPTY_CHANGELIST_VALUE = _('Null')


class FakeMethodField(object):
    """
    This class used when a column is an model function, wrap function as a fake field to display in select columns.
    """

    def __init__(self, name, verbose_name):
        # Initial comm field attrs
        self.name = name
        self.verbose_name = verbose_name
        self.primary_key = False


class ResultRow(dict):
    pass


class ResultItem(object):

    def __init__(self, field_name, row):
        self.classes = []
        self.text = '&nbsp;'
        self.wraps = []
        self.tag = 'td'
        self.tag_attrs = []
        self.allow_tags = False
        self.btns = []
        self.menus = []
        self.is_display_link = False
        self.row = row
        self.field_name = field_name
        self.field = None
        self.attr = None
        self.value = None

    @property
    def label(self):
        text = mark_safe(
            self.text) if self.allow_tags else conditional_escape(self.text)
        if force_text(text) == '':
            text = mark_safe('&nbsp;')
        for wrap in self.wraps:
            text = mark_safe(wrap % text)
        return text

    @property
    def tagattrs(self):
        return mark_safe(
            '%s%s' % ((self.tag_attrs and ' '.join(self.tag_attrs) or ''),
                      (self.classes and (' class="%s"' % ' '.join(self.classes)) or '')))


class ResultHeader(ResultItem):

    def __init__(self, field_name, row):
        super(ResultHeader, self).__init__(field_name, row)
        self.tag = 'th'
        self.tag_attrs = ['scope="col"']
        self.sortable = False
        self.allow_tags = True
        self.sorted = False
        self.ascending = None
        self.sort_priority = None
        self.url_primary = None
        self.url_remove = None
        self.url_toggle = None


class ListAdminView(ModelAdminView):
    """
    Display models objects view. this class has ordering and simple filter features.
    """
    list_display = ('__str__',)
    list_display_links = ()
    list_display_links_details = False
    list_select_related = None
    list_per_page = 50
    list_max_show_all = 200
    list_exclude = ()
    search_fields = ()
    paginator_class = Paginator
    ordering = None

    # Change list templates
    object_list_template = None

    def init_request(self, *args, **kwargs):

        if not self.has_view_permission():
            raise PermissionDenied

        request = self.request
        request.session['LIST_QUERY'] = (self.model_info, self.request.META['QUERY_STRING'])

        self.pk_attname = self.opts.pk.attname
        self.lookup_opts = self.opts
        self.list_display = self.get_list_display()
        self.list_display_links = self.get_list_display_links()

        # Get page number parameters from the query string.
        try:
            self.page_num = int(request.GET.get(PAGE_VAR, 0))
        except ValueError:
            self.page_num = 0

        # Get params from request
        self.show_all = ALL_VAR in request.GET
        self.to_field = request.GET.get(TO_FIELD_VAR)
        self.params = dict(request.GET.items())

        if PAGE_VAR in self.params:
            del self.params[PAGE_VAR]
        if ERROR_FLAG in self.params:
            del self.params[ERROR_FLAG]

    @filter_hook
    def get_list_display(self):
        """
        Return a sequence containing the fields to be displayed on the list.
        """
        self.base_list_display = (COL_LIST_VAR in self.request.GET and self.request.GET[COL_LIST_VAR] != "" and
                                  self.request.GET[COL_LIST_VAR].split('.')) or self.list_display
        return list(self.base_list_display)

    @filter_hook
    def get_list_display_links(self):
        """
        Return a sequence containing the fields to be displayed as links
        on the changelist. The list_display parameter is the list of fields
        returned by get_list_display().
        """
        if self.list_display_links or not self.list_display:
            return self.list_display_links
        else:
            # Use only the first item in list_display as link
            return list(self.list_display)[:1]

    def make_result_list(self):
        # Get search parameters from the query string.
        self.list_queryset = self.get_list_queryset()
        self.ordering_field_columns = self.get_ordering_field_columns()
        self.paginator = self.get_paginator()

        # Get the number of objects, with admin filters applied.
        self.result_count = self.paginator.count

        self.can_show_all = self.result_count <= self.list_max_show_all
        self.multi_page = self.result_count > self.list_per_page

        # Get the list of objects to display on this page.
        if (self.show_all and self.can_show_all) or not self.multi_page:
            self.result_list = self.list_queryset._clone()
        else:
            try:
                self.result_list = self.paginator.page(
                    self.page_num + 1).object_list
            except InvalidPage:
                if ERROR_FLAG in self.request.GET.keys():
                    return SimpleTemplateResponse('xadmin/views/invalid_setup.html', {
                        'title': _('Database error'),
                    })
                return HttpResponseRedirect(self.request.path + '?' + ERROR_FLAG + '=1')
        self.has_more = self.result_count > (
            self.list_per_page * self.page_num + len(self.result_list))

    @filter_hook
    def get_result_list(self):
        return self.make_result_list()

    @filter_hook
    def post_result_list(self):
        return self.make_result_list()

    @filter_hook
    def get_list_queryset(self):
        """
        Get model queryset. The query has been filted and ordered.
        """
        # First, get queryset from base class.
        queryset = self.queryset()

        # Use select_related() if one of the list_display options is a field
        # with a relationship and the provided queryset doesn't already have
        # select_related defined.
        if not queryset.query.select_related:
            if self.list_select_related:
                queryset = queryset.select_related()
            elif self.list_select_related is None:
                related_fields = []
                for field_name in self.list_display:
                    try:
                        field = self.opts.get_field(field_name)
                    except models.FieldDoesNotExist:
                        pass
                    else:
                        if isinstance(field.remote_field, models.ManyToOneRel):
                            related_fields.append(field_name)
                if related_fields:
                    queryset = queryset.select_related(*related_fields)
            else:
                pass

        # Then, set queryset ordering.
        queryset = queryset.order_by(*self.get_ordering())

        # Return the queryset.
        return queryset

    # List ordering
    def _get_default_ordering(self):
        ordering = []
        if self.ordering:
            ordering = self.ordering
        elif self.opts.ordering:
            ordering = self.opts.ordering
        return ordering

    @filter_hook
    def get_ordering_field(self, field_name):
        """
        Returns the proper model field name corresponding to the given
        field_name to use for ordering. field_name may either be the name of a
        proper model field or the name of a method (on the admin or model) or a
        callable with the 'admin_order_field' attribute. Returns None if no
        proper model field name can be matched.
        """
        try:
            field = self.opts.get_field(field_name)
            return field.name
        except models.FieldDoesNotExist:
            # See whether field_name is a name of a non-field
            # that allows sorting.
            if callable(field_name):
                attr = field_name
            elif hasattr(self, field_name):
                attr = getattr(self, field_name)
            else:
                attr = getattr(self.model, field_name)
            return getattr(attr, 'admin_order_field', None)

    @filter_hook
    def get_ordering(self):
        """
        Returns the list of ordering fields for the change list.
        First we check the get_ordering() method in model admin, then we check
        the object's default ordering. Then, any manually-specified ordering
        from the query string overrides anything. Finally, a deterministic
        order is guaranteed by ensuring the primary key is used as the last
        ordering field.
        """
        ordering = list(super(ListAdminView, self).get_ordering()
                        or self._get_default_ordering())
        if ORDER_VAR in self.params and self.params[ORDER_VAR]:
            # Clear ordering and used params
            ordering = [
                pfx + self.get_ordering_field(field_name)
                for n, pfx, field_name in map(
                    lambda p: p.rpartition('-'),
                    self.params[ORDER_VAR].split('.')
                )
                if self.get_ordering_field(field_name)
            ]

        # Ensure that the primary key is systematically present in the list of
        # ordering fields so we can guarantee a deterministic order across all
        # database backends.
        pk_name = self.opts.pk.name
        if not (set(ordering) & set(['pk', '-pk', pk_name, '-' + pk_name])):
            # The two sets do not intersect, meaning the pk isn't present. So
            # we add it.
            ordering.append('-pk')

        return ordering

    @filter_hook
    def get_ordering_field_columns(self):
        """
        Returns a OrderedDict of ordering field column numbers and asc/desc
        """

        # We must cope with more than one column having the same underlying sort
        # field, so we base things on column numbers.
        ordering = self._get_default_ordering()
        ordering_fields = OrderedDict()
        if ORDER_VAR not in self.params or not self.params[ORDER_VAR]:
            # for ordering specified on ModelAdmin or model Meta, we don't know
            # the right column numbers absolutely, because there might be more
            # than one column associated with that ordering, so we guess.
            for field in ordering:
                if field.startswith('-'):
                    field = field[1:]
                    order_type = 'desc'
                else:
                    order_type = 'asc'
                for attr in self.list_display:
                    if self.get_ordering_field(attr) == field:
                        ordering_fields[field] = order_type
                        break
        else:
            for p in self.params[ORDER_VAR].split('.'):
                none, pfx, field_name = p.rpartition('-')
                ordering_fields[field_name] = 'desc' if pfx == '-' else 'asc'
        return ordering_fields

    def get_check_field_url(self, f):
        """
        Return the select column menu items link.
        We must use base_list_display, because list_display maybe changed by plugins.
        """
        fields = [fd for fd in self.base_list_display if fd != f.name]
        if len(self.base_list_display) == len(fields):
            if f.primary_key:
                fields.insert(0, f.name)
            else:
                fields.append(f.name)
        return self.get_query_string({COL_LIST_VAR: '.'.join(fields)})

    def get_model_method_fields(self):
        """
        Return the fields info defined in model. use FakeMethodField class wrap method as a db field.
        """
        methods = []
        for name in dir(self):
            try:
                if getattr(getattr(self, name), 'is_column', False):
                    methods.append((name, getattr(self, name)))
            except:
                pass
        return [FakeMethodField(name, getattr(method, 'short_description', capfirst(name.replace('_', ' '))))
                for name, method in methods]

    @filter_hook
    def get_context(self):
        """
        Prepare the context for templates.
        """
        self.title = _('%s List') % force_text(self.opts.verbose_name)
        model_fields = [(f, f.name in self.list_display, self.get_check_field_url(f))
                        for f in (list(self.opts.fields) + self.get_model_method_fields()) if f.name not in self.list_exclude]

        new_context = {
            'model_name': force_text(self.opts.verbose_name_plural),
            'title': self.title,
            'cl': self,
            'model_fields': model_fields,
            'clean_select_field_url': self.get_query_string(remove=[COL_LIST_VAR]),
            'has_add_permission': self.has_add_permission(),
            'app_label': self.app_label,
            'brand_name': self.opts.verbose_name_plural,
            'brand_icon': self.get_model_icon(self.model),
            'add_url': self.model_admin_url('add'),
            'result_headers': self.result_headers(),
            'results': self.results()
        }
        context = super(ListAdminView, self).get_context()
        context.update(new_context)
        return context

    @filter_hook
    def get_response(self, context, *args, **kwargs):
        pass

    @csrf_protect_m
    @filter_hook
    def get(self, request, *args, **kwargs):
        """
        The 'change list' admin view for this model.
        """
        response = self.get_result_list()
        if response:
            return response

        context = self.get_context()
        context.update(kwargs or {})

        response = self.get_response(context, *args, **kwargs)
        return response or TemplateResponse(request, self.object_list_template or
                                            self.get_template_list('views/model_list.html'), context)

    @filter_hook
    def post_response(self, *args, **kwargs):
        pass

    @csrf_protect_m
    @filter_hook
    def post(self, request, *args, **kwargs):
        return self.post_result_list() or self.post_response(*args, **kwargs) or self.get(request, *args, **kwargs)

    @filter_hook
    def get_paginator(self):
        return self.paginator_class(self.list_queryset, self.list_per_page, 0, True)

    @filter_hook
    def get_page_number(self, i):
        if i == DOT:
            return mark_safe(u'<span class="dot-page">...</span> ')
        elif i == self.page_num:
            return mark_safe(u'<span class="this-page">%d</span> ' % (i + 1))
        else:
            return mark_safe(u'<a href="%s"%s>%d</a> ' % (escape(self.get_query_string({PAGE_VAR: i})), (i == self.paginator.num_pages - 1 and ' class="end"' or ''), i + 1))

    # Result List methods
    @filter_hook
    def result_header(self, field_name, row):
        ordering_field_columns = self.ordering_field_columns
        item = ResultHeader(field_name, row)
        text, attr = label_for_field(field_name, self.model,
                                     model_admin=self,
                                     return_attr=True
                                     )
        item.text = text
        item.attr = attr
        if attr and not getattr(attr, "admin_order_field", None):
            return item

        # OK, it is sortable if we got this far
        th_classes = ['sortable']
        order_type = ''
        new_order_type = 'desc'
        sort_priority = 0
        sorted = False
        # Is it currently being sorted on?
        if field_name in ordering_field_columns:
            sorted = True
            order_type = ordering_field_columns.get(field_name).lower()
            arr = ordering_field_columns.keys()
            if six.PY3:
                arr = list(arr)
            sort_priority = arr.index(field_name) + 1
            th_classes.append('sorted %sending' % order_type)
            new_order_type = {'asc': 'desc', 'desc': 'asc'}[order_type]

        # build new ordering param
        o_list_asc = []  # URL for making this field the primary sort
        o_list_desc = []  # URL for making this field the primary sort
        o_list_remove = []  # URL for removing this field from sort
        o_list_toggle = []  # URL for toggling order type for this field
        make_qs_param = lambda t, n: ('-' if t == 'desc' else '') + str(n)

        for j, ot in ordering_field_columns.items():
            if j == field_name:  # Same column
                param = make_qs_param(new_order_type, j)
                # We want clicking on this header to bring the ordering to the
                # front
                o_list_asc.insert(0, j)
                o_list_desc.insert(0, '-' + j)
                o_list_toggle.append(param)
                # o_list_remove - omit
            else:
                param = make_qs_param(ot, j)
                o_list_asc.append(param)
                o_list_desc.append(param)
                o_list_toggle.append(param)
                o_list_remove.append(param)

        if field_name not in ordering_field_columns:
            o_list_asc.insert(0, field_name)
            o_list_desc.insert(0, '-' + field_name)

        item.sorted = sorted
        item.sortable = True
        item.ascending = (order_type == "asc")
        item.sort_priority = sort_priority

        menus = [
            ('asc', o_list_asc, 'caret-up', _(u'Sort ASC')),
            ('desc', o_list_desc, 'caret-down', _(u'Sort DESC')),
        ]
        if sorted:
            row['num_sorted_fields'] = row['num_sorted_fields'] + 1
            menus.append((None, o_list_remove, 'times', _(u'Cancel Sort')))
            item.btns.append('<a class="toggle" href="%s"><i class="fa fa-%s"></i></a>' % (
                self.get_query_string({ORDER_VAR: '.'.join(o_list_toggle)}), 'sort-up' if order_type == "asc" else 'sort-down'))

        item.menus.extend(['<li%s><a href="%s" class="active"><i class="fa fa-%s"></i> %s</a></li>' %
                           (
                               (' class="active"' if sorted and order_type == i[
                                   0] else ''),
                               self.get_query_string({ORDER_VAR: '.'.join(i[1])}), i[2], i[3]) for i in menus])
        item.classes.extend(th_classes)

        return item

    @filter_hook
    def result_headers(self):
        """
        Generates the list column headers.
        """
        row = ResultRow()
        row['num_sorted_fields'] = 0
        row.cells = [self.result_header(
            field_name, row) for field_name in self.list_display]
        return row

    @filter_hook
    def result_item(self, obj, field_name, row):
        """
        Generates the actual list of data.
        """
        item = ResultItem(field_name, row)
        try:
            f, attr, value = lookup_field(field_name, obj, self)
        except (AttributeError, ObjectDoesNotExist, NoReverseMatch):
            item.text = mark_safe("<span class='text-muted'>%s</span>" % EMPTY_CHANGELIST_VALUE)
        else:
            if f is None:
                item.allow_tags = getattr(attr, 'allow_tags', False)
                boolean = getattr(attr, 'boolean', False)
                if boolean:
                    item.allow_tags = True
                    item.text = boolean_icon(value)
                else:
                    item.text = smart_text(value)
            else:
                if isinstance(f.remote_field, models.ManyToOneRel):
                    field_val = getattr(obj, f.name)
                    if field_val is None:
                        item.text = mark_safe("<span class='text-muted'>%s</span>" % EMPTY_CHANGELIST_VALUE)
                    else:
                        item.text = field_val
                else:
                    item.text = display_for_field(value, f)
                if isinstance(f, models.DateField)\
                    or isinstance(f, models.TimeField)\
                        or isinstance(f, models.ForeignKey):
                    item.classes.append('nowrap')

            item.field = f
            item.attr = attr
            item.value = value

        # If list_display_links not defined, add the link tag to the first field
        if (item.row['is_display_first'] and not self.list_display_links) \
                or field_name in self.list_display_links:
            item.row['is_display_first'] = False
            item.is_display_link = True
            if self.list_display_links_details:
                item_res_uri = self.model_admin_url("detail", getattr(obj, self.pk_attname))
                if item_res_uri:
                    if self.has_change_permission(obj):
                        edit_url = self.model_admin_url("change", getattr(obj, self.pk_attname))
                    else:
                        edit_url = ""
                    item.wraps.append('<a data-res-uri="%s" data-edit-uri="%s" class="details-handler" rel="tooltip" title="%s">%%s</a>'
                                      % (item_res_uri, edit_url, _(u'Details of %s') % str(obj)))
            else:
                url = self.url_for_result(obj)
                item.wraps.append(u'<a href="%s">%%s</a>' % url)

        return item

    @filter_hook
    def result_row(self, obj):
        row = ResultRow()
        row['is_display_first'] = True
        row['object'] = obj
        row.cells = [self.result_item(
            obj, field_name, row) for field_name in self.list_display]
        return row

    @filter_hook
    def results(self):
        results = []
        for obj in self.result_list:
            results.append(self.result_row(obj))
        return results

    @filter_hook
    def url_for_result(self, result):
        return self.get_object_url(result)

    # Media
    @filter_hook
    def get_media(self):
        media = super(ListAdminView, self).get_media() + self.vendor('xadmin.page.list.js', 'xadmin.page.form.js')
        if self.list_display_links_details:
            media += self.vendor('xadmin.plugin.details.js', 'xadmin.form.css')
        return media

    # Blocks
    @inclusion_tag('xadmin/includes/pagination.html')
    def block_pagination(self, context, nodes, page_type='normal'):
        """
        Generates the series of links to the pages in a paginated list.
        """
        paginator, page_num = self.paginator, self.page_num

        pagination_required = (
            not self.show_all or not self.can_show_all) and self.multi_page
        if not pagination_required:
            page_range = []
        else:
            ON_EACH_SIDE = {'normal': 5, 'small': 3}.get(page_type, 3)
            ON_ENDS = 2

            # If there are 10 or fewer pages, display links to every page.
            # Otherwise, do some fancy
            if paginator.num_pages <= 10:
                page_range = range(paginator.num_pages)
            else:
                # Insert "smart" pagination links, so that there are always ON_ENDS
                # links at either end of the list of pages, and there are always
                # ON_EACH_SIDE links at either end of the "current page" link.
                page_range = []
                if page_num > (ON_EACH_SIDE + ON_ENDS):
                    page_range.extend(range(0, ON_EACH_SIDE - 1))
                    page_range.append(DOT)
                    page_range.extend(
                        range(page_num - ON_EACH_SIDE, page_num + 1))
                else:
                    page_range.extend(range(0, page_num + 1))
                if page_num < (paginator.num_pages - ON_EACH_SIDE - ON_ENDS - 1):
                    page_range.extend(
                        range(page_num + 1, page_num + ON_EACH_SIDE + 1))
                    page_range.append(DOT)
                    page_range.extend(range(
                        paginator.num_pages - ON_ENDS, paginator.num_pages))
                else:
                    page_range.extend(range(page_num + 1, paginator.num_pages))

        need_show_all_link = self.can_show_all and not self.show_all and self.multi_page
        return {
            'cl': self,
            'pagination_required': pagination_required,
            'show_all_url': need_show_all_link and self.get_query_string({ALL_VAR: ''}),
            'page_range': map(self.get_page_number, page_range),
            'ALL_VAR': ALL_VAR,
            '1': 1,
        }
