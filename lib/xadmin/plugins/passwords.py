# coding=utf-8
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetConfirmView as password_reset_confirm
from django.template.response import TemplateResponse
from django.utils.translation import ugettext as _

from xadmin.sites import site
from xadmin.views.base import BaseAdminPlugin, BaseAdminView, csrf_protect_m
from xadmin.views.website import LoginView


class ResetPasswordSendView(BaseAdminView):

    need_site_permission = False

    password_reset_form = PasswordResetForm
    password_reset_template = 'xadmin/auth/password_reset/form.html'
    password_reset_done_template = 'xadmin/auth/password_reset/done.html'
    password_reset_token_generator = default_token_generator

    password_reset_from_email = None
    password_reset_email_template = 'xadmin/auth/password_reset/email.html'
    password_reset_subject_template = None

    def get(self, request, *args, **kwargs):
        context = super(ResetPasswordSendView, self).get_context()
        context['form'] = kwargs.get('form', self.password_reset_form())

        return TemplateResponse(request, self.password_reset_template, context)

    @csrf_protect_m
    def post(self, request, *args, **kwargs):
        form = self.password_reset_form(request.POST)

        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': self.password_reset_token_generator,
                'email_template_name': self.password_reset_email_template,
                'request': request,
                'domain_override': request.get_host()
            }

            if self.password_reset_from_email:
                opts['from_email'] = self.password_reset_from_email
            if self.password_reset_subject_template:
                opts['subject_template_name'] = self.password_reset_subject_template

            form.save(**opts)
            context = super(ResetPasswordSendView, self).get_context()
            return TemplateResponse(request, self.password_reset_done_template, context)
        else:
            return self.get(request, form=form)


site.register_view(r'^xadmin/password_reset/$', ResetPasswordSendView, name='xadmin_password_reset')


class ResetLinkPlugin(BaseAdminPlugin):

    def block_form_bottom(self, context, nodes):
        reset_link = self.get_admin_url('xadmin_password_reset')
        return '<div class="text-info" style="margin-top:15px;"><a href="%s"><i class="fa fa-question-sign"></i> %s</a></div>' % (reset_link, _('Forgotten your password or username?'))


site.register_plugin(ResetLinkPlugin, LoginView)


class ResetPasswordComfirmView(BaseAdminView):

    need_site_permission = False

    password_reset_set_form = SetPasswordForm
    password_reset_confirm_template = 'xadmin/auth/password_reset/confirm.html'
    password_reset_token_generator = default_token_generator

    def do_view(self, request, uidb36, token, *args, **kwargs):
        context = super(ResetPasswordComfirmView, self).get_context()
        return password_reset_confirm(request, uidb36, token,
                                      template_name=self.password_reset_confirm_template,
                                      token_generator=self.password_reset_token_generator,
                                      set_password_form=self.password_reset_set_form,
                                      post_reset_redirect=self.get_admin_url('xadmin_password_reset_complete'),
                                      current_app=self.admin_site.name, extra_context=context)

    def get(self, request, uidb36, token, *args, **kwargs):
        return self.do_view(request, uidb36, token)

    def post(self, request, uidb36, token, *args, **kwargs):
        return self.do_view(request, uidb36, token)

    def get_media(self):
        return super(ResetPasswordComfirmView, self).get_media() + \
            self.vendor('xadmin.page.form.js', 'xadmin.form.css')


site.register_view(r'^xadmin/password_reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                   ResetPasswordComfirmView, name='xadmin_password_reset_confirm')


class ResetPasswordCompleteView(BaseAdminView):

    need_site_permission = False

    password_reset_complete_template = 'xadmin/auth/password_reset/complete.html'

    def get(self, request, *args, **kwargs):
        context = super(ResetPasswordCompleteView, self).get_context()
        context['login_url'] = self.get_admin_url('index')

        return TemplateResponse(request, self.password_reset_complete_template, context)


site.register_view(r'^xadmin/password_reset/complete/$', ResetPasswordCompleteView, name='xadmin_password_reset_complete')
