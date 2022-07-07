from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"^task", views.TaskViewSets, base_name='task')

