# -*- coding: utf-8 -*-

from backends import database, repository
from webapp2 import RequestHandler, cached_property


class BaseHandler(RequestHandler):

    def __init__(self, request, response):
        self.initialize(request, response)

    @cached_property
    def db(self):
        return database()


class UpdateHandler(BaseHandler):

    def get(self):
        self.response.write(str(self.db.synchronize(repository())))


class PageHandler(BaseHandler):

    def get(self, path):
        if path:
            content = self.db.content_of(path)
            if content:
                self.response.write(content['content'])
            else:
                self.abort(404)
        else:
            self.response.write('homepage')


class IndexHandler(BaseHandler):

    def get(self, cat):
        for page in [p for p in self.db.pages() if p.startswith(cat)]:
            content = self.db.content_of(page)
            self.response.write('<li>')
            self.response.write(content['title'])
            self.response.write('</li>')
