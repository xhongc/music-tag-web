from __future__ import absolute_import

from .celery_app import app as current_app

__all__ = ('current_app',)