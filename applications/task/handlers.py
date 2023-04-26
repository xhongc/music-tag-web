def init_task(sender, **kwargs):
    from django.contrib.auth.models import User
    from applications.user.models import UserProfile
    import os
    from django.conf import settings

    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@qq.com", "admin")

    UserProfile.objects.get_or_create(user=User.objects.get(username="admin"))
    music_folder = os.path.join(settings.MEDIA_ROOT, "music")
    os.makedirs(music_folder, exist_ok=True)
