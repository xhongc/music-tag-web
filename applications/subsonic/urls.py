from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"", views.SubsonicViewSet, base_name='subsonic')

