from django.contrib import admin
from django.urls import path, include
from django_vue_cli.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
]
