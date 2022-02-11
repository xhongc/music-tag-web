import django_filters as filters


class NodeTemplateFilter(filters.FilterSet):
    template_type = filters.CharFilter(lookup_expr="iexact")
