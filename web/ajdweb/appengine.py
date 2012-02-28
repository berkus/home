# -*- coding: utf-8 -*-

from jinja2 import Markup
from datetime import datetime
from database import Database
from google.appengine.ext import db
from google.appengine.api import memcache


class Page(db.Model):

    date = db.DateProperty(required=True)
    title = db.StringProperty(required=True)
    summary = db.TextProperty(required=True)
    content = db.TextProperty(required=True)
    version = db.StringProperty(required=True)


class Version(db.Model):

    changes = db.StringListProperty(required=True)
    timestamp = db.DateTimeProperty(auto_now_add=True)


class AppEngine(Database):

    def version(self):
        l = db.Query(Version, keys_only=True).order('-timestamp').get()
        return (l.name() if l else None)

    def pages(self):
        return set([k.name() for k in Page.all(keys_only=True)])

    def version_of(self, p):
        page = Page.get_by_key_name(p)
        return (page.version if page else None)

    def add(self, p, contents):
        if contents[0]:
            page = Page(
                key_name=p,
                date=datetime.strptime(contents[1], '%d %B %Y').date(),
                title=db.Text(contents[2], 'utf-8'),
                summary=db.Text(contents[3], 'utf-8'),
                content=db.Text(contents[4], 'utf-8'),
                version=contents[5],
                )
            page.put()
            return ('add', p)

    def remove(self, p):
        page = Page.get_by_key_name(p)
        if page:
            page.delete()
            return ('remove', p)

    def change(self, p, contents):
        self.remove(p)
        self.add(p, contents)
        return ('change', p)

    def record(self, version, updates):
        Version(key_name=version, changes=[' '.join([p[0], p[1]]) for p in updates]).put()
        return (version, updates)

    def content_of(self, p):
        page = Page.get_by_key_name(p)
        return ({
            'url': p,
            'date': page.date,
            'title': Markup(page.title),
            'summary': Markup(page.summary),
            'content': Markup(page.content),
            'breadcrumb': self._breadcrumb(p),
            } if page else None)

    def index_of(self, cat):
        index = {
            'url': cat,
            'index': [],
            'date': datetime.today(),
            'breadcrumb': self._breadcrumb(cat),
            }
        for p in self.pages():
            if p.startswith(cat):
                index['index'].append(self.content_of(p))
        return index

    def _breadcrumb(self, p):
        breadcrumb = ['/']
        for crumb in p.split('/')[1:-1]:
            breadcrumb.append(breadcrumb[-1] + crumb)
        return breadcrumb
