from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    subsonic_api_token = models.CharField(blank=True, null=True, max_length=255)

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"
