# -*- coding: utf-8 -*-

''' A content datastore with Google App Engine backend. '''

from datastore import Datastore
from google.appengine.ext import db


class Content(db.Model):

    summary = db.TextProperty()
    matter = db.TextProperty()
    title = db.StringProperty(required=True)
    url_id = db.StringProperty(required=True)
    version = db.StringProperty(required=True)


class Page(db.Model):

    date = db.DateProperty()
    tags = db.StringListProperty()
    content = db.ReferenceProperty(Content, required=True)


class Tag(db.Model):

    pages = db.StringListProperty()
    parent_tag = db.StringProperty()
    children = db.StringListProperty()
    content = db.ReferenceProperty(Content)


class Version(db.Model):

    changes = db.StringListProperty(required=True)
    timestamp = db.DateTimeProperty(auto_now_add=True)


class GaeStore(Datastore):

    def __init__(self, config):
        pass

    def version(self):
        l = db.Query(Version, keys_only=True).order('-timestamp').get()
        return (l.name() if l else None)

    def ids(self):
        return set([k.name() for k in Content.all(keys_only=True)])

    def content_of(self, e):
        ''' Returns the content of the given entry '''

        content = Content.get_by_key_name(e)
        return {'id': e, 'matter': (content.matter if content else None)}

    def version_of(self, e):
        ''' Returns the content of the given entry '''

        content = Content.get_by_key_name(e)
        return (content.version if content else None)

    def record_change(self, version, updates):
        Version(key_name=version, changes=[' '.join([p[0], p[1]]) for p in updates]).put()

    def get_pages(self):
        pages = db.Query(Page).order('-date').run()
        return [self.get_page(p.key().name(), p) for p in pages if p.content]

    def get_page(self, p, entry=None):
        if not entry:
            entry = Page.get_by_key_name(p)

        if not entry or not entry.content:
            return None

        page = {'id': p, 'content_id': entry.content.key().name()}
        page['tags'] = entry.tags
        page['title'] = entry.content.title
        page['summary'] = entry.content.summary
        page['date'] = entry.date.strftime('%Y-%m-%d')

        return page

    def get_tags(self):
        return [self.get_tag(p.key().name(), p) for p in db.Query(Tag).run() if p.content]

    def get_tag(self, t, entry=None):
        if not entry:
            entry = Tag.get_by_key_name(t)

        if not entry or not entry.content:
            return None

        tag = {'id': t, 'content_id': entry.content.key().name()}
        tag['title'] = entry.content.title
        tag['summary'] = entry.content.summary
        tag['pages'] = entry.pages
        tag['parent_id'] = entry.parent_tag
        tag['children'] = entry.children
        return tag

    def add(self, e, version, data, url_id=None):
        ''' Adds the passed entry into the datastore'''

        entry = self.extract(e, data)

        if not entry.title:
            return

        if not url_id:
            dedup = 1
            dedup_id = entry.url_id

            existing_url_ids = [k.name() for k in Page.all(keys_only=True)]
            existing_url_ids.append([k.name() for k in Tag.all(keys_only=True)])

            while dedup_id in existing_url_ids:
                dedup_id = '{0}_{1}'.format(entry.url_id, dedup)
                dedup = dedup + 1

            entry.url_id = dedup_id
        else:
            entry.url_id = url_id

        # create or update the content entry.
        content = Content.get_by_key_name(e)
        if content:
            content.version = version
            content.url_id = entry.url_id
            content.title = entry.title.decode('utf-8')
            content.matter = entry.matter.decode('utf-8')
            content.summary = entry.summary.decode('utf-8')
        else:
            content = Content(
                key_name=e,
                version=version,
                date=entry.date,
                url_id=entry.url_id,
                title=entry.title.decode('utf-8'),
                matter=entry.matter.decode('utf-8'),
                summary=entry.summary.decode('utf-8'),
                )

        # create the page/tag entry.
        item = None
        if entry.is_tag:
            item = Tag.get_or_insert(entry.url_id)
            item.content = content
            if len(entry.tags):
                parent = entry.tags[0]
                item.parent_tag = parent
                tag = Tag.get_or_insert(parent)
                if entry.url_id not in tag.children:
                    tag.children.append(entry.url_id)
                    tag.put()
        else:
            item = Page.get_or_insert(entry.url_id, content=content)
            item.tags = entry.tags
            item.date = entry.date
            for t in entry.tags:
                tag = Tag.get_or_insert(t)
                if entry.url_id not in tag.pages:
                    tag.pages.append(entry.url_id)
                    tag.put()

        content.put()
        item.put()

    def remove(self, e):
        content = Content.get_by_key_name(e)
        entry = Datastore.Entry(e)
        entry.url_id = content.url_id
        if entry.is_tag:
            tag = Tag.get_by_key_name(entry.url_id)
            if tag.parent_tag:
                parent = Tag.get_by_key_name(tag.parent_tag)
                if parent:
                    parent.children.remove(entry.url_id)
                    parent.put()
            tag.delete()
        else:
            page = Page.get_by_key_name(entry.url_id)
            for t in page.tags:
                tag = Tag.get_by_key_name(t)
                if tag:
                    tag.pages.remove(entry.url_id)
                    tag.put()
            page.delete()
        content.delete()

    def update(self, e, version, data):
        content = Content.get_by_key_name(e)
        self.add(e, version, data, content.url_id)
