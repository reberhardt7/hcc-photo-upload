import os

from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('upload', '/upload')
    config.add_route('authorize_gdrive', '/authorize_gdrive')
    oauth2callback_path = os.environ['OAUTH_CALLBACK_PATH']
    if not oauth2callback_path.startswith('/'):
        oauth2callback_path = '/' + oauth2callback_path
    config.add_route('oauth2callback', oauth2callback_path)
    config.scan()
    return config.make_wsgi_app()
