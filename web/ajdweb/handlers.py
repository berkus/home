# -*- coding: utf-8 -*-

from webapp2_extras import jinja2
from os.path import dirname, join
from backends import database, repository
from webapp2 import RequestHandler, cached_property


class BaseHandler(RequestHandler):

    def __init__(self, request, response):
        self.initialize(request, response)

    @cached_property
    def db(self):
        return database()

    @cached_property
    def jinja2(self):
        jinja2.default_config['template_path'] = join(dirname(__file__), 'templates')
        return jinja2.get_jinja2(app=self.app)

    def render_response(self, _template, **context):
        rv = self.jinja2.render_template(_template, **context)
        self.response.write(rv)


class UpdateHandler(BaseHandler):

    def get(self):
        self.response.write(str(self.db.synchronize(repository())))


class PageHandler(BaseHandler):

    def get(self, path):
        if len(path) > 0:
            page = self.db.content_of(path)
            if page:
                self.render_response('page', **page)
            else:
                page = self.db.index_of(path)
                if page:
                    self.render_response('index', **page)
                else:
                    self.abort(404)
        else:
            page = self.db.top()
            self.render_response('home', **page)
