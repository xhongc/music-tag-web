from __future__ import absolute_import
from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.template.loader import get_template
from django.template.context import Context
from django.utils import six
from django.utils.safestring import mark_safe
from django.utils.html import escape, format_html
from django.utils.text import Truncator
from django.core.cache import cache, caches

from xadmin.views.list import EMPTY_CHANGELIST_VALUE
from xadmin.util import is_related_field, is_related_field2
import datetime

FILTER_PREFIX = '_p_'
SEARCH_VAR = '_q_'

from .util import (get_model_from_relation,
                   reverse_field_path, get_limit_choices_to_from_path, prepare_lookup_value)


class BaseFilter(object):
    title = None
    template = 'xadmin/filters/list.html'

    @classmethod
    def test(cls, field, request, params, model, admin_view, field_path):
        pass

    def __init__(self, request, params, model, admin_view):
        self.used_params = {}
        self.request = request
        self.params = params
        self.model = model
        self.admin_view = admin_view

        if self.title is None:
            raise ImproperlyConfigured(
                "The filter '%s' does not specify "
                "a 'title'." % self.__class__.__name__)

    def query_string(self, new_params=None, remove=None):
        return self.admin_view.get_query_string(new_params, remove)

    def form_params(self):
        arr = map(lambda k: FILTER_PREFIX + k, self.used_params.keys())
        if six.PY3:
            arr = list(arr)
        return self.admin_view.get_form_params(remove=arr)

    def has_output(self):
        """
        Returns True if some choices would be output for this filter.
        """
        raise NotImplementedError

    @property
    def is_used(self):
        return len(self.used_params) > 0

    def do_filte(self, queryset):
        """
        Returns the filtered queryset.
        """
        raise NotImplementedError

    def get_context(self):
        return {'title': self.title, 'spec': self, 'form_params': self.form_params()}

    def __str__(self):
        tpl = get_template(self.template)
        return mark_safe(tpl.render(context=self.get_context()))


class FieldFilterManager(object):
    _field_list_filters = []
    _take_priority_index = 0

    def register(self, list_filter_class, take_priority=False):
        if take_priority:
            # This is to allow overriding the default filters for certain types
            # of fields with some custom filters. The first found in the list
            # is used in priority.
            self._field_list_filters.insert(
                self._take_priority_index, list_filter_class)
            self._take_priority_index += 1
        else:
            self._field_list_filters.append(list_filter_class)
        return list_filter_class

    def create(self, field, request, params, model, admin_view, field_path):
        for list_filter_class in self._field_list_filters:
            if not list_filter_class.test(field, request, params, model, admin_view, field_path):
                continue
            return list_filter_class(field, request, params,
                                     model, admin_view, field_path=field_path)

manager = FieldFilterManager()


class FieldFilter(BaseFilter):

    lookup_formats = {}

    def __init__(self, field, request, params, model, admin_view, field_path):
        self.field = field
        self.field_path = field_path
        self.title = getattr(field, 'verbose_name', field_path)
        self.context_params = {}

        super(FieldFilter, self).__init__(request, params, model, admin_view)

        for name, format in self.lookup_formats.items():
            p = format % field_path
            self.context_params["%s_name" % name] = FILTER_PREFIX + p
            if p in params:
                value = prepare_lookup_value(p, params.pop(p))
                self.used_params[p] = value
                self.context_params["%s_val" % name] = value
            else:
                self.context_params["%s_val" % name] = ''

        arr = map(
            lambda kv: setattr(self, 'lookup_' + kv[0], kv[1]),
            self.context_params.items()
        )
        if six.PY3:
            list(arr)

    def get_context(self):
        context = super(FieldFilter, self).get_context()
        context.update(self.context_params)
        obj = map(lambda k: FILTER_PREFIX + k, self.used_params.keys())
        if six.PY3:
            obj = list(obj)
        context['remove_url'] = self.query_string({}, obj)
        return context

    def has_output(self):
        return True

    def do_filte(self, queryset):
        return queryset.filter(**self.used_params)


class ListFieldFilter(FieldFilter):
    template = 'xadmin/filters/list.html'

    def get_context(self):
        context = super(ListFieldFilter, self).get_context()
        context['choices'] = list(self.choices())
        return context


@manager.register
class BooleanFieldListFilter(ListFieldFilter):
    lookup_formats = {'exact': '%s__exact', 'isnull': '%s__isnull'}

    @classmethod
    def test(cls, field, request, params, model, admin_view, field_path):
        return isinstance(field, (models.BooleanField, models.NullBooleanField))

    def choices(self):
        for lookup, title in (
                ('', _('All')),
                ('1', _('Yes')),
                ('0', _('No')),
        ):
            yield {
                'selected': (
                    self.lookup_exact_val == lookup
                    and not self.lookup_isnull_val
                ),
                'query_string': self.query_string(
                    {self.lookup_exact_name: lookup},
                    [self.lookup_isnull_name],
                ),
                'display': title,
            }
        if isinstance(self.field, models.NullBooleanField):
            yield {
                'selected': self.lookup_isnull_val == 'True',
                'query_string': self.query_string(
                    {self.lookup_isnull_name: 'True'},
                    [self.lookup_exact_name],
                ),
                'display': _('Unknown'),
            }


