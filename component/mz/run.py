import os

from django.conf import settings

os.environ["FPCALC"] = os.path.join(settings.BASE_DIR, "component", "mz", "fpcalc")
from component.mz import acoustid

apikey = "cSpUJKpD"


def get_acoustid(path):
    return acoustid.match(apikey, path)
