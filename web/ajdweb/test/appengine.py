# -*- coding: utf-8 -*-

import unittest
from datetime import datetime
from ajdweb.backends import _appengine
from google.appengine.ext import testbed
from ajdweb.appengine import Page, Version


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
        self.testbed.init_memcache_stub()
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
        newrepo = MockRepo({'version': '124', 'pages': 'unit-test-1:def;unit-test-3:pqr'})
        self.assertEquals(len(self.db.synchronize(newrepo)), 3)  # 3 changes, 1 add, 1 remove, 1 change
        self.assertEquals(len(self.db.pages()), 2)
        self.assertEquals(self.db.version_of('unit-test-1'), 'def')
