from django.db import models


class Task(models.Model):
    full_path = models.CharField(max_length=255)
    state = models.CharField(max_length=255, default="wait")
    parent_path = models.CharField(max_length=255, default="")
    filename = models.CharField(max_length=255, default="")


class TaskRecord(models.Model):
    song_name = models.CharField(max_length=255, default="")
    artist_name = models.CharField(max_length=255, default="")
    full_path = models.CharField(max_length=255, default="")
    tag_source = models.CharField(max_length=255, default="")
    icon = models.CharField(max_length=255, default="icon-folder")
    state = models.CharField(max_length=255, default="wait")
    extra = models.TextField(default="")
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    batch = models.CharField(max_length=255, default="")
