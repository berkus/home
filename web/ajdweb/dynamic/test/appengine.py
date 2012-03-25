# -*- coding: utf-8 -*-

import unittest
from datetime import datetime
from dynamic.backends import _appengine
from google.appengine.ext import testbed
from dynamic.appengine import Page, Version


class MockRepo:

    def __init__(self, config):
        self._version = config['version']
        self._pages = {}
        for p in config['pages'].split(';'):
            elems = p.split(':')
            self._pages[elems[0]] = elems[1]

    def version(self):
        return self._version

    def pages(self):
        return set(self._pages.iterkeys())

    def version_of(self, p):
        return self._pages[p]

    def content_of(self, p):
        return (
            True,
            '07 September 2011',
            p,
            'क ख ग',
            'this is test content',
            self._pages[p],
            )


class AppEngineTest(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.db = _appengine()
        self.repo = MockRepo({'version': '123', 'pages': 'unit-test-1:abc;unit-test-2:def'})
        self.db.synchronize(self.repo)

    def tearDown(self):
        self.testbed.deactivate()

    def test_synchronize(self):
        self.assertEquals(self.db.version(), self.repo.version())
        self.assertEquals(len(self.db.pages()), 2)
        self.assertEquals(self.db.version_of('unit-test-1'), 'abc')

    def test_update(self):
        newrepo = MockRepo({'version': '124', 'pages': 'unit-test-1:def;/foo/bar/unit-test-3:pqr'})
        self.assertEquals(self.db.synchronize(newrepo)[0], '124')
        self.assertEquals(len(self.db.pages()), 2)
        self.assertEquals(self.db.version_of('unit-test-1'), 'def')

    def test_getpage(self):
        newrepo = MockRepo({'version': '124', 'pages': '/top/mid/leaf1:ver;/top/mid/leaf2:ver'})
        self.assertEquals(self.db.synchronize(newrepo)[0], '124')
        self.assertEquals(self.db.content_of('badpage'), None)
        content = self.db.content_of('/top/mid/leaf1')
        self.assertEquals(len(content), 7)
        self.assertEquals(content['url'],'/top/mid/leaf1')
        self.assertEquals(content['breadcrumb'],['/','/top/','/top/mid/'])
        self.assertEquals(content['today'].day,datetime.today().day)

    def test_getindex(self):
        newrepo = MockRepo({'version': '124', 'pages': '/top/mid1/leaf1:ver;/top/mid1/leaf2:ver;/top/mid2/leaf3:ver'})
        self.assertEquals(self.db.synchronize(newrepo)[0], '124')
        self.assertEquals(len(self.db.index_of('/')['pages']), 3)
        self.assertEquals(len(self.db.index_of('/top/mid1')['pages']), 2)
        self.assertEquals(len(self.db.index_of('/top/mid2')['pages']), 1)
        self.assertEquals(len(self.db.index_of('/top/bad')['pages']), 0)
        #self.assertEquals(self.db.index_of('/top/bad'), None)
