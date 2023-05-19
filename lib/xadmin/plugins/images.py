from django.db import models
from django import forms
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from xadmin.sites import site
from xadmin.views import BaseAdminPlugin, ModelFormAdminView, DetailAdminView, ListAdminView


def get_gallery_modal():
    return """
        <!-- modal-gallery is the modal dialog used for the image gallery -->
        <div id="modal-gallery" class="modal modal-gallery fade" tabindex="-1">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
                <h4 class="modal-title"></h4>
              </div>
              <div class="modal-body"><div class="modal-image"><h1 class="loader"><i class="fa-spinner fa-spin fa fa-large loader"></i></h1></div></div>
              <div class="modal-footer">
                  <a class="btn btn-info modal-prev"><i class="fa fa-arrow-left"></i> <span>%s</span></a>
                  <a class="btn btn-primary modal-next"><span>%s</span> <i class="fa fa-arrow-right"></i></a>
                  <a class="btn btn-success modal-play modal-slideshow" data-slideshow="5000"><i class="fa fa-play"></i> <span>%s</span></a>
                  <a class="btn btn-default modal-download" target="_blank"><i class="fa fa-download"></i> <span>%s</span></a>
              </div>
            </div><!-- /.modal-content -->
          </div><!-- /.modal-dialog -->
        </div>
    """ % (_('Previous'), _('Next'), _('Slideshow'), _('Download'))


class AdminImageField(forms.ImageField):

    def widget_attrs(self, widget):
        return {'label': self.label}


class AdminImageWidget(forms.FileInput):
    """
    A ImageField Widget that shows its current value if it has one.
    """
    def __init__(self, attrs={}):
        super(AdminImageWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None, renderer=None):
        output = []
        if value and hasattr(value, "url"):
            label = self.attrs.get('label', name)
            output.append('<a href="%s" target="_blank" title="%s" data-gallery="gallery"><img src="%s" class="field_img"/></a><br/>%s ' %
                         (value.url, label, value.url, _('Change:')))
        output.append(super(AdminImageWidget, self).render(name, value, attrs, renderer))
        return mark_safe(u''.join(output))


class ModelDetailPlugin(BaseAdminPlugin):

    def __init__(self, admin_view):
        super(ModelDetailPlugin, self).__init__(admin_view)
        self.include_image = False

    def get_field_attrs(self, attrs, db_field, **kwargs):
        if isinstance(db_field, models.ImageField):
            attrs['widget'] = AdminImageWidget
            attrs['form_class'] = AdminImageField
            self.include_image = True
        return attrs

    def get_field_result(self, result, field_name):
        if isinstance(result.field, models.ImageField):
            if result.value:
                img = getattr(result.obj, field_name)
                result.text = mark_safe('<a href="%s" target="_blank" title="%s" data-gallery="gallery"><img src="%s" class="field_img"/></a>' % (img.url, result.label, img.url))
                self.include_image = True
        return result

    # Media
    def get_media(self, media):
        if self.include_image:
            media = media + self.vendor('image-gallery.js',
                                        'image-gallery.css')
        return media

    def block_before_fieldsets(self, context, node):
        if self.include_image:
            return '<div id="gallery" data-toggle="modal-gallery" data-target="#modal-gallery">'

    def block_after_fieldsets(self, context, node):
        if self.include_image:
            return "</div>"

    def block_extrabody(self, context, node):
        if self.include_image:
            return get_gallery_modal()


class ModelListPlugin(BaseAdminPlugin):

    list_gallery = False

    def init_request(self, *args, **kwargs):
        return bool(self.list_gallery)

    # Media
    def get_media(self, media):
        return media + self.vendor('image-gallery.js', 'image-gallery.css')

    def block_results_top(self, context, node):
        return '<div id="gallery" data-toggle="modal-gallery" data-target="#modal-gallery">'

    def block_results_bottom(self, context, node):
        return "</div>"

    def block_extrabody(self, context, node):
        return get_gallery_modal()


site.register_plugin(ModelDetailPlugin, DetailAdminView)
site.register_plugin(ModelDetailPlugin, ModelFormAdminView)
site.register_plugin(ModelListPlugin, ListAdminView)
