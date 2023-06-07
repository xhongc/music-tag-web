from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django_vue_cli.views import index
from applications.task.urls import router as task_router
from applications.user.urls import router as user_router
from applications.subsonic.urls import router as subsonic_router
from django.views import static
from rest_framework_jwt.views import obtain_jwt_token

admin.site.site_header = "音乐管理系统"
admin.site.site_title = "音乐管理系统 ｜ Music Tag"
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    re_path(r"^api/", include(task_router.urls)),
    re_path(r"^rest/", include(subsonic_router.urls)),
    re_path(r"^user/", include(user_router.urls)),
    re_path(r'^api/token/', obtain_jwt_token),
    # nginx 处理了静态文件
    re_path(r'^static/(?P<path>.*)$', static.serve,
            {'document_root': settings.STATIC_ROOT}, name='static'),
    re_path(r'^media/(?P<path>.*)$', static.serve, {'document_root': settings.MEDIA_ROOT}),
]
