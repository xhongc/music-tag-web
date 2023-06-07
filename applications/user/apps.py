from django.apps import AppConfig


class UserConfig(AppConfig):
    name = 'applications.user'
    managed = True
    verbose_name = 'Subsonic用户'
    verbose_name_plural = 'Subsonic用户'
