# -*- coding: utf-8 -*-

from jinja2 import Markup
from markdown import markdown
from webapp2_extras import jinja2
from os.path import dirname, join
from webapp2 import RequestHandler, cached_property


class BaseView(RequestHandler):

    def __init__(self, request, response):
        self.initialize(request, response)
        self.datastore = request.app.registry.get('datastore')

    @cached_property
    def jinja2(self):
        jinja2.default_config['template_path'] = join(dirname(__file__), 'templates')
        return jinja2.get_jinja2(app=self.app)

    def render_response(self, template, **context):
        rv = self.jinja2.render_template(template, **context)
        self.response.write(rv)


class Page(BaseView):

    def get(self, p):
        page = self.datastore.get_page(p)
        if page:
            context['title']=page['title']
            context['when']=page['date']


            page['content'] = Markup(markdown(self.datastore.content_of(page['content_id'])['matter']))
            self.render_response('page', **page)
        else:
            self.abort(404)

class Tag(BaseView):
    def get(self, t):
