from rest_framework import mixins, status
from rest_framework.response import Response

from component.drf.viewsets import GenericViewSet


class TaskViewSets(mixins.ListModelMixin, GenericViewSet):
    def list(self, request, *args, **kwargs):
        return Response({})
