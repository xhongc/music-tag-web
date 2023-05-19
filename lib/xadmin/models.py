import json
import django
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _, ugettext
from django.urls.base import reverse
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.base import ModelBase
from django.utils.encoding import python_2_unicode_compatible, smart_text

from django.db.models.signals import post_migrate
from django.contrib.auth.models import Permission

import datetime
import decimal
from xadmin.util import quote

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


def add_view_permissions(sender, **kwargs):
    """
    This syncdb hooks takes care of adding a view permission too all our
    content types.
    """
    # for each of our content types
    for content_type in ContentType.objects.all():
        # build our permission slug
        codename = "view_%s" % content_type.model

        # if it doesn't exist..
        if not Permission.objects.filter(content_type=content_type, codename=codename):
            # add it
            Permission.objects.create(content_type=content_type,
                                      codename=codename,
                                      name="Can view %s" % content_type.name)
            # print "Added view permission for %s" % content_type.name

# check for all our view permissions after a syncdb
post_migrate.connect(add_view_permissions)


@python_2_unicode_compatible
class Bookmark(models.Model):
    title = models.CharField(_(u'Title'), max_length=128)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_(u"user"), blank=True, null=True)
    url_name = models.CharField(_(u'Url Name'), max_length=64)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    query = models.CharField(_(u'Query String'), max_length=1000, blank=True)
    is_share = models.BooleanField(_(u'Is Shared'), default=False)

    @property
    def url(self):
        base_url = reverse(self.url_name)
        if self.query:
            base_url = base_url + '?' + self.query
        return base_url

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _(u'Bookmark')
        verbose_name_plural = _('Bookmarks')


class JSONEncoder(DjangoJSONEncoder):

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, datetime.date):
            return o.strftime('%Y-%m-%d')
        elif isinstance(o, decimal.Decimal):
            return str(o)
        elif isinstance(o, ModelBase):
            return '%s.%s' % (o._meta.app_label, o._meta.model_name)
        else:
            try:
                return super(JSONEncoder, self).default(o)
            except Exception:
                return smart_text(o)


@python_2_unicode_compatible
class UserSettings(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_(u"user"))
    key = models.CharField(_('Settings Key'), max_length=256)
    value = models.TextField(_('Settings Content'))

    def json_value(self):
        return json.loads(self.value)

    def set_json(self, obj):
        self.value = json.dumps(obj, cls=JSONEncoder, ensure_ascii=False)

    def __str__(self):
        return "%s %s" % (self.user, self.key)

    class Meta:
        verbose_name = _(u'User Setting')
        verbose_name_plural = _('User Settings')


@python_2_unicode_compatible
class UserWidget(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_(u"user"))
    page_id = models.CharField(_(u"Page"), max_length=256)
    widget_type = models.CharField(_(u"Widget Type"), max_length=50)
    value = models.TextField(_(u"Widget Params"))

    def get_value(self):
        value = json.loads(self.value)
        value['id'] = self.id
        value['type'] = self.widget_type
        return value

    def set_value(self, obj):
        self.value = json.dumps(obj, cls=JSONEncoder, ensure_ascii=False)

    def save(self, *args, **kwargs):
        created = self.pk is None
        super(UserWidget, self).save(*args, **kwargs)
        if created:
            try:
                portal_pos = UserSettings.objects.get(
                    user=self.user, key="dashboard:%s:pos" % self.page_id)
                portal_pos.value = "%s,%s" % (self.pk, portal_pos.value) if portal_pos.value else self.pk
                portal_pos.save()
            except Exception:
                pass

    def __str__(self):
        return "%s %s widget" % (self.user, self.widget_type)

    class Meta:
        verbose_name = _(u'User Widget')
        verbose_name_plural = _('User Widgets')


@python_2_unicode_compatible
class Log(models.Model):
    action_time = models.DateTimeField(
        _('action time'),
        default=timezone.now,
        editable=False,
    )
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        models.CASCADE,
        verbose_name=_('user'),
    )
    ip_addr = models.GenericIPAddressField(_('action ip'), blank=True, null=True)
    content_type = models.ForeignKey(
        ContentType,
        models.SET_NULL,
        verbose_name=_('content type'),
        blank=True, null=True,
    )
    object_id = models.TextField(_('object id'), blank=True, null=True)
    object_repr = models.CharField(_('object repr'), max_length=200)
    action_flag = models.CharField(_('action flag'), max_length=32)
    message = models.TextField(_('change message'), blank=True)

    class Meta:
        verbose_name = _('log entry')
        verbose_name_plural = _('log entries')
        ordering = ('-action_time',)

    def __repr__(self):
        return smart_text(self.action_time)

    def __str__(self):
        if self.action_flag == 'create':
            return ugettext('Added "%(object)s".') % {'object': self.object_repr}
        elif self.action_flag == 'change':
            return ugettext('Changed "%(object)s" - %(changes)s') % {
                'object': self.object_repr,
                'changes': self.message,
            }
        elif self.action_flag == 'delete' and self.object_repr:
            return ugettext('Deleted "%(object)s."') % {'object': self.object_repr}

        return self.message

    def get_edited_object(self):
        "Returns the edited object represented by this log entry"
        return self.content_type.get_object_for_this_type(pk=self.object_id)
