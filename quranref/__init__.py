import sys
import os
from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
from pyramid.renderers import JSON

from .routes import application_routes

from .apps import enabled_apps
from . import apps
from . import graph_models

from pyck.ext import add_admin_handler, AdminController
from pyck.lib import get_submodules


def do_config(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    load_project_settings()

    session_factory = SignedCookieSessionFactory(settings.get('session.secret', 'hello'))

    config = Configurator(session_factory=session_factory, settings=settings)
    config.add_tween('quranref.auth.authenticator')
    config.add_renderer('prettyjson', JSON(indent=4))
    config.include('pyramid_mako')
    config.add_view('pyramid.view.append_slash_notfound_view',
                    context='pyramid.httpexceptions.HTTPNotFound')

    # ArangoDB configuration
    graph_models.connect(server=settings['gdb.server'],
                         port=settings['gdb.port'],
                         username=settings['gdb.username'],
                         password=settings['gdb.password'],
                         db_name=settings['gdb.database'])

    application_routes(config)
    configure_app_routes(config)

    all_apps = get_submodules(apps)

    ignored_apps = []
    enabled_app_names = [subapp.APP_NAME for subapp in enabled_apps]
    for app in all_apps:
        if app['is_package'] and app['name'] not in enabled_app_names:
            ignored_apps.append('.apps.' + app['name'])

    config.scan(ignore=ignored_apps)

    return config


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    config = do_config(global_config, **settings)

    return config.make_wsgi_app()


def load_project_settings():
    here = os.path.dirname(__file__)
    sys.path.insert(0, here + '/apps')
    sys.path.insert(0, here)


def configure_app_routes(config):
    """
    Pluggable - Application routes integration
    ==========================================

    Integrates routes for all applications present in the apps folder and enabled (present in the enabled_apps
    list in apps.__init__.py).

    Normally each application is automatically given a route_prefix matching the
    application name. So for example, if you have an application named blog, its route_prefix would be /blog
    and all other application routes will also be prefixed with /blog. If you want to override the route_prefix
    and want the application accessible under some other route prefix (or no route prefix at all), use the
    app_route_prefixes dictionary present in this function to specify an alternate route for the application.
    Specify just / if you want the application routes to be accessible at the same level as the main project's
    routes.
    """

    # The app_route_prefixes dictionary for overriding app route prefixes
    app_route_prefixes = {
        # 'blog': '/myblog'
    }

    for app_module in enabled_apps:
        app_name = app_module.APP_NAME
        app_route_prefix = app_route_prefixes.get(app_name, '/%s' % app_name)

        try:
            config.include(app_module.application_routes, route_prefix=app_route_prefix)
        except Exception as exp:
            print(repr(exp))

        # process global routes for sub apps
        if hasattr(app_module, 'global_routes'):
            config.include(app_module.global_routes)
