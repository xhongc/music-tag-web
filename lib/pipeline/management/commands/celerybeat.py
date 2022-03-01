"""

Start the celery clock service from the Django management command.

"""
from __future__ import absolute_import, unicode_literals

from optparse import make_option as Option

from celery.bin import beat

from pipeline.management.commands.app import app
from pipeline.management.commands.base import CeleryCommand

beat = beat.beat(app=app)


class Command(CeleryCommand):
    """Run the celery periodic task scheduler."""

    help = 'Old alias to the "celery beat" command.'
    options = (
        Option("-A", "--app", default=None),
        Option("--broker", default=None),
        Option("--loader", default=None),
        Option("--config", default=None),
        Option("--workdir", default=None, dest="working_directory"),
        Option("--result-backend", default=None),
        Option("--no-color", "-C", action="store_true", default=None),
        Option("--quiet", "-q", action="store_true"),
    )
    if beat.get_options() is not None:
        options = options + CeleryCommand.options + beat.get_options()

    def handle(self, *args, **options):
        beat.run(*args, **options)
