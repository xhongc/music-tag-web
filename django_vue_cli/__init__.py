from __future__ import absolute_import

from component.mysql_pool import patch_mysql
from .celery_app import app as current_app

__all__ = ('current_app',)
patch_mysql()