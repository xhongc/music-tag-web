
from django.contrib.contenttypes.models import ContentType
from django.urls.base import reverse
from django.db import transaction
from django.db.models import Q
from django.forms import ModelChoiceField
from django.http import QueryDict
from django.template import loader
from django.utils.decorators import method_decorator
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect

from xadmin.filters import FILTER_PREFIX, SEARCH_VAR
from xadmin.plugins.relate import RELATE_PREFIX
from xadmin.plugins.utils import get_context_dict
from xadmin.sites import site
from xadmin.views import ModelAdminView, BaseAdminPlugin, ListAdminView
from xadmin.views.list import COL_LIST_VAR, ORDER_VAR
from xadmin.views.dashboard import widget_manager, BaseWidget, PartialBaseWidget

from xadmin.models import Bookmark

csrf_protect_m = method_decorator(csrf_protect)


class BookmarkPlugin(BaseAdminPlugin):

    # [{'title': "Female", 'query': {'gender': True}, 'order': ('-age'), 'cols': ('first_name', 'age', 'phones'), 'search': 'Tom'}]
    list_bookmarks = []
    show_bookmarks = True

    def has_change_permission(self, obj=None):
        if not obj or self.user.is_superuser:
            return True
        else:
            return obj.user == self.user

    def get_context(self, context):
        if not self.show_bookmarks:
            return context

        bookmarks = []

        current_qs = '&'.join([
            '%s=%s' % (k, v)
            for k, v in sorted(filter(
                lambda i: bool(i[1] and (
                    i[0] in (COL_LIST_VAR, ORDER_VAR, SEARCH_VAR)
                    or i[0].startswith(FILTER_PREFIX)
                    or i[0].startswith(RELATE_PREFIX)
                )),
                self.request.GET.items()
            ))
        ])

        model_info = (self.opts.app_label, self.opts.model_name)
        has_selected = False
        menu_title = _(u"Bookmark")
        list_base_url = reverse('xadmin:%s_%s_changelist' %
                                model_info, current_app=self.admin_site.name)

        # local bookmarks
        for bk in self.list_bookmarks:
            title = bk['title']
            params = dict([
                (FILTER_PREFIX + k, v)
                for (k, v) in bk['query'].items()
            ])
            if 'order' in bk:
                params[ORDER_VAR] = '.'.join(bk['order'])
            if 'cols' in bk:
                params[COL_LIST_VAR] = '.'.join(bk['cols'])
            if 'search' in bk:
                params[SEARCH_VAR] = bk['search']

            def check_item(i):
                return bool(i[1]) or i[1] == False
            bk_qs = '&'.join([
                    '%s=%s' % (k, v)
                    for k, v in sorted(filter(check_item, params.items()))
            ])

            url = list_base_url + '?' + bk_qs
            selected = (current_qs == bk_qs)

            bookmarks.append(
                {'title': title, 'selected': selected, 'url': url})
            if selected:
                menu_title = title
                has_selected = True

        content_type = ContentType.objects.get_for_model(self.model)
        bk_model_info = (Bookmark._meta.app_label, Bookmark._meta.model_name)
        bookmarks_queryset = Bookmark.objects.filter(
            content_type=content_type,
            url_name='xadmin:%s_%s_changelist' % model_info
        ).filter(Q(user=self.user) | Q(is_share=True))

        for bk in bookmarks_queryset:
            selected = (current_qs == bk.query)

            if self.has_change_permission(bk):
                change_or_detail = 'change'
            else:
                change_or_detail = 'detail'

            bookmarks.append({'title': bk.title, 'selected': selected, 'url': bk.url, 'edit_url':
                              reverse('xadmin:%s_%s_%s' % (bk_model_info[0], bk_model_info[1], change_or_detail),
                                      args=(bk.id,))})
            if selected:
                menu_title = bk.title
                has_selected = True

        post_url = reverse('xadmin:%s_%s_bookmark' % model_info,
                           current_app=self.admin_site.name)

        new_context = {
            'bk_menu_title': menu_title,
            'bk_bookmarks': bookmarks,
            'bk_current_qs': current_qs,
            'bk_has_selected': has_selected,
            'bk_list_base_url': list_base_url,
            'bk_post_url': post_url,
            'has_add_permission_bookmark': self.admin_view.request.user.has_perm('xadmin.add_bookmark'),
            'has_change_permission_bookmark': self.admin_view.request.user.has_perm('xadmin.change_bookmark')
        }
        context.update(new_context)
        return context

    # Media
    def get_media(self, media):
        return media + self.vendor('xadmin.plugin.bookmark.js')

    # Block Views
    def block_nav_menu(self, context, nodes):
        if self.show_bookmarks:
            nodes.insert(0, loader.render_to_string('xadmin/blocks/model_list.nav_menu.bookmarks.html',
                                                    context=get_context_dict(context)))


