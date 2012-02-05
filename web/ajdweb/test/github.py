# -*- coding: utf-8 -*-

import unittest
from ajdweb.backends import _github

class GithubTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.github = _github()

    def test_version(self):
        self.assertEquals(len(self.github.version()), 40)

    def test_load_pages(self):
        page = iter(self.github.pages()).next()
        self.assertEquals(len(self.github.version_of(page)), 40)
        (ok, date, title, summary, html, sha) = self.github.content_of(page)
        self.assertTrue(ok)
