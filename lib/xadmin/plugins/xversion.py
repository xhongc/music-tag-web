from crispy_forms.utils import TEMPLATE_PACK
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models.query import QuerySet
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils import six
from django.utils.encoding import force_text, smart_text
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.translation import ugettext as _
from xadmin.layout import Field, render_field
from xadmin.plugins.inline import Inline
from xadmin.plugins.actions import BaseActionView
from xadmin.plugins.inline import InlineModelAdmin
from xadmin.sites import site
from xadmin.util import unquote, quote, model_format_dict, is_related_field2
from xadmin.views import BaseAdminPlugin, ModelAdminView, CreateAdminView, UpdateAdminView, DetailAdminView, ModelFormAdminView, DeleteAdminView, ListAdminView
from xadmin.views.base import csrf_protect_m, filter_hook
from xadmin.views.detail import DetailAdminUtil
from reversion.models import Revision, Version
from reversion.revisions import is_active, register, is_registered, set_comment, create_revision, set_user
from contextlib import contextmanager
from functools import partial


def _autoregister(admin, model, follow=None):
    """Registers a model with reversion, if required."""
    if model._meta.proxy:
        raise RegistrationError("Proxy models cannot be used with django-reversion, register the parent class instead")
    if not is_registered(model):
        follow = follow or []
        for parent_cls, field in model._meta.parents.items():
            follow.append(field.name)
            _autoregister(admin, parent_cls)
        register(model, follow=follow, format=admin.reversion_format)


def _register_model(admin, model):
    if not hasattr(admin, 'reversion_format'):
        admin.reversion_format = 'json'

    if not is_registered(model):
        inline_fields = []
        for inline in getattr(admin, 'inlines', []):
            inline_model = inline.model
            if getattr(inline, 'generic_inline', False):
                ct_field = getattr(inline, 'ct_field', 'content_type')
                ct_fk_field = getattr(inline, 'ct_fk_field', 'object_id')
                for field in model._meta.many_to_many:
                    if isinstance(field, GenericRelation) \
                            and field.rel.to == inline_model \
                            and field.object_id_field_name == ct_fk_field \
                            and field.content_type_field_name == ct_field:
                        inline_fields.append(field.name)
                _autoregister(admin, inline_model)
            else:
                fk_name = getattr(inline, 'fk_name', None)
                if not fk_name:
                    for field in inline_model._meta.fields:
                        if isinstance(field, (models.ForeignKey, models.OneToOneField)) and issubclass(model, field.remote_field.model):
                            fk_name = field.name
                _autoregister(admin, inline_model, follow=[fk_name])
                if not inline_model._meta.get_field(fk_name).remote_field.is_hidden():
                    accessor = inline_model._meta.get_field(fk_name).remote_field.get_accessor_name()
                    inline_fields.append(accessor)
        _autoregister(admin, model, inline_fields)


def register_models(admin_site=None):
    if admin_site is None:
        admin_site = site

    for model, admin in admin_site._registry.items():
        if getattr(admin, 'reversion_enable', False):
            _register_model(admin, model)


@contextmanager
def do_create_revision(request):
    with create_revision():
        set_user(request.user)
        yield


