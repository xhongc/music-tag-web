def init_task(sender, **kwargs):
    from django.contrib.auth.models import User
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@qq.com", "admin")
