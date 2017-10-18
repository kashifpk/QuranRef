import sys
import os
from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
from pyramid.renderers import JSON

from .routes import application_routes

from . import graph_models


def do_config(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    load_project_settings()

    session_factory = SignedCookieSessionFactory(settings.get('session.secret', 'hello'))

    config = Configurator(session_factory=session_factory, settings=settings)
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
    config.scan()

    return config


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    config = do_config(global_config, **settings)

    return config.make_wsgi_app()


def load_project_settings():
    here = os.path.dirname(__file__)
    sys.path.insert(0, here)
