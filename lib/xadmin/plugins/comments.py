import xadmin

from xadmin.layout import *
from xadmin.util import username_field

from django.conf import settings
from django.contrib.comments.models import Comment
from django.utils.translation import ugettext_lazy as _, ungettext
from django.contrib.comments import get_model
from django.contrib.comments.views.moderation import perform_flag, perform_approve, perform_delete

class UsernameSearch(object):
    """The User object may not be auth.User, so we need to provide
    a mechanism for issuing the equivalent of a .filter(user__username=...)
    search in CommentAdmin.
    """
    def __str__(self):
        return 'user__%s' % username_field


class CommentsAdmin(object):
    form_layout = (
        Main(
            Fieldset(None,
                'content_type', 'object_pk', 'site',
                css_class='unsort no_title'
            ),
            Fieldset('Content',
                'user', 'user_name', 'user_email', 'user_url', 'comment'
            ),
        ),
        Side(
            Fieldset(_('Metadata'),
                'submit_date', 'ip_address', 'is_public', 'is_removed'
            ),
        )
    )

    list_display = ('name', 'content_type', 'object_pk', 'ip_address', 'submit_date', 'is_public', 'is_removed')
    list_filter = ('submit_date', 'site', 'is_public', 'is_removed')
    ordering = ('-submit_date',)
    search_fields = ('comment', UsernameSearch(), 'user_name', 'user_email', 'user_url', 'ip_address')
    actions = ["flag_comments", "approve_comments", "remove_comments"]
    model_icon = 'fa fa-comment'

    def get_actions(self):
        actions = super(CommentsAdmin, self).get_actions()
        # Only superusers should be able to delete the comments from the DB.
        if not self.user.is_superuser and 'delete_selected' in actions:
            actions.pop('delete_selected')
        if not self.user.has_perm('comments.can_moderate'):
            if 'approve_comments' in actions:
                actions.pop('approve_comments')
            if 'remove_comments' in actions:
                actions.pop('remove_comments')
        return actions

    def flag_comments(self, request, queryset):
        self._bulk_flag(queryset, perform_flag,
                        lambda n: ungettext('flagged', 'flagged', n))
    flag_comments.short_description = _("Flag selected comments")
    flag_comments.icon = 'flag'

    def approve_comments(self, request, queryset):
        self._bulk_flag(queryset, perform_approve,
                        lambda n: ungettext('approved', 'approved', n))
    approve_comments.short_description = _("Approve selected comments")
    approve_comments.icon = 'ok'

    def remove_comments(self, request, queryset):
        self._bulk_flag(queryset, perform_delete,
                        lambda n: ungettext('removed', 'removed', n))
    remove_comments.short_description = _("Remove selected comments")
    remove_comments.icon = 'remove-circle'

    def _bulk_flag(self, queryset, action, done_message):
        """
        Flag, approve, or remove some comments from an admin action. Actually
        calls the `action` argument to perform the heavy lifting.
        """
        n_comments = 0
        for comment in queryset:
            action(self.request, comment)
            n_comments += 1

        msg = ungettext('1 comment was successfully %(action)s.',
                        '%(count)s comments were successfully %(action)s.',
                        n_comments)
        self.message_user(msg % {'count': n_comments, 'action': done_message(n_comments)}, 'success')

# Only register the default admin if the model is the built-in comment model
# (this won't be true if there's a custom comment app).
if 'django.contrib.comments' in settings.INSTALLED_APPS and (get_model() is Comment):
    xadmin.site.register(Comment, CommentsAdmin)
