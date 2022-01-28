# -*- coding: utf-8 -*-

from rest_framework import filters


class OrderingFilter(filters.OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        orderings = self.get_ordering(request, queryset, view)

        if orderings:
            custom_ordering = self.get_custom_ordering(request, view, orderings)
            return queryset.extra(select=custom_ordering, order_by=orderings)

        return queryset

    @staticmethod
    def get_ordering_class(view):
        return getattr(view, "ordering_class", None)

    def get_custom_ordering(self, request, view, orderings):
        custom_ordering = {}
        ordering_class = self.get_ordering_class(view)

        # viewset whether to define ordering class
        if ordering_class:
            for index, order_name in enumerate(orderings):
                reverse = order_name.startswith("-")
                order_func = getattr(ordering_class, order_name.lstrip("-"), None)

                # ordering class whether to define order method, Note: method name cannot be the same as field name
                if order_func:
                    custom_order = order_func(reverse, request)
                    custom_order_name = order_name.lstrip("-")
                    custom_ordering.update({custom_order_name: custom_order})
                    orderings[index] = custom_order_name

        return custom_ordering