class ReversionPlugin(BaseAdminPlugin):

    # The serialization format to use when registering models with reversion.
    reversion_format = "json"

    # Whether to ignore duplicate revision data.
    ignore_duplicate_revisions = False

    reversion_enable = False

    def init_request(self, *args, **kwargs):
        return self.reversion_enable

    def do_post(self, __):
        def _method():
            self.revision_context_manager.set_user(self.user)
            comment = ''
            admin_view = self.admin_view
            if isinstance(admin_view, CreateAdminView):
                comment = _(u"Initial version.")
            elif isinstance(admin_view, UpdateAdminView):
                comment = _(u"Change version.")
            elif isinstance(admin_view, RevisionView):
                comment = _(u"Revert version.")
            elif isinstance(admin_view, RecoverView):
                comment = _(u"Rercover version.")
            elif isinstance(admin_view, DeleteAdminView):
                comment = _(u"Deleted %(verbose_name)s.") % {
                    "verbose_name": self.opts.verbose_name}
            self.revision_context_manager.set_comment(comment)
            return __()
        return _method

    def post(self, __, request, *args, **kwargs):
        with do_create_revision(request):
            return __()

    # Block Views
    def block_top_toolbar(self, context, nodes):
        recoverlist_url = self.admin_view.model_admin_url('recoverlist')
        nodes.append(mark_safe('<div class="btn-group"><a class="btn btn-default btn-sm" href="%s"><i class="fa fa-trash-o"></i> %s</a></div>' % (recoverlist_url, _(u"Recover"))))

    def block_nav_toggles(self, context, nodes):
        obj = getattr(
            self.admin_view, 'org_obj', getattr(self.admin_view, 'obj', None))
        if obj:
            revisionlist_url = self.admin_view.model_admin_url(
                'revisionlist', quote(obj.pk))
            nodes.append(mark_safe('<a href="%s" class="navbar-toggle pull-right"><i class="fa fa-calendar"></i></a>' % revisionlist_url))

    def block_nav_btns(self, context, nodes):
        obj = getattr(
            self.admin_view, 'org_obj', getattr(self.admin_view, 'obj', None))
        if obj:
            revisionlist_url = self.admin_view.model_admin_url(
                'revisionlist', quote(obj.pk))
            nodes.append(mark_safe('<a href="%s" class="btn btn-default"><i class="fa fa-calendar"></i> <span>%s</span></a>' % (revisionlist_url, _(u'History'))))

# action revision


class ActionRevisionPlugin(BaseAdminPlugin):

    reversion_enable = False

    def init_request(self, *args, **kwargs):
        return self.reversion_enable

    def do_action(self, __, queryset):
        with do_create_revision(self.request):
            return __()


class BaseReversionView(ModelAdminView):

    # The serialization format to use when registering models with reversion.
    reversion_format = "json"

    # Whether to ignore duplicate revision data.
    ignore_duplicate_revisions = False

    # If True, then the default ordering of object_history and recover lists will be reversed.
    history_latest_first = False

    reversion_enable = False

    def init_request(self, *args, **kwargs):
        if not self.has_change_permission() and not self.has_add_permission():
            raise PermissionDenied

    def _order_version_queryset(self, queryset):
        """Applies the correct ordering to the given version queryset."""
        if self.history_latest_first:
            return queryset.order_by("-pk")
        return queryset.order_by("pk")


class RecoverListView(BaseReversionView):

    recover_list_template = None

    def get_context(self):
        context = super(RecoverListView, self).get_context()
        opts = self.opts
        deleted = self._order_version_queryset(Version.objects.get_deleted(self.model))
        context.update({
            "opts": opts,
            "app_label": opts.app_label,
            "model_name": capfirst(opts.verbose_name),
            "title": _("Recover deleted %(name)s") % {"name": force_text(opts.verbose_name_plural)},
            "deleted": deleted,
            "changelist_url": self.model_admin_url("changelist"),
        })
        return context

    @csrf_protect_m
    def get(self, request, *args, **kwargs):
        context = self.get_context()

        return TemplateResponse(
            request, self.recover_list_template or self.get_template_list(
                "views/recover_list.html"),
            context)


