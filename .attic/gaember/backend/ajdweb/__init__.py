# -*- coding: utf-8 -*-

''' Web Content Generator '''

from json import load
from webapp2 import WSGIApplication
from os.path import join, abspath, dirname


def load_config(cfgfile='config.json'):
    ''' Load configuration from the passed file '''

    return load(open(abspath(join(dirname(dirname(__file__)), cfgfile))))


def initialize(config, datastore, repository):
    ''' Initializes the WSGI application with the passed configuration and datastore/repo '''

    routes = [(r'/api/(tags|pages)', 'ajdweb.handlers.List')]
    routes.append((r'/api/sync', 'ajdweb.handlers.Synchronize'))
    routes.append((r'/api/contents/(.*)', 'ajdweb.handlers.Content'))
    routes.append((r'/api/(tag|page)s/(.*)', 'ajdweb.handlers.Item'))

    # routes.append((r'/','ajdweb.views.Home'))
    # routes.append((r'/(.*)','ajdweb.views.Page'))
    # routes.append((r'/tag/(.*)','ajdweb.views.Tag'))
    # routes.append((r'/feed/(.*)','ajdweb.views.Feed'))

    app = WSGIApplication(routes=routes, debug=True, config=config)
    app.registry['datastore'] = datastore
    app.registry['repository'] = repository
    datastore.synchronize(repository)
    return app
