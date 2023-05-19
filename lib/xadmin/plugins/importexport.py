#!/usr/bin/env python
# encoding=utf-8
"""
Author:zcyuefan
Topic:django-import-export plugin for xadmin to help importing and exporting data using .csv/.xls/.../.json files

Use:
+++ settings.py +++
INSTALLED_APPS = (
    ...
    'import_export',
)

+++ model.py +++
from django.db import models

class Foo(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()

+++ adminx.py +++
import xadmin
from import_export import resources
from .models import Foo

class FooResource(resources.ModelResource):

    class Meta:
        model = Foo
        # fields = ('name', 'description',)
        # exclude = ()


@xadmin.sites.register(Foo)
class FooAdmin(object):
    import_export_args = {'import_resource_class': FooResource, 'export_resource_class': FooResource}

++++++++++++++++
More info about django-import-export please refer https://github.com/django-import-export/django-import-export
"""
from datetime import datetime
from django.template import loader
from xadmin.plugins.utils import get_context_dict
from xadmin.sites import site
from xadmin.views import BaseAdminPlugin, ListAdminView, ModelAdminView
from xadmin.views.base import csrf_protect_m, filter_hook
from django.db import transaction
from import_export.admin import DEFAULT_FORMATS, SKIP_ADMIN_LOG, TMP_STORAGE_CLASS
from import_export.resources import modelresource_factory
from import_export.forms import (
    ImportForm,
    ConfirmImportForm,
    ExportForm,
)
from import_export.results import RowResult
from import_export.signals import post_export, post_import
try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text
from django.utils.translation import ugettext_lazy as _
from django.template.response import TemplateResponse
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.urls.base import reverse
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, HttpResponse


class ImportMenuPlugin(BaseAdminPlugin):
    import_export_args = {}

    def init_request(self, *args, **kwargs):
        return bool(self.import_export_args.get('import_resource_class'))

    def block_top_toolbar(self, context, nodes):
        has_change_perm = self.has_model_perm(self.model, 'change')
        has_add_perm = self.has_model_perm(self.model, 'add')
        if has_change_perm and has_add_perm:
            model_info = (self.opts.app_label, self.opts.model_name)
            import_url = reverse('xadmin:%s_%s_import' % model_info, current_app=self.admin_site.name)
            context = get_context_dict(context or {})  # no error!
            context.update({
                'import_url': import_url,
            })
            nodes.append(loader.render_to_string('xadmin/blocks/model_list.top_toolbar.importexport.import.html',
                                                 context=context))


class ImportBaseView(ModelAdminView):
    """
    """
    resource_class = None
    import_export_args = {}
    #: template for import view
    import_template_name = 'xadmin/import_export/import.html'
    #: resource class
    #: available import formats
    formats = DEFAULT_FORMATS
    #: import data encoding
    from_encoding = "utf-8"
    skip_admin_log = None
    # storage class for saving temporary files
    tmp_storage_class = None

    def get_skip_admin_log(self):
        if self.skip_admin_log is None:
            return SKIP_ADMIN_LOG
        else:
            return self.skip_admin_log

    def get_tmp_storage_class(self):
        if self.tmp_storage_class is None:
            return TMP_STORAGE_CLASS
        else:
            return self.tmp_storage_class

    def get_resource_kwargs(self, request, *args, **kwargs):
        return {}

    def get_import_resource_kwargs(self, request, *args, **kwargs):
        return self.get_resource_kwargs(request, *args, **kwargs)

    def get_resource_class(self, usage):
        if usage == 'import':
            return self.import_export_args.get('import_resource_class') if self.import_export_args.get(
                'import_resource_class') else modelresource_factory(self.model)
        elif usage == 'export':
            return self.import_export_args.get('export_resource_class') if self.import_export_args.get(
                'export_resource_class') else modelresource_factory(self.model)
        else:
            return modelresource_factory(self.model)

    def get_import_resource_class(self):
        """
        Returns ResourceClass to use for import.
        """
        return self.process_import_resource(self.get_resource_class(usage='import'))

    def process_import_resource(self, resource):
        """
        Returns processed ResourceClass to use for import.
        Override to custom your own process
        """
        return resource

    def get_import_formats(self):
        """
        Returns available import formats.
        """
        return [f for f in self.formats if f().can_import()]


