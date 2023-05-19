from collections import OrderedDict
from django.forms.utils import ErrorDict
from django.utils.html import escape
from django.utils.encoding import force_text
from xadmin.sites import site
from xadmin.views import BaseAdminPlugin, ListAdminView, ModelFormAdminView, DetailAdminView


NON_FIELD_ERRORS = '__all__'


class BaseAjaxPlugin(BaseAdminPlugin):

    def init_request(self, *args, **kwargs):
        return bool(self.request.is_ajax() or self.request.GET.get('_ajax'))


class AjaxListPlugin(BaseAjaxPlugin):
    
    def get_list_display(self,list_display):
        list_fields = [field for field in self.request.GET.get('_fields',"").split(",") 
                                if field.strip() != ""]
        if list_fields:
            return list_fields
        return list_display

    def get_result_list(self, response):
        av = self.admin_view
        base_fields = self.get_list_display(av.base_list_display)
        headers = dict([(c.field_name, force_text(c.text)) for c in av.result_headers(
        ).cells if c.field_name in base_fields])

        objects = [dict([(o.field_name, escape(str(o.value))) for i, o in
                         enumerate(filter(lambda c:c.field_name in base_fields, r.cells))])
                   for r in av.results()]

        return self.render_response({'headers': headers, 'objects': objects, 'total_count': av.result_count, 'has_more': av.has_more})


class JsonErrorDict(ErrorDict):

    def __init__(self, errors, form):
        super(JsonErrorDict, self).__init__(errors)
        self.form = form

    def as_json(self):
        if not self:
            return u''
        return [{'id': self.form[k].auto_id if k != NON_FIELD_ERRORS else NON_FIELD_ERRORS, 'name': k, 'errors': v} for k, v in self.items()]


class AjaxFormPlugin(BaseAjaxPlugin):

    def post_response(self, __):
        new_obj = self.admin_view.new_obj
        return self.render_response({
            'result': 'success',
            'obj_id': new_obj.pk,
            'obj_repr': str(new_obj),
            'change_url': self.admin_view.model_admin_url('change', new_obj.pk),
            'detail_url': self.admin_view.model_admin_url('detail', new_obj.pk)
        })

    def get_response(self, __):
        if self.request.method.lower() != 'post':
            return __()

        result = {}
        form = self.admin_view.form_obj
        if form.is_valid():
            result['result'] = 'success'
        else:
            result['result'] = 'error'
            result['errors'] = JsonErrorDict(form.errors, form).as_json()

        return self.render_response(result)


class AjaxDetailPlugin(BaseAjaxPlugin):

    def get_response(self, __):
        if self.request.GET.get('_format') == 'html':
            self.admin_view.detail_template = 'xadmin/views/quick_detail.html'
            return __()

        form = self.admin_view.form_obj
        layout = form.helper.layout

        results = []

        for p, f in layout.get_field_names():
            result = self.admin_view.get_field_result(f)
            results.append((result.label, result.val))

        return self.render_response(OrderedDict(results))

site.register_plugin(AjaxListPlugin, ListAdminView)
site.register_plugin(AjaxFormPlugin, ModelFormAdminView)
site.register_plugin(AjaxDetailPlugin, DetailAdminView)
