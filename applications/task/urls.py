from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"", views.TaskViewSets, base_name='task')
router.register(r"record", views.TaskModelViewSets, base_name='record')

