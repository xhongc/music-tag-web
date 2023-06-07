from django.apps import AppConfig


class MusicConfig(AppConfig):
    name = 'applications.music'
    managed = True
    verbose_name = '音乐管理'
    verbose_name_plural = '音乐管理'
