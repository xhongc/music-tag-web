from django.db import models


class Task(models.Model):
    name = models.CharField(max_length=255)
