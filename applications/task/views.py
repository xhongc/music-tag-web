from django.shortcuts import render

from applications.task.models import Task
from applications.task.serializers import TaskSerializer
from component.drf.viewsets import GenericViewSet
from rest_framework import mixins


class TaskViewSets(mixins.ListModelMixin,
                   GenericViewSet):
    queryset = Task.objects.order_by("-id")
    serializer_class = TaskSerializer
