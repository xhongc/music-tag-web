
PLUGINS = (
    'actions',
    'filters',
    'bookmark',
    'export',
    'layout',
    'refresh',
    'details',
    'editable',
    'relate',
    'chart',
    'ajax',
    'relfield',
    'inline',
    'topnav',
    'portal',
    'quickform',
    'wizard',
    'images',
    'auth',
    'multiselect',
    'themes',
    'aggregation',
    # 'mobile',
    'passwords',
    'sitemenu',
    'language',
    'quickfilter',
    'sortablelist',
    'importexport'
)


def register_builtin_plugins(site):
    from importlib import import_module
    from django.conf import settings

    exclude_plugins = getattr(settings, 'XADMIN_EXCLUDE_PLUGINS', [])

    [import_module('xadmin.plugins.%s' % plugin) for plugin in PLUGINS if plugin not in exclude_plugins]
