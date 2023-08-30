import django_filters


class TaskFilters(django_filters.FilterSet):
    state = django_filters.CharFilter(lookup_expr="iexact")
