import binascii
import hashlib

from django.contrib.auth.models import User
from rest_framework import authentication, exceptions
from django.contrib.auth import authenticate as django_authenticate

from applications.user.models import UserProfile


def get_token(salt, password):
    to_hash = password + salt
    h = hashlib.md5()
    h.update(to_hash.encode("utf-8"))
    return h.hexdigest()


def authenticate(username, password):
    try:
        if password.startswith("enc:"):
            password = password.replace("enc:", "", 1)
            password = binascii.unhexlify(password).decode("utf-8")

        user = django_authenticate(username=username, password=password)

    except (User.DoesNotExist, binascii.Error):
        raise exceptions.AuthenticationFailed("Wrong username or password.")

    return user, None


def authenticate_salt(username, salt, token):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise exceptions.AuthenticationFailed("Wrong username or password.")
    user_profile, _ = UserProfile.objects.get_or_create(user=user)
    try:
        expected = get_token(salt, user_profile.subsonic_api_token)
    except Exception:
        raise exceptions.AuthenticationFailed("请设置你的subsonic api token")
    if expected != token:
        raise exceptions.AuthenticationFailed("Wrong username or password.")
    return user, None


class SubsonicAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        data = request.GET or request.POST
        username = data.get("u")
        if not username:
            return None

        p = data.get("p")
        s = data.get("s")
        t = data.get("t")
        if not p and (not s or not t):
            raise exceptions.AuthenticationFailed("Missing credentials")

        if p:
            return authenticate(username, p)

        return authenticate_salt(username, s, t)
