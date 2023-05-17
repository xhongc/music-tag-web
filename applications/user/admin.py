# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subsonic_api_token')
    list_filter = ('user',)
