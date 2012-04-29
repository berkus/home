# -*- coding: utf-8 -*-

from jinja2 import Markup
from datetime import datetime
from database import Database

from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Date, DateTime, String, UnicodeText, create_engine

Base = declarative_base()


class Page(Base):

    __tablename__ = 'pages'
    id = Column(String, primary_key=True)
    date = Column(Date)
    title = Column(UnicodeText)
    summary = Column(UnicodeText)
    content = Column(UnicodeText)
    version = Column(String)

    def __init__(self, p, contents):
        self.id = p
        self.date = datetime.strptime(contents[1], '%d %B %Y').date()
        self.title = contents[2]
        self.summary = contents[3]
        self.content = contents[4]
        self.version = contents[5]

    def content(self):
        return {
            'url': self.id,
            'date': self.date,
            'title': Markup(self.title),
            'summary': Markup(self.summary),
            'content': Markup(self.content),
            'breadcrumb': _breadcrumb(self.id),
            'today': datetime.today(),
            }


class Version(Base):

    __tablename__ = 'version'
    id = Column(String, primary_key=True)
    changes = Column(String)
    timestamp = Column(DateTime)

    def __init__(self, version, updates):
        self.id = version
        self.changes = 'change'
        self.timestamp = datetime.now()


class SqlDb(Database):

    def __init__(self, config):
        self._engine = create_engine(config['DB'], echo=config['DEBUG'])
        self._sessionmaker = sessionmaker(bind=self._engine)
        Base.metadata.create_all(self._engine)

    def version(self):
        session = self._sessionmaker()
        l = session.query(Version).order_by(desc(Version.timestamp)).first()
        session.close()
        return (l.id if l else None)

    def pages(self):
        session = self._sessionmaker()
        result = set([k.id for k in session.query(Page.id).all()])
        session.close()
        return result

    def add(self, p, contents):
        if contents[0]:
            session = self._sessionmaker()
            session.add(Page(p, contents))
            session.commit()
            session.close()
            return ('add', p)

    def remove(self, p):
        session = self._sessionmaker()
        session.query(Page).filter(Page.id == p).delete()
        session.commit()
        session.close()
        return ('remove', p)

    def change(self, p, contents):
        self.remove(p)
        self.add(p, contents)
        return ('change', p)

    def record(self, version, updates):
        session = self._sessionmaker()
        session.add(Version(version, updates))
        session.commit()
        session.close()
        return (version, updates)

    def _page(self, p):
        try:
            session = self._sessionmaker()
            page = session.query(Page).filter(Page.id == p).one()
            session.close()
        except:
            page = None
        return page

    def content_of(self, p):
        page = self._page(p)
        return (page.content() if page else None)

    def version_of(self, p):
        page = self._page(p)
        return (page.version if page else None)

    def index_of(self, cat):
        index = {
            'url': cat,
            'pages': [],
            'date': datetime.today(),
            'breadcrumb': _breadcrumb(cat),
            'today': datetime.today(),
            }
        for p in self.pages():
            print p
            if p.startswith(cat):
                index['pages'].append(self.content_of(p))
        return index


def _breadcrumb(p):
    breadcrumb = ['/']
    for crumb in p.split('/')[1:-1]:
        breadcrumb.append(breadcrumb[-1] + crumb + '/')
    return breadcrumb
