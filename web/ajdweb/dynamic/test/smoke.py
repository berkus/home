# -*- coding: utf-8 -*-

import unittest
from jinja2 import Markup
from datetime import datetime
from google.appengine.ext import testbed
from dynamic.appengine import Page, Version
from dynamic.backends import database, repository

class SmokeTest(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.db = database()
        self.repo = repository()
        self.db.synchronize(self.repo)
        print self.db.pages()

    def test_getpage(self):
        contents=self.db.content_of('/tech/emacs_devanagari')
        self.assertEquals(contents['title'],Markup(u'Writing in हिन्दी'))
