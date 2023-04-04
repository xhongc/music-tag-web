from django.db import models


class Music(models.Model):
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255, default="")
    album = models.CharField(max_length=255, default="")
    genre = models.CharField(max_length=255, default="")
    year = models.CharField(max_length=255, default="")
    lyrics = models.TextField(default="")
    comment = models.TextField(default="")
    fs_id = models.CharField(max_length=255, default="")
    path = models.TextField(default="")
    parent_path = models.CharField(max_length=255, default="")
    size = models.CharField(max_length=255, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
