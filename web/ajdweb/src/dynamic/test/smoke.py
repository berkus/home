# -*- coding: utf-8 -*-

import unittest
from jinja2 import Markup
from datetime import datetime
from google.appengine.ext import testbed
from dynamic.appengine import Page, Version
from dynamic.backends import _appengine, _github

class SmokeTest(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.db = _appengine()
        self.repo = _github()
        self.db.synchronize(self.repo)

    def test_getpage(self):
        contents=self.db.content_of('/tech/emacs_devanagari')
        self.assertEquals(contents['title'],Markup(u'Writing in हिन्दी'))