class RevisionListView(BaseReversionView):

    object_history_template = None
    revision_diff_template = None

    def _reversion_order_version_queryset(self, queryset):
        """Applies the correct ordering to the given version queryset."""
        if not self.history_latest_first:
            queryset = queryset.order_by("pk")
        return queryset

    def get_context(self):
        context = super(RevisionListView, self).get_context()

        opts = self.opts
        action_list = [
            {
                "revision": version.revision,
                "url": self.model_admin_url('revision', quote(version.object_id), version.id),
                "version": version
            }
            for version
            in self._reversion_order_version_queryset(Version.objects.get_for_object_reference(
                self.model,
                self.obj.pk,
            ).select_related("revision__user"))
        ]
        context.update({
            'title': _('Change history: %s') % force_text(self.obj),
            'action_list': action_list,
            'model_name': capfirst(force_text(opts.verbose_name_plural)),
            'object': self.obj,
            'app_label': opts.app_label,
            "changelist_url": self.model_admin_url("changelist"),
            "update_url": self.model_admin_url("change", self.obj.pk),
            'opts': opts,
        })
        return context

    def get(self, request, object_id, *args, **kwargs):
        object_id = unquote(object_id)
        self.obj = self.get_object(object_id)

        if not self.has_change_permission(self.obj):
            raise PermissionDenied

        return self.get_response()

    def get_response(self):
        context = self.get_context()

        return TemplateResponse(self.request, self.object_history_template or
                                self.get_template_list('views/model_history.html'), context)

    def get_version_object(self, version):
        obj_version = version._object_version
        obj = obj_version.object
        obj._state.db = self.obj._state.db

        for field_name, pks in obj_version.m2m_data.items():
            f = self.opts.get_field(field_name)
            if f.rel and isinstance(f.rel, models.ManyToManyRel):
                setattr(obj, f.name, f.rel.to._default_manager.get_query_set(
                ).filter(pk__in=pks).all())

        detail = self.get_model_view(DetailAdminUtil, self.model, obj)

        return obj, detail

    def post(self, request, object_id, *args, **kwargs):
        object_id = unquote(object_id)
        self.obj = self.get_object(object_id)

        if not self.has_change_permission(self.obj):
            raise PermissionDenied

        params = self.request.POST
        if 'version_a' not in params or 'version_b' not in params:
            self.message_user(_("Must select two versions."), 'error')
            return self.get_response()

        version_a_id = params['version_a']
        version_b_id = params['version_b']

        if version_a_id == version_b_id:
            self.message_user(
                _("Please select two different versions."), 'error')
            return self.get_response()

        version_a = get_object_or_404(Version, pk=version_a_id)
        version_b = get_object_or_404(Version, pk=version_b_id)

        diffs = []

        obj_a, detail_a = self.get_version_object(version_a)
        obj_b, detail_b = self.get_version_object(version_b)

        for f in (self.opts.fields + self.opts.many_to_many):
            if is_related_field2(f):
                label = f.opts.verbose_name
            else:
                label = f.verbose_name

            value_a = f.value_from_object(obj_a)
            value_b = f.value_from_object(obj_b)
            is_diff = value_a != value_b

            if type(value_a) in (list, tuple) and type(value_b) in (list, tuple) \
                    and len(value_a) == len(value_b) and is_diff:
                is_diff = False
                for i in xrange(len(value_a)):
                    if value_a[i] != value_a[i]:
                        is_diff = True
                        break
            if type(value_a) is QuerySet and type(value_b) is QuerySet:
                is_diff = list(value_a) != list(value_b)

            diffs.append((label, detail_a.get_field_result(
                f.name).val, detail_b.get_field_result(f.name).val, is_diff))

        context = super(RevisionListView, self).get_context()
        context.update({
            'object': self.obj,
            'opts': self.opts,
            'version_a': version_a,
            'version_b': version_b,
            'revision_a_url': self.model_admin_url('revision', quote(version_a.object_id), version_a.id),
            'revision_b_url': self.model_admin_url('revision', quote(version_b.object_id), version_b.id),
            'diffs': diffs
        })

        return TemplateResponse(
            self.request, self.revision_diff_template or self.get_template_list('views/revision_diff.html'),
            context)

    @filter_hook
    def get_media(self):
        return super(RevisionListView, self).get_media() + self.vendor('xadmin.plugin.revision.js', 'xadmin.form.css')


class BaseRevisionView(ModelFormAdminView):

    @filter_hook
    def get_revision(self):
        return self.version.field_dict

    @filter_hook
    def get_form_datas(self):
        datas = {"instance": self.org_obj, "initial": self.get_revision()}
        if self.request_method == 'post':
            datas.update(
                {'data': self.request.POST, 'files': self.request.FILES})
        return datas

    @filter_hook
    def get_context(self):
        context = super(BaseRevisionView, self).get_context()
        context.update({
            'object': self.org_obj
        })
        return context

    @filter_hook
    def get_media(self):
        return super(BaseRevisionView, self).get_media() + self.vendor('xadmin.plugin.revision.js')


