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
        if path:
            page = self.db.content_of(path)
            if page:
                self.render_response('page.html', **page)
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
