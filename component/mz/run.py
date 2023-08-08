import os
import sys

from django.conf import settings

if sys.platform == 'darwin':
    os.environ["FPCALC"] = os.path.join(settings.BASE_DIR, "component", "mz", "fpcalc")
else:
    os.environ["FPCALC"] = os.path.join(settings.BASE_DIR, "component", "mz", "fpcalc_linux")

from component.mz import acoustid

apikey = "cSpUJKpD"


def get_acoustid(path):
    try:
        return acoustid.match(apikey, path)
    except Exception:
        return ""