class DiffField(Field):

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        html = ''
        for field in self.fields:
            html += ('<div class="diff_field" rel="tooltip"><textarea class="org-data" style="display:none;">%s</textarea>%s</div>' %
                     (_('Current: %s') % self.attrs.pop('orgdata', ''), render_field(field, form, form_style, context, template_pack=template_pack, attrs=self.attrs)))
        return html


class RevisionView(BaseRevisionView):

    revision_form_template = None

    def init_request(self, object_id, version_id):
        self.detail = self.get_model_view(
            DetailAdminView, self.model, object_id)
        self.org_obj = self.detail.obj
        self.version = get_object_or_404(
            Version, pk=version_id, object_id=smart_text(self.org_obj.pk))

        self.prepare_form()

    def get_form_helper(self):
        helper = super(RevisionView, self).get_form_helper()
        diff_fields = {}
        version_data = self.version.field_dict

        for f in self.opts.fields:
            fvalue = f.value_from_object(self.org_obj)
            vvalue = version_data.get(f.name, None)

            if fvalue is None and vvalue == '':
                vvalue = None
            if is_related_field2(f):
                vvalue = version_data.get(f.name + '_' + f.rel.get_related_field().name, None)

            if fvalue != vvalue:
                diff_fields[f.name] = self.detail.get_field_result(f.name).val
        for k, v in diff_fields.items():
            helper[k].wrap(DiffField, orgdata=v)
        return helper

    @filter_hook
    def get_context(self):
        context = super(RevisionView, self).get_context()
        context["title"] = _(
            "Revert %s") % force_text(self.model._meta.verbose_name)
        return context

    @filter_hook
    def get_response(self):
        context = self.get_context()
        context.update(self.kwargs or {})

        form_template = self.revision_form_template
        return TemplateResponse(
            self.request, form_template or self.get_template_list(
                'views/revision_form.html'),
            context)

    @filter_hook
    def post_response(self):
        self.message_user(_('The %(model)s "%(name)s" was reverted successfully. You may edit it again below.') %
                          {"model": force_text(self.opts.verbose_name), "name": smart_text(self.new_obj)}, 'success')
        return HttpResponseRedirect(self.model_admin_url('change', self.new_obj.pk))


class RecoverView(BaseRevisionView):

    recover_form_template = None

    def init_request(self, version_id):
        if not self.has_change_permission() and not self.has_add_permission():
            raise PermissionDenied

        self.version = get_object_or_404(Version, pk=version_id)
        self.org_obj = self.version._object_version.object

        self.prepare_form()

    @filter_hook
    def get_context(self):
        context = super(RecoverView, self).get_context()
        context["title"] = _("Recover %s") % self.version.object_repr
        return context

    @filter_hook
    def get_response(self):
        context = self.get_context()
        context.update(self.kwargs or {})

        form_template = self.recover_form_template
        return TemplateResponse(
            self.request, form_template or self.get_template_list(
                'views/recover_form.html'),
            context)

    @filter_hook
    def post_response(self):
        self.message_user(_('The %(model)s "%(name)s" was recovered successfully. You may edit it again below.') %
                          {"model": force_text(self.opts.verbose_name), "name": smart_text(self.new_obj)}, 'success')
        return HttpResponseRedirect(self.model_admin_url('change', self.new_obj.pk))


class InlineDiffField(Field):

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        html = ''
        instance = form.instance
        if not instance.pk:
            return super(InlineDiffField, self).render(form, form_style, context)

        initial = form.initial
        opts = instance._meta
        detail = form.detail
        for field in self.fields:
            f = opts.get_field(field)
            f_html = render_field(field, form, form_style, context,
                                  template_pack=template_pack, attrs=self.attrs)
            if f.value_from_object(instance) != initial.get(field, None):
                current_val = detail.get_field_result(f.name).val
                html += ('<div class="diff_field" rel="tooltip"><textarea class="org-data" style="display:none;">%s</textarea>%s</div>'
                         % (_('Current: %s') % current_val, f_html))
            else:
                html += f_html
        return html

# inline hack plugin


