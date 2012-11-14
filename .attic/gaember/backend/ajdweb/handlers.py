# -*- coding: utf-8 -*-

from json import dumps
from webapp2 import RequestHandler


class Base(RequestHandler):

    ''' The base handler '''

    def __init__(self, request, response):
        ''' Initialize to get hold of a reference to the datastore '''

        self.initialize(request, response)
        self.datastore = request.app.registry.get('datastore')

    def options(self, arg1=None, arg2=None):
        ''' Respond to the OPTIONS call made before a CORS request '''

        self._headers()

    def get(self, arg1, arg2=None):
        ''' The GET response handler '''

        (key, value) = self.get_value(arg1, arg2)

        if value:
            self._headers()
            self.response.write(dumps({key: value}))
        else:
            self.response.set_status(404)

    def _headers(self):
        ''' Add the headers in the configuration to the response '''

        for (header, value) in self.request.app.config['handlers']['headers'].iteritems():
            self.response.headerlist.append((header.encode('ascii'), value.encode('ascii')))


class List(Base):

    ''' Gets the values for /api/tags and /api/pages'''

    def get_value(self, kind, ignore):
        ''' Responds to /api/<kind> where 'kind' is one of 'pages' or 'tags' '''

        value = (self.datastore.get_pages() if kind == 'pages' else self.datastore.get_tags())
        return (kind, value)


class Item(Base):

    ''' Gets the value of a specific item: /api/tags/<item>'''

    def get_value(self, kind, item):
        ''' Responds to /api/<kind>s/<item> where 'kind' is one of 'page' or 'tag' '''

        value = (self.datastore.get_page(item) if kind == 'page' else self.datastore.get_tag(item))
        return (kind, value)


class Content(Base):

    ''' Gets the content matter. '''

    def get_value(self, id, ignore):
        ''' Responds to /api/contents/<id> - where 'id' identifies the requested content '''

        return ('content', self.datastore.content_of(id))


class Synchronize(RequestHandler):

    ''' Synchronizes the datastore with the repository '''

    def post(self):
        ''' The trigger to synchronize '''

        datastore = self.request.app.registry.get('datastore')
        repository = self.request.app.registry.get('repository')
        repository.refresh()
        self.response.write(dumps({'updates': datastore.synchronize(repository)}))
