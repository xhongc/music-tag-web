from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django_vue_cli.views import index
from applications.task.urls import router as task_router
from django.views import static
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    re_path(r"^api/", include(task_router.urls)),
    re_path(r'^api/token/', obtain_jwt_token),
    re_path(r'^static/(?P<path>.*)$', static.serve,
            {'document_root': settings.STATIC_ROOT}, name='static'),
]