@manager.register
class ChoicesFieldListFilter(ListFieldFilter):
    lookup_formats = {'exact': '%s__exact'}

    @classmethod
    def test(cls, field, request, params, model, admin_view, field_path):
        return bool(field.choices)

    def choices(self):
        yield {
            'selected': self.lookup_exact_val is '',
            'query_string': self.query_string({}, [self.lookup_exact_name]),
            'display': _('All')
        }
        for lookup, title in self.field.flatchoices:
            yield {
                'selected': smart_text(lookup) == self.lookup_exact_val,
                'query_string': self.query_string({self.lookup_exact_name: lookup}),
                'display': title,
            }


@manager.register
class TextFieldListFilter(FieldFilter):
    template = 'xadmin/filters/char.html'
    lookup_formats = {'in': '%s__in', 'search': '%s__contains'}

    @classmethod
    def test(cls, field, request, params, model, admin_view, field_path):
        return (
            isinstance(field, models.CharField)
            and field.max_length > 20
            or isinstance(field, models.TextField)
        )


@manager.register
class NumberFieldListFilter(FieldFilter):
    template = 'xadmin/filters/number.html'
    lookup_formats = {'equal': '%s__exact', 'lt': '%s__lt', 'gt': '%s__gt',
                      'ne': '%s__ne', 'lte': '%s__lte', 'gte': '%s__gte',
                      }

    @classmethod
    def test(cls, field, request, params, model, admin_view, field_path):
        return isinstance(field, (models.DecimalField, models.FloatField, models.IntegerField))

    def do_filte(self, queryset):
        params = self.used_params.copy()
        ne_key = '%s__ne' % self.field_path
        if ne_key in params:
            queryset = queryset.exclude(
                **{self.field_path: params.pop(ne_key)})
        return queryset.filter(**params)


@manager.register
class DateFieldListFilter(ListFieldFilter):
    template = 'xadmin/filters/date.html'
    lookup_formats = {'since': '%s__gte', 'until': '%s__lt',
                      'year': '%s__year', 'month': '%s__month', 'day': '%s__day',
                      'isnull': '%s__isnull'}

    @classmethod
    def test(cls, field, request, params, model, admin_view, field_path):
        return isinstance(field, models.DateField)

    def __init__(self, field, request, params, model, admin_view, field_path):
        self.field_generic = '%s__' % field_path
        self.date_params = dict([(FILTER_PREFIX + k, v) for k, v in params.items()
                                 if k.startswith(self.field_generic)])

        super(DateFieldListFilter, self).__init__(
            field, request, params, model, admin_view, field_path)

        now = timezone.now()
        # When time zone support is enabled, convert "now" to the user's time
        # zone so Django's definition of "Today" matches what the user expects.
        if now.tzinfo is not None:
            current_tz = timezone.get_current_timezone()
            now = now.astimezone(current_tz)
            if hasattr(current_tz, 'normalize'):
                # available for pytz time zones
                now = current_tz.normalize(now)

        if isinstance(field, models.DateTimeField):
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        else:       # field is a models.DateField
            today = now.date()
        tomorrow = today + datetime.timedelta(days=1)

        self.links = (
            (_('Any date'), {}),
            (_('Has date'), {
                self.lookup_isnull_name: False
            }),
            (_('Has no date'), {
                self.lookup_isnull_name: 'True'
            }),
            (_('Today'), {
                self.lookup_since_name: str(today),
                self.lookup_until_name: str(tomorrow),
            }),
            (_('Past 7 days'), {
                self.lookup_since_name: str(today - datetime.timedelta(days=7)),
                self.lookup_until_name: str(tomorrow),
            }),
            (_('This month'), {
                self.lookup_since_name: str(today.replace(day=1)),
                self.lookup_until_name: str(tomorrow),
            }),
            (_('This year'), {
                self.lookup_since_name: str(today.replace(month=1, day=1)),
                self.lookup_until_name: str(tomorrow),
            }),
        )

    def get_context(self):
        context = super(DateFieldListFilter, self).get_context()
        context['choice_selected'] = bool(self.lookup_year_val) or bool(self.lookup_month_val) \
            or bool(self.lookup_day_val)
        return context

    def choices(self):
        for title, param_dict in self.links:
            yield {
                'selected': self.date_params == param_dict,
                'query_string': self.query_string(
                    param_dict, [FILTER_PREFIX + self.field_generic]),
                'display': title,
            }


