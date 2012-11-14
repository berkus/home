# -*- coding: utf-8 -*-

from redis import StrictRedis
from datastore import Datastore


class RedisStore(Datastore):

    ''' A datastore implementation with Redis at the backend. '''

    def __init__(self, config):
        ''' Initializes the connection to the backend '''

        connection = config['redis']['connection']

        db = config['redis']['db']
        host = config['redis']['host']
        port = config['redis']['port']
        self.redis = StrictRedis(host=host, port=port, db=db)

    def version(self):
        ''' Returns the current datastore version '''

        return self.redis.get('version')

    def ids(self):
        ''' Returns the set of entries in the datastore '''

        return set(self.redis.smembers('ids'))

    def content_of(self, e):
        ''' Returns the content of the given entry '''

        return {'id': e, 'matter': self.redis.hget(e, 'matter')}

    def version_of(self, e):
        ''' Returns the version of the given entry '''

        return self.redis.hget(e, 'version')

    def record_change(self, ver, changes):
        ''' Sets the version of the datastore '''

        self.redis.set('version', ver)

    def get_pages(self):
        ''' Returns an index of all pages in the datastore. '''

        return [self.get_page(p, e) for (p, e) in self.redis.hgetall('pages').iteritems()]

    def get_tags(self):
        ''' Returns an index of all tags in the datastore. '''

        return [self.get_tag(t, e) for (t, e) in self.redis.hgetall('tags').iteritems()]

    def get_page(self, p, entry=None):
        ''' Returns the attributes for a single page. Only the attributes and not the content are
        returned. The content itself can be retrieved using content_of(page.content_id)'''

        if not entry:
            entry = self.redis.hget('pages', p)

        if not entry:
            return None

        page = {'id': p, 'content_id': entry}

        command = self.redis.pipeline()
        command.hget(entry, 'date')
        command.hget(entry, 'tags')
        command.hget(entry, 'title')
        command.hget(entry, 'summary')
        attrs = command.execute()

        page['date'] = attrs[0]
        page['title'] = attrs[2]
        page['summary'] = attrs[3]
        page['tags'] = attrs[1].split(',')
        return page

    def get_tag(self, t, entry=None):
        ''' Returns the attributes for a single tag. Only the attributes and not the content are
        returned. The content itself can be retrieved using content_of(tag.content_id)'''

        if not entry:
            entry = self.redis.hget('tags', t)

        if not entry:
            return None

        tag = {'id': t, 'content_id': entry}

        command = self.redis.pipeline()
        command.hget(entry, 'tags')
        command.hget(entry, 'title')
        command.hget(entry, 'summary')
        command.smembers('tag_children_' + t)
        command.smembers('pages_tagged_' + t)
        attrs = command.execute()

        tag['title'] = attrs[1]
        tag['summary'] = (attrs[2] if attrs[2] else None)
        tag['pages'] = (list(attrs[4]) if attrs[4] else None)
        tag['children'] = (list(attrs[3]) if attrs[3] else None)
        tag['parent_id'] = (attrs[0] if attrs[0] and len(attrs[0]) else None)

        return tag

    def add(self, e, version, data):
        ''' Adds the passed entry into the datastore'''

        entry = self.extract(e, data)

        if not entry.title:  # don't need entries without a title
            return

        command = self.redis.pipeline()
        storehash = ('tags' if entry.is_tag else 'pages')

        dedup = 1
        dedup_id = entry.url_id
        while self.redis.hexists(storehash, dedup_id):
            dedup_id = '{0}_{1}'.format(entry.url_id, dedup)
            dedup = dedup + 1

        entry.url_id = dedup_id

        command.hset(e, 'version', version)
        command.hset(e, 'date', entry.date)
        command.hset(e, 'title', entry.title)
        command.hset(e, 'matter', entry.matter)
        command.hset(e, 'url_id', entry.url_id)
        command.hset(e, 'summary', entry.summary)
        command.hset(e, 'tags', ','.join(entry.tags))

        if entry.tags:
            if entry.is_tag:
                command.sadd('tag_children_' + entry.tags[0], entry.url_id)
            else:
                for tag in entry.tags:
                    command.sadd('pages_tagged_' + tag, entry.url_id)

        command.sadd('ids', e)
        command.hset(storehash, entry.url_id, e)
        command.execute()

    def remove(self, e):
        ''' Remove an entry from the datastore '''

        entry = Datastore.Entry(e)
        entry.url_id = self.redis.hget(e, 'url_id')

        command = self.redis.pipeline()
        if entry.is_tag:
            command.hdel('tags', entry.url_id)
            command.delete('tag_children_' + entry.url_id)
            command.delete('pages_tagged_' + entry.url_id)
            if entry.tags:
                command.srem('tag_children_' + entry.tags[0], entry.url_id)
        else:
            command.hdel('pages', entry.url_id)
            for tag in entry.tags:
                command.srem('pages_tagged_' + tag, entry.url_id)

        command.srem('ids', e)
        command.execute()

    def update(self, e, version, data):

        entry = Datastore.Entry(e)
        entry.url_id = self.redis.hget(e, 'url_id')
        storehash = ('tags' if entry.is_tag else 'pages')
        self.redis.hdel(storehash, entry.url_id)
        self.add(e, version, data)

    def clear(self):
        self.redis.flushall()
