# -*- coding: utf-8 -*-
from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    """
    自定义分页格式，综合页码和url
    """

    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 10000

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("page", self.page.number),
                    ("total_page", self.page.paginator.num_pages),
                    ("count", self.page.paginator.count),
                    ("items", data),
                ]
            )
        )

    def get_paginated_data(self, data):
        return OrderedDict(
            [
                ("page", self.page.number),
                ("total_page", self.page.paginator.num_pages),
                ("count", self.page.paginator.count),
                ("items", data),
            ]
        )
