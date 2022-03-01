# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from __future__ import absolute_import, unicode_literals

import os
import sys

import celery

try:
    import django_celery_beat
except ImportError:
    import djcelery

from kombu.utils.encoding import str_to_bytes
from django.core.management.base import BaseCommand

DB_SHARED_THREAD = """\
DatabaseWrapper objects created in a thread can only \
be used in that same thread.  The object with alias '{0}' \
was created in thread id {1} and this is thread id {2}.\
"""


def setenv(k, v):  # noqa
    os.environ[str_to_bytes(k)] = str_to_bytes(v)


def patch_thread_ident():
    # monkey patch django.
    # This patch make sure that we use real threads to get the ident which
    # is going to happen if we are using gevent or eventlet.
    # -- patch taken from gunicorn
    if getattr(patch_thread_ident, "called", False):
        return
    try:
        from django.db.backends.base.base import BaseDatabaseWrapper, DatabaseError

        if "validate_thread_sharing" in BaseDatabaseWrapper.__dict__:
            import threading

            _get_ident = threading.get_ident

            __old__init__ = BaseDatabaseWrapper.__init__

            def _init(self, *args, **kwargs):
                __old__init__(self, *args, **kwargs)
                self._thread_ident = _get_ident()

            def _validate_thread_sharing(self):
                if not self.allow_thread_sharing and self._thread_ident != _get_ident():
                    raise DatabaseError(DB_SHARED_THREAD % (self.alias, self._thread_ident, _get_ident()),)

            BaseDatabaseWrapper.__init__ = _init
            BaseDatabaseWrapper.validate_thread_sharing = _validate_thread_sharing

        patch_thread_ident.called = True
    except ImportError:
        pass


patch_thread_ident()


class CeleryCommand(BaseCommand):
    options = ()
    if hasattr(BaseCommand, "option_list"):
        options = BaseCommand.option_list
    else:

        def add_arguments(self, parser):
            option_typemap = {"string": str, "int": int, "float": float}
            for opt in self.option_list:
                option = {k: v for k, v in opt.__dict__.items() if v is not None}
                flags = option.get("_long_opts", []) + option.get("_short_opts", [])
                if option.get("default") == ("NO", "DEFAULT"):
                    option["default"] = None
                if option.get("nargs") == 1:
                    del option["nargs"]
                del option["_long_opts"]
                del option["_short_opts"]
                if "type" in option:
                    opttype = option["type"]
                    option["type"] = option_typemap.get(opttype, opttype)
                parser.add_argument(*flags, **option)

    skip_opts = ["--app", "--loader", "--config", "--no-color"]
    requires_system_checks = False
    keep_base_opts = False
    stdout, stderr = sys.stdout, sys.stderr

    def get_version(self):
        def get_version(self):
            try:
                version = "celery {c.__version__}\ndjango-celery-beat {d.__version__}".format(
                    c=celery, d=django_celery_beat,
                )
            except ImportError:
                version = "celery {c.__version__}\ndjango-celery {d.__version__}".format(c=celery, d=djcelery,)
            return version

    def execute(self, *args, **options):
        broker = options.get("broker")
        if broker:
            self.set_broker(broker)
        super(CeleryCommand, self).execute(*args, **options)

    def set_broker(self, broker):
        setenv("CELERY_BROKER_URL", broker)

    def run_from_argv(self, argv):
        self.handle_default_options(argv[2:])
        return super(CeleryCommand, self).run_from_argv(argv)

    def handle_default_options(self, argv):
        acc = []
        broker = None
        for i, arg in enumerate(argv):
            # --settings and --pythonpath are also handled
            # by BaseCommand.handle_default_options, but that is
            # called with the resulting options parsed by optparse.
            if "--settings=" in arg:
                _, settings_module = arg.split("=")
                setenv("DJANGO_SETTINGS_MODULE", settings_module)
            elif "--pythonpath=" in arg:
                _, pythonpath = arg.split("=")
                sys.path.insert(0, pythonpath)
            elif "--broker=" in arg:
                _, broker = arg.split("=")
            elif arg == "-b":
                broker = argv[i + 1]
            else:
                acc.append(arg)
        if broker:
            self.set_broker(broker)
        return argv if self.keep_base_opts else acc

    def die(self, msg):
        sys.stderr.write(msg)
        sys.stderr.write("\n")
        sys.exit()

    def _is_unwanted_option(self, option):
        return option._long_opts and option._long_opts[0] in self.skip_opts

    @property
    def option_list(self):
        return [x for x in self.options if not self._is_unwanted_option(x)]
