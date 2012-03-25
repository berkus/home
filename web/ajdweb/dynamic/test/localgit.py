# -*- coding: utf-8 -*-

import unittest
from dynamic.backends import _localgit

class LocalGitTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.localgit = _localgit()

    def test_version(self):
        self.assertEquals(len(self.localgit.version()), 40)

    def test_load_pages(self):
        page = iter(self.localgit.pages()).next()
        self.assertEquals(len(self.localgit.version_of(page)), 40)
        (ok, date, title, summary, html, sha) = self.localgit.content_of(page)
        self.assertTrue(ok)