class BookmarkView(ModelAdminView):

    @csrf_protect_m
    @transaction.atomic
    def post(self, request):
        model_info = (self.opts.app_label, self.opts.model_name)
        url_name = 'xadmin:%s_%s_changelist' % model_info
        bookmark = Bookmark(
            content_type=ContentType.objects.get_for_model(self.model),
            title=request.POST[
                'title'], user=self.user, query=request.POST.get('query', ''),
            is_share=request.POST.get('is_share', 0), url_name=url_name)
        bookmark.save()
        content = {'title': bookmark.title, 'url': bookmark.url}
        return self.render_response(content)


class BookmarkAdmin(object):

    model_icon = 'fa fa-book'
    list_display = ('title', 'user', 'url_name', 'query')
    list_display_links = ('title',)
    user_fields = ['user']
    hidden_menu = True

    def queryset(self):
        if self.user.is_superuser:
            return Bookmark.objects.all()
        return Bookmark.objects.filter(Q(user=self.user) | Q(is_share=True))

    def get_list_display(self):
        list_display = super(BookmarkAdmin, self).get_list_display()
        if not self.user.is_superuser:
            list_display.remove('user')
        return list_display

    def has_change_permission(self, obj=None):
        if not obj or self.user.is_superuser:
            return True
        else:
            return obj.user == self.user


@widget_manager.register
class BookmarkWidget(PartialBaseWidget):
    widget_type = _('bookmark')
    widget_icon = 'fa fa-bookmark'
    description = _(
        'Bookmark Widget, can show user\'s bookmark list data in widget.')
    template = "xadmin/widgets/list.html"

    bookmark = ModelChoiceField(
        label=_('Bookmark'), queryset=Bookmark.objects.all(), required=False)

    def setup(self):
        BaseWidget.setup(self)

        bookmark = self.cleaned_data['bookmark']
        model = bookmark.content_type.model_class()
        data = QueryDict(bookmark.query)
        self.bookmark = bookmark

        if not self.title:
            self.title = smart_text(bookmark)

        req = self.make_get_request("", data.items())
        self.list_view = self.get_view_class(
            ListAdminView, model, list_per_page=10, list_editable=[])(req)

    def has_perm(self):
        return True

    def context(self, context):
        list_view = self.list_view
        list_view.make_result_list()

        base_fields = list_view.base_list_display
        if len(base_fields) > 5:
            base_fields = base_fields[0:5]

        context['result_headers'] = [c for c in list_view.result_headers(
        ).cells if c.field_name in base_fields]
        context['results'] = [
            [o for i, o in enumerate(filter(
                lambda c: c.field_name in base_fields,
                r.cells
            ))]
            for r in list_view.results()
        ]
        context['result_count'] = list_view.result_count
        context['page_url'] = self.bookmark.url

site.register(Bookmark, BookmarkAdmin)
site.register_plugin(BookmarkPlugin, ListAdminView)
site.register_modelview(r'^bookmark/$', BookmarkView, name='%s_%s_bookmark')
