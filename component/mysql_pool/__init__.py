# -*- coding: utf-8 -*-
"""
猴子补丁实现django中mysql线程池
"""

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from sqlalchemy import event, exc
from sqlalchemy.pool import Pool, manage

# POOL_PESSIMISTIC_MODE为True表示每次复用连接池都检查一下连接状态
POOL_PESSIMISTIC_MODE = getattr(settings, "DJORM_POOL_PESSIMISTIC", False)

POOL_SETTINGS = getattr(settings, "DJORM_POOL_OPTIONS", {})
POOL_SETTINGS.setdefault("recycle", 3600)


@event.listens_for(Pool, "checkout")
def _on_checkout(dbapi_connection, connection_record, connection_proxy):
    if POOL_PESSIMISTIC_MODE:
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("SELECT 1")
        except Exception:
            # raise DisconnectionError - pool will try
            # connecting again up to three times before raising.
            raise exc.DisconnectionError()
        finally:
            cursor.close()


@event.listens_for(Pool, "checkin")
def _on_checkin(*args, **kwargs):
    pass


@event.listens_for(Pool, "connect")
def _on_connect(*args, **kwargs):
    pass


def patch_mysql():
    class HashableDict(dict):
        def __hash__(self):
            return hash(frozenset(self))

    class HashableList(list):
        def __hash__(self):
            return hash(tuple(sorted(self)))

    class ManagerProxy(object):
        def __init__(self, manager):
            self.manager = manager

        def __getattr__(self, key):
            return getattr(self.manager, key)

        def connect(self, *args, **kwargs):
            if "conv" in kwargs:
                conv = kwargs["conv"]
                if isinstance(conv, dict):
                    items = []
                    for k, v in conv.items():
                        if isinstance(v, list):
                            v = HashableList(v)
                        items.append((k, v))
                    kwargs["conv"] = HashableDict(items)
            if "ssl" in kwargs:
                ssl = kwargs["ssl"]
                if isinstance(ssl, dict):
                    items = []
                    for k, v in ssl.items():
                        if isinstance(v, list):
                            v = HashableList(v)
                        items.append((k, v))
                    kwargs["ssl"] = HashableDict(items)
            return self.manager.connect(*args, **kwargs)

    try:
        from django.db.backends.mysql import base as mysql_base
    except (ImproperlyConfigured, ImportError) as e:
        return

    if not hasattr(mysql_base, "_Database"):
        mysql_base._Database = mysql_base.Database
        mysql_base.Database = ManagerProxy(manage(mysql_base._Database, **POOL_SETTINGS))