class InlineRevisionPlugin(BaseAdminPlugin):

    def get_related_versions(self, obj, version, formset):
        """Retreives all the related Version objects for the given FormSet."""
        object_id = obj.pk
        # Get the fk name.
        try:
            fk_name = formset.fk.name + '_' + formset.fk.rel.get_related_field().name
        except AttributeError:
            # This is a GenericInlineFormset, or similar.
            fk_name = formset.ct_fk_field.name
        # Look up the revision data.
        revision_versions = version.revision.version_set.all()
        related_versions = dict([(related_version.object_id, related_version)
                                 for related_version in revision_versions
                                 if ContentType.objects.get_for_id(related_version.content_type_id).model_class() == formset.model
                                 and smart_text(related_version.field_dict[fk_name]) == smart_text(object_id)])
        return related_versions

    def _hack_inline_formset_initial(self, revision_view, formset):
        """Hacks the given formset to contain the correct initial data."""
        # Now we hack it to push in the data from the revision!
        initial = []
        related_versions = self.get_related_versions(
            revision_view.org_obj, revision_view.version, formset)
        formset.related_versions = related_versions
        for related_obj in formset.queryset:
            if smart_text(related_obj.pk) in related_versions:
                initial.append(
                    related_versions.pop(smart_text(related_obj.pk)).field_dict)
            else:
                initial_data = model_to_dict(related_obj)
                initial_data["DELETE"] = True
                initial.append(initial_data)
        for related_version in related_versions.values():
            initial_row = related_version.field_dict
            pk_name = ContentType.objects.get_for_id(
                related_version.content_type_id).model_class()._meta.pk.name
            del initial_row[pk_name]
            initial.append(initial_row)
        # Reconstruct the forms with the new revision data.
        formset.initial = initial
        formset.forms = [formset._construct_form(
            n) for n in xrange(len(initial))]
        # Hack the formset to force a save of everything.

        def get_changed_data(form):
            return [field.name for field in form.fields]
        for form in formset.forms:
            form.has_changed = lambda: True
            form._get_changed_data = partial(get_changed_data, form=form)

        def total_form_count_hack(count):
            return lambda: count
        formset.total_form_count = total_form_count_hack(len(initial))

        if self.request.method == 'GET' and formset.helper and formset.helper.layout:
            helper = formset.helper
            cls_str = str if six.PY3 else basestring
            helper.filter(cls_str).wrap(InlineDiffField)
            fake_admin_class = type(str('%s%sFakeAdmin' % (self.opts.app_label, self.opts.model_name)), (object, ), {'model': self.model})
            for form in formset.forms:
                instance = form.instance
                if instance.pk:
                    form.detail = self.get_view(
                        DetailAdminUtil, fake_admin_class, instance)

    def instance_form(self, formset, **kwargs):
        admin_view = self.admin_view.admin_view
        if hasattr(admin_view, 'version') and hasattr(admin_view, 'org_obj'):
            self._hack_inline_formset_initial(admin_view, formset)
        return formset


class VersionInline(object):
    model = Version
    extra = 0
    style = 'accordion'


class ReversionAdmin(object):
    model_icon = 'fa fa-exchange'

    list_display = ('__str__', 'date_created', 'user', 'comment')
    list_display_links = ('__str__',)

    list_filter = ('date_created', 'user')
    inlines = [VersionInline]

site.register(Revision, ReversionAdmin)

site.register_modelview(
    r'^recover/$', RecoverListView, name='%s_%s_recoverlist')
site.register_modelview(
    r'^recover/([^/]+)/$', RecoverView, name='%s_%s_recover')
site.register_modelview(
    r'^([^/]+)/revision/$', RevisionListView, name='%s_%s_revisionlist')
site.register_modelview(
    r'^([^/]+)/revision/([^/]+)/$', RevisionView, name='%s_%s_revision')

site.register_plugin(ReversionPlugin, ListAdminView)
site.register_plugin(ReversionPlugin, ModelFormAdminView)
site.register_plugin(ReversionPlugin, DeleteAdminView)

site.register_plugin(InlineRevisionPlugin, InlineModelAdmin)
site.register_plugin(ActionRevisionPlugin, BaseActionView)