@manager.register
class RelatedFieldSearchFilter(FieldFilter):
    template = 'xadmin/filters/fk_search.html'

    @classmethod
    def test(cls, field, request, params, model, admin_view, field_path):
        if not is_related_field2(field):
            return False
        related_modeladmin = admin_view.admin_site._registry.get(
            get_model_from_relation(field))
        return related_modeladmin and getattr(related_modeladmin, 'relfield_style', None) in ('fk-ajax', 'fk-select')

    def __init__(self, field, request, params, model, model_admin, field_path):
        other_model = get_model_from_relation(field)
        if hasattr(field, 'remote_field'):
            rel_name = field.remote_field.get_related_field().name
        else:
            rel_name = other_model._meta.pk.name

        self.lookup_formats = {'in': '%%s__%s__in' % rel_name, 'exact': '%%s__%s__exact' % rel_name}
        super(RelatedFieldSearchFilter, self).__init__(
            field, request, params, model, model_admin, field_path)

        related_modeladmin = self.admin_view.admin_site._registry.get(other_model)
        self.relfield_style = related_modeladmin.relfield_style

        if hasattr(field, 'verbose_name'):
            self.lookup_title = field.verbose_name
        else:
            self.lookup_title = other_model._meta.verbose_name
        self.title = self.lookup_title
        self.search_url = model_admin.get_admin_url('%s_%s_changelist' % (
            other_model._meta.app_label, other_model._meta.model_name))
        self.label = self.label_for_value(other_model, rel_name, self.lookup_exact_val) if self.lookup_exact_val else ""
        self.choices = '?'
        if field.remote_field.limit_choices_to:
            for i in list(field.remote_field.limit_choices_to):
                self.choices += "&_p_%s=%s" % (i, field.remote_field.limit_choices_to[i])
            self.choices = format_html(self.choices)

    def label_for_value(self, other_model, rel_name, value):
        try:
            obj = other_model._default_manager.get(**{rel_name: value})
            return '%s' % escape(Truncator(obj).words(14, truncate='...'))
        except (ValueError, other_model.DoesNotExist):
            return ""

    def get_context(self):
        context = super(RelatedFieldSearchFilter, self).get_context()
        context['search_url'] = self.search_url
        context['label'] = self.label
        context['choices'] = self.choices
        context['relfield_style'] = self.relfield_style
        return context


@manager.register
class RelatedFieldListFilter(ListFieldFilter):

    @classmethod
    def test(cls, field, request, params, model, admin_view, field_path):
        return is_related_field2(field)

    def __init__(self, field, request, params, model, model_admin, field_path):
        other_model = get_model_from_relation(field)
        if hasattr(field, 'remote_field'):
            rel_name = field.remote_field.get_related_field().name
        else:
            rel_name = other_model._meta.pk.name

        self.lookup_formats = {'in': '%%s__%s__in' % rel_name, 'exact': '%%s__%s__exact' %
                               rel_name, 'isnull': '%s__isnull'}
        self.lookup_choices = field.get_choices(include_blank=False)
        super(RelatedFieldListFilter, self).__init__(
            field, request, params, model, model_admin, field_path)

        if hasattr(field, 'verbose_name'):
            self.lookup_title = field.verbose_name
        else:
            self.lookup_title = other_model._meta.verbose_name
        self.title = self.lookup_title

    def has_output(self):
        if (is_related_field(self.field)
                and self.field.field.null or hasattr(self.field, 'remote_field')
                and self.field.null):
            extra = 1
        else:
            extra = 0
        return len(self.lookup_choices) + extra > 1

    def expected_parameters(self):
        return [self.lookup_kwarg, self.lookup_kwarg_isnull]

    def choices(self):
        yield {
            'selected': self.lookup_exact_val == '' and not self.lookup_isnull_val,
            'query_string': self.query_string({},
                                              [self.lookup_exact_name, self.lookup_isnull_name]),
            'display': _('All'),
        }
        for pk_val, val in self.lookup_choices:
            yield {
                'selected': self.lookup_exact_val == smart_text(pk_val),
                'query_string': self.query_string({
                    self.lookup_exact_name: pk_val,
                }, [self.lookup_isnull_name]),
                'display': val,
            }
        if (is_related_field(self.field)
                and self.field.field.null or hasattr(self.field, 'remote_field')
                and self.field.null):
            yield {
                'selected': bool(self.lookup_isnull_val),
                'query_string': self.query_string({
                    self.lookup_isnull_name: 'True',
                }, [self.lookup_exact_name]),
                'display': EMPTY_CHANGELIST_VALUE,
            }


