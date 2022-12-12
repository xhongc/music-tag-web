from rest_framework.decorators import action
from rest_framework.response import Response

from component.drf.viewsets import GenericViewSet


class UserViewSets(GenericViewSet):
    @action(methods=['GET'], detail=False)
    def info(self, request, *args, **kwargs):
        return Response({
            "username": request.user.username,
            "role": "admin" if request.user.is_superuser else "other"
        })
