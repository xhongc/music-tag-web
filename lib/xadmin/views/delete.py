from django.core.exceptions import PermissionDenied
from django.db import transaction, router
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django import VERSION as django_version
from django.utils import six
from django.utils.encoding import force_text
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.contrib.admin.utils import get_deleted_objects

from xadmin.util import unquote
from xadmin.views.edit import UpdateAdminView
from xadmin.views.detail import DetailAdminView
from xadmin.views.base import ModelAdminView, filter_hook, csrf_protect_m


class DeleteAdminView(ModelAdminView):
    delete_confirmation_template = None

    def __init__(self, request, *args, **kwargs):
        if django_version > (2, 0):
            for model in self.admin_site._registry:
                if not hasattr(self.admin_site._registry[model], 'has_delete_permission'):
                    setattr(self.admin_site._registry[model], 'has_delete_permission', self.has_delete_permission)
        super(DeleteAdminView, self).__init__(request, *args, **kwargs)

    def init_request(self, object_id, *args, **kwargs):
        "The 'delete' admin view for this model."
        self.obj = self.get_object(unquote(object_id))

        if not self.has_delete_permission(self.obj):
            raise PermissionDenied

        if self.obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_text(self.opts.verbose_name), 'key': escape(object_id)})

        using = router.db_for_write(self.model)

        # Populate deleted_objects, a data structure of all related objects that
        # will also be deleted.
        if django_version > (2, 1):
            (self.deleted_objects, model_count, self.perms_needed, self.protected) = get_deleted_objects(
                [self.obj], self.opts, self.admin_site)
        else:
            (self.deleted_objects, model_count, self.perms_needed, self.protected) = get_deleted_objects(
                [self.obj], self.opts, self.request.user, self.admin_site, using)

    @csrf_protect_m
    @filter_hook
    def get(self, request, object_id):
        context = self.get_context()

        return TemplateResponse(request, self.delete_confirmation_template or
                                self.get_template_list("views/model_delete_confirm.html"), context)

    @csrf_protect_m
    @transaction.atomic
    @filter_hook
    def post(self, request, object_id):
        if self.perms_needed:
            raise PermissionDenied

        self.delete_model()

        response = self.post_response()
        cls_str = str if six.PY3 else basestring
        if isinstance(response, cls_str):
            response = HttpResponseRedirect(response)
        return response

    @filter_hook
    def delete_model(self):
        """
        Given a model instance delete it from the database.
        """
        self.log('delete', '', self.obj)
        self.obj.delete()

    @filter_hook
    def get_context(self):
        if self.perms_needed or self.protected:
            title = _("Cannot delete %(name)s") % {"name":
                                                   force_text(self.opts.verbose_name)}
        else:
            title = _("Are you sure?")

        new_context = {
            "title": title,
            "object": self.obj,
            "deleted_objects": self.deleted_objects,
            "perms_lacking": self.perms_needed,
            "protected": self.protected,
        }
        context = super(DeleteAdminView, self).get_context()
        context.update(new_context)
        return context

    @filter_hook
    def get_breadcrumb(self):
        bcs = super(DeleteAdminView, self).get_breadcrumb()
        bcs.append({
            'title': force_text(self.obj),
            'url': self.get_object_url(self.obj)
        })
        item = {'title': _('Delete')}
        if self.has_delete_permission():
            item['url'] = self.model_admin_url('delete', self.obj.pk)
        bcs.append(item)

        return bcs

    @filter_hook
    def post_response(self):

        self.message_user(_('The %(name)s "%(obj)s" was deleted successfully.') %
                          {'name': force_text(self.opts.verbose_name), 'obj': force_text(self.obj)}, 'success')

        if not self.has_view_permission():
            return self.get_admin_url('index')
        return self.model_admin_url('changelist')
