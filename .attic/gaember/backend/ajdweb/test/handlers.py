# -*- coding: utf-8 -*-

from json import loads
from webapp2 import Request


class HandlersTest:

    bad_urls = [
        '/',
        '/foo',
        '/api/bad',
        '/api/pages/bad',
        '/api/tags/bad',
        '/api/content/bad',
        ]

    good_urls = [
        '/api/tags',
        '/api/pages',
        '/api/tags/foo',
        '/api/pages/page',
        '/api/pages/page_1',
        '/api/contents/foo/root',
        '/api/contents/bar/subbar/tagged',
        ]

    def test_bad_requests(self):
        for method in ['OPTIONS', 'GET']:
            for url in HandlersTest.bad_urls:
                request = Request.blank(url)
                response = request.get_response(self.api)
                self.assertEqual(response.status_int, 404)

    def test_headers(self):
        for url in HandlersTest.good_urls:
            for method in ['OPTIONS', 'GET']:
                request = Request.blank(url)
                request.method = method
                response = request.get_response(self.api)
                self.assertEqual(response.status_int, 200)
                for (k, v) in self.api.config['handlers']['headers'].iteritems():
                    self.assertEqual(response.headers.get(k), v)

    def test_get_pages(self):
        request = Request.blank('/api/pages')
        response = loads(request.get_response(self.api).body)
        self.assertEqual(len(response), 1)
        self.assertEqual(len(response['pages']), 7)

        request = Request.blank('/api/pages/' + response['pages'][0]['id'])
        response = loads(request.get_response(self.api).body)
        self.assertEqual(len(response), 1)

        content_id = response['page']['content_id']
        request = Request.blank('/api/contents/' + content_id)
        response = loads(request.get_response(self.api).body)
        self.assertEqual(len(response), 1)
        self.assertEqual(response['content']['id'], content_id)

    class MockRepo:

        def __init__(self, content, version='ver'):
            self.contents = content
            self.ver = version

        def refresh(self):
            pass

        def ids(self):
            return set(self.contents.iterkeys())

        def version(self):
            return self.ver

        def content_of(self, e):
            return self.contents[e][1]

        def version_of(self, e):
            return self.contents[e][0]

    def test_get_tags(self):
        request = Request.blank('/api/tags')
        response = loads(request.get_response(self.api).body)
        self.assertEqual(len(response), 1)
        self.assertEqual(len(response['tags']), 4)

        request = Request.blank('/api/tags/' + response['tags'][0]['id'])
        response = loads(request.get_response(self.api).body)
        self.assertEqual(len(response), 1)

        content_id = response['tag']['content_id']
        request = Request.blank('/api/contents/' + content_id)
        response = loads(request.get_response(self.api).body)
        self.assertEqual(len(response), 1)
        self.assertEqual(response['content']['id'], content_id)

    def test_empty_sync(self):
        request = Request.blank('/api/sync')
        request.method = 'POST'
        response = request.get_response(self.api)
        updates = loads(response.body)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(len(updates['updates']), 0)

    def test_sync(self):
        request = Request.blank('/api/sync')
        request.method='POST'
        repo = self.api.registry.get('repository')
        newcontent = {
            'foo/root': (repo.version_of('bar/root'), repo.content_of('bar/root')),
            'foo/subfoo/root': ('changed', repo.content_of('foo/subfoo/root')),
            'foo/new': ('changed', repo.content_of('foo/root')),
            'bar/subbar/birthday': ('changed', repo.content_of('bar/subbar/tagged')),
            'bar/root': (repo.version_of('bar/root'), repo.content_of('foo/root')),
            }
        self.api.registry['repository'] = HandlersTest.MockRepo(newcontent)
        response = request.get_response(self.api)
        updates = loads(response.body)['updates']

        self.assertEqual(len(updates), 11)
        self.assertTrue(['add', 'foo/new'] in updates)
        self.assertTrue(['update', 'foo/root'] in updates)
        self.assertFalse(['update', 'bar/root'] in updates)