class ImportView(ImportBaseView):

    def get_media(self):
        media = super(ImportView, self).get_media()
        media = media + self.vendor('xadmin.plugin.importexport.css')
        return media

    @filter_hook
    def get(self, request, *args, **kwargs):
        if not (self.has_change_permission() and self.has_add_permission()):
            raise PermissionDenied

        resource = self.get_import_resource_class()(**self.get_import_resource_kwargs(request, *args, **kwargs))

        context = super(ImportView, self).get_context()

        import_formats = self.get_import_formats()
        form = ImportForm(import_formats,
                          request.POST or None,
                          request.FILES or None)

        context['title'] = _("Import") + ' ' + self.opts.verbose_name
        context['form'] = form
        context['opts'] = self.model._meta
        context['fields'] = [f.column_name for f in resource.get_user_visible_fields()]

        request.current_app = self.admin_site.name
        return TemplateResponse(request, [self.import_template_name],
                                context)

    @filter_hook
    @csrf_protect_m
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
            Perform a dry_run of the import to make sure the import will not
        result in errors.  If there where no error, save the user
        uploaded file to a local temp file that will be used by
        'process_import' for the actual import.
        """
        if not (self.has_change_permission() and self.has_add_permission()):
            raise PermissionDenied

        resource = self.get_import_resource_class()(**self.get_import_resource_kwargs(request, *args, **kwargs))

        context = super(ImportView, self).get_context()

        import_formats = self.get_import_formats()
        form = ImportForm(import_formats,
                          request.POST or None,
                          request.FILES or None)

        if request.POST and form.is_valid():
            input_format = import_formats[
                int(form.cleaned_data['input_format'])
            ]()
            import_file = form.cleaned_data['import_file']
            # first always write the uploaded file to disk as it may be a
            # memory file or else based on settings upload handlers
            tmp_storage = self.get_tmp_storage_class()()
            data = bytes()
            for chunk in import_file.chunks():
                data += chunk

            tmp_storage.save(data, input_format.get_read_mode())

            # then read the file, using the proper format-specific mode
            # warning, big files may exceed memory
            try:
                data = tmp_storage.read(input_format.get_read_mode())
                if not input_format.is_binary() and self.from_encoding:
                    data = force_text(data, self.from_encoding)
                dataset = input_format.create_dataset(data)
            except UnicodeDecodeError as e:
                return HttpResponse(_(u"<h1>Imported file has a wrong encoding: %s</h1>" % e))
            except Exception as e:
                return HttpResponse(_(u"<h1>%s encountered while trying to read file: %s</h1>" % (type(e).__name__,
                                                                                                  import_file.name)))
            result = resource.import_data(dataset, dry_run=True,
                                          raise_errors=False,
                                          file_name=import_file.name,
                                          user=request.user)

            context['result'] = result

            if not result.has_errors():
                context['confirm_form'] = ConfirmImportForm(initial={
                    'import_file_name': tmp_storage.name,
                    'original_file_name': import_file.name,
                    'input_format': form.cleaned_data['input_format'],
                })

        context['title'] = _("Import") + ' ' + self.opts.verbose_name
        context['form'] = form
        context['opts'] = self.model._meta
        context['fields'] = [f.column_name for f in resource.get_user_visible_fields()]

        request.current_app = self.admin_site.name
        return TemplateResponse(request, [self.import_template_name],
                                context)


class ImportProcessView(ImportBaseView):

    @filter_hook
    @csrf_protect_m
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Perform the actual import action (after the user has confirmed he
        wishes to import)
        """
        resource = self.get_import_resource_class()(**self.get_import_resource_kwargs(request, *args, **kwargs))

        confirm_form = ConfirmImportForm(request.POST)
        if confirm_form.is_valid():
            import_formats = self.get_import_formats()
            input_format = import_formats[
                int(confirm_form.cleaned_data['input_format'])
            ]()
            tmp_storage = self.get_tmp_storage_class()(name=confirm_form.cleaned_data['import_file_name'])
            data = tmp_storage.read(input_format.get_read_mode())
            if not input_format.is_binary() and self.from_encoding:
                data = force_text(data, self.from_encoding)
            dataset = input_format.create_dataset(data)

            result = resource.import_data(dataset, dry_run=False,
                                          raise_errors=True,
                                          file_name=confirm_form.cleaned_data['original_file_name'],
                                          user=request.user)

            if not self.get_skip_admin_log():
                # Add imported objects to LogEntry
                logentry_map = {
                    RowResult.IMPORT_TYPE_NEW: ADDITION,
                    RowResult.IMPORT_TYPE_UPDATE: CHANGE,
                    RowResult.IMPORT_TYPE_DELETE: DELETION,
                }
                content_type_id = ContentType.objects.get_for_model(self.model).pk
                for row in result:
                    if row.import_type != row.IMPORT_TYPE_ERROR and row.import_type != row.IMPORT_TYPE_SKIP:
                        LogEntry.objects.log_action(
                            user_id=request.user.pk,
                            content_type_id=content_type_id,
                            object_id=row.object_id,
                            object_repr=row.object_repr,
                            action_flag=logentry_map[row.import_type],
                            change_message="%s through import_export" % row.import_type,
                        )
            success_message = str(_(u'Import finished')) + ' , ' + str(_(u'Add')) + ' : %d' % result.totals[
                RowResult.IMPORT_TYPE_NEW] + ' , ' + str(_(u'Update')) + ' : %d' % result.totals[
                RowResult.IMPORT_TYPE_UPDATE]

            messages.success(request, success_message)
            tmp_storage.remove()

            post_import.send(sender=None, model=self.model)
            model_info = (self.opts.app_label, self.opts.model_name)
            url = reverse('xadmin:%s_%s_changelist' % model_info,
                          current_app=self.admin_site.name)
            return HttpResponseRedirect(url)


