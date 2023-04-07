from django.apps import AppConfig
from django.db.models.signals import post_migrate

from applications.task.handlers import init_task


class ProjectConfig(AppConfig):
    name = 'applications.task'

    def ready(self):
        post_migrate.connect(init_task, self)
