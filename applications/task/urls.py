from rest_framework.routers import DefaultRouter

from . import views

task_router = DefaultRouter()
task_router.register(r"task", viewset=views.TaskViewSets, base_name="task")