class ExportMixin(object):
    #: resource class
    resource_class = None
    #: template for change_list view
    change_list_template = None
    import_export_args = {}
    #: template for export view
    # export_template_name = 'xadmin/import_export/export.html'
    #: available export formats
    formats = DEFAULT_FORMATS
    #: export data encoding
    to_encoding = "utf-8"
    list_select_related = None

    def get_resource_kwargs(self, request, *args, **kwargs):
        return {}

    def get_export_resource_kwargs(self, request, *args, **kwargs):
        return self.get_resource_kwargs(request, *args, **kwargs)

    def get_resource_class(self, usage):
        if usage == 'import':
            return self.import_export_args.get('import_resource_class') if self.import_export_args.get(
                'import_resource_class') else modelresource_factory(self.model)
        elif usage == 'export':
            return self.import_export_args.get('export_resource_class') if self.import_export_args.get(
                'export_resource_class') else modelresource_factory(self.model)
        else:
            return modelresource_factory(self.model)

    def get_export_resource_class(self):
        """
        Returns ResourceClass to use for export.
        """
        return self.get_resource_class(usage='export')

    def get_export_formats(self):
        """
        Returns available export formats.
        """
        return [f for f in self.formats if f().can_export()]

    def get_export_filename(self, file_format):
        date_str = datetime.now().strftime('%Y-%m-%d-%H%M%S')
        filename = "%s-%s.%s" % (self.opts.verbose_name.encode('utf-8'),
                                 date_str,
                                 file_format.get_extension())
        return filename

    def get_export_queryset(self, request, context):
        """
        Returns export queryset.

        Default implementation respects applied search and filters.
        """
        # scope = self.request.POST.get('_select_across', False) == '1'
        scope = request.GET.get('scope')
        select_across = request.GET.get('_select_across', False) == '1'
        selected = request.GET.get('_selected_actions', '')
        if scope == 'all':
            queryset = self.admin_view.queryset()
        elif scope == 'header_only':
            queryset = []
        elif scope == 'selected':
            if not select_across:
                selected_pk = selected.split(',')
                queryset = self.admin_view.queryset().filter(pk__in=selected_pk)
            else:
                queryset = self.admin_view.queryset()
        else:
            queryset = [r['object'] for r in context['results']]
        return queryset

    def get_export_data(self, file_format, queryset, *args, **kwargs):
        """
        Returns file_format representation for given queryset.
        """
        request = kwargs.pop("request")
        resource_class = self.get_export_resource_class()
        data = resource_class(**self.get_export_resource_kwargs(request)).export(queryset, *args, **kwargs)
        export_data = file_format.export_data(data)
        return export_data


class ExportMenuPlugin(ExportMixin, BaseAdminPlugin):
    import_export_args = {}

    # Media
    def get_media(self, media):
        return media + self.vendor('xadmin.plugin.importexport.css', 'xadmin.plugin.importexport.js')

    def init_request(self, *args, **kwargs):
        return bool(self.import_export_args.get('export_resource_class'))

    def block_top_toolbar(self, context, nodes):
        formats = self.get_export_formats()
        form = ExportForm(formats)

        context = get_context_dict(context or {})  # no error!
        context.update({
            'form': form,
            'opts': self.opts,
            'form_params': self.admin_view.get_form_params({'_action_': 'export'}),
        })
        nodes.append(loader.render_to_string('xadmin/blocks/model_list.top_toolbar.importexport.export.html',
                                             context=context))


class ExportPlugin(ExportMixin, BaseAdminPlugin):

    def init_request(self, *args, **kwargs):
        return self.request.GET.get('_action_') == 'export'

    def get_response(self, response, context, *args, **kwargs):
        has_view_perm = self.has_model_perm(self.model, 'view')
        if not has_view_perm:
            raise PermissionDenied

        export_format = self.request.GET.get('file_format')

        if not export_format:
            messages.warning(self.request, _('You must select an export format.'))
        else:
            formats = self.get_export_formats()
            file_format = formats[int(export_format)]()
            queryset = self.get_export_queryset(self.request, context)
            export_data = self.get_export_data(file_format, queryset, request=self.request)
            content_type = file_format.get_content_type()
            # Django 1.7 uses the content_type kwarg instead of mimetype
            try:
                response = HttpResponse(export_data, content_type=content_type)
            except TypeError:
                response = HttpResponse(export_data, mimetype=content_type)
            response['Content-Disposition'] = 'attachment; filename=%s' % (
                self.get_export_filename(file_format),
            )
            post_export.send(sender=None, model=self.model)
            return response


site.register_modelview(r'^import/$', ImportView, name='%s_%s_import')
site.register_modelview(r'^process_import/$', ImportProcessView, name='%s_%s_process_import')
site.register_plugin(ImportMenuPlugin, ListAdminView)
site.register_plugin(ExportMenuPlugin, ListAdminView)
site.register_plugin(ExportPlugin, ListAdminView)