@manager.register
class MultiSelectFieldListFilter(ListFieldFilter):
    """ Delegates the filter to the default filter and ors the results of each

    Lists the distinct values of each field as a checkbox
    Uses the default spec for each 

    """
    template = 'xadmin/filters/checklist.html'
    lookup_formats = {'in': '%s__in'}
    cache_config = {'enabled': False, 'key': 'quickfilter_%s', 'timeout': 3600, 'cache': 'default'}

    @classmethod
    def test(cls, field, request, params, model, admin_view, field_path):
        return True

    def get_cached_choices(self):
        if not self.cache_config['enabled']:
            return None
        c = caches(self.cache_config['cache'])
        return c.get(self.cache_config['key'] % self.field_path)

    def set_cached_choices(self, choices):
        if not self.cache_config['enabled']:
            return
        c = caches(self.cache_config['cache'])
        return c.set(self.cache_config['key'] % self.field_path, choices)

    def __init__(self, field, request, params, model, model_admin, field_path, field_order_by=None, field_limit=None, sort_key=None, cache_config=None):
        super(MultiSelectFieldListFilter, self).__init__(field, request, params, model, model_admin, field_path)

        # Check for it in the cachce
        if cache_config is not None and type(cache_config) == dict:
            self.cache_config.update(cache_config)

        if self.cache_config['enabled']:
            self.field_path = field_path
            choices = self.get_cached_choices()
            if choices:
                self.lookup_choices = choices
                return

        # Else rebuild it
        queryset = self.admin_view.queryset().exclude(**{"%s__isnull" % field_path: True}).values_list(field_path, flat=True).distinct()
        #queryset = self.admin_view.queryset().distinct(field_path).exclude(**{"%s__isnull"%field_path:True})

        if field_order_by is not None:
            # Do a subquery to order the distinct set
            queryset = self.admin_view.queryset().filter(id__in=queryset).order_by(field_order_by)

        if field_limit is not None and type(field_limit) == int and queryset.count() > field_limit:
            queryset = queryset[:field_limit]

        self.lookup_choices = [str(it) for it in queryset.values_list(field_path, flat=True) if str(it).strip() != ""]
        if sort_key is not None:
            self.lookup_choices = sorted(self.lookup_choices, key=sort_key)

        if self.cache_config['enabled']:
            self.set_cached_choices(self.lookup_choices)

    def choices(self):
        self.lookup_in_val = (type(self.lookup_in_val) in (tuple, list)) and self.lookup_in_val or list(self.lookup_in_val)
        yield {
            'selected': len(self.lookup_in_val) == 0,
            'query_string': self.query_string({}, [self.lookup_in_name]),
            'display': _('All'),
        }
        for val in self.lookup_choices:
            yield {
                'selected': smart_text(val) in self.lookup_in_val,
                'query_string': self.query_string({self.lookup_in_name: ",".join([val] + self.lookup_in_val), }),
                'remove_query_string': self.query_string({self.lookup_in_name: ",".join([v for v in self.lookup_in_val if v != val]), }),
                'display': val,
            }


@manager.register
class AllValuesFieldListFilter(ListFieldFilter):
    lookup_formats = {'exact': '%s__exact', 'isnull': '%s__isnull'}

    @classmethod
    def test(cls, field, request, params, model, admin_view, field_path):
        return True

    def __init__(self, field, request, params, model, admin_view, field_path):
        parent_model, reverse_path = reverse_field_path(model, field_path)
        queryset = parent_model._default_manager.all()
        # optional feature: limit choices base on existing relationships
        # queryset = queryset.complex_filter(
        #    {'%s__isnull' % reverse_path: False})
        limit_choices_to = get_limit_choices_to_from_path(model, field_path)
        queryset = queryset.filter(limit_choices_to)

        self.lookup_choices = (queryset
                               .distinct()
                               .order_by(field.name)
                               .values_list(field.name, flat=True))
        super(AllValuesFieldListFilter, self).__init__(
            field, request, params, model, admin_view, field_path)

    def choices(self):
        yield {
            'selected': (self.lookup_exact_val is '' and self.lookup_isnull_val is ''),
            'query_string': self.query_string({}, [self.lookup_exact_name, self.lookup_isnull_name]),
            'display': _('All'),
        }
        include_none = False
        for val in self.lookup_choices:
            if val is None:
                include_none = True
                continue
            val = smart_text(val)
            yield {
                'selected': self.lookup_exact_val == val,
                'query_string': self.query_string({self.lookup_exact_name: val},
                                                  [self.lookup_isnull_name]),
                'display': val,
            }
        if include_none:
            yield {
                'selected': bool(self.lookup_isnull_val),
                'query_string': self.query_string({self.lookup_isnull_name: 'True'},
                                                  [self.lookup_exact_name]),
                'display': EMPTY_CHANGELIST_VALUE,
            }
