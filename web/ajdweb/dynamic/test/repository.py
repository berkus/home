# -*- coding: utf-8 -*-

import unittest
from dynamic.backends import _github, _localgit


class RepoTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.repo = cls._repository()

    def test_version(self):
        self.assertEquals(len(self.repo.version()), 40)

    def test_load_pages(self):
        page = iter(self.repo.pages()).next()
        self.assertEquals(len(self.repo.version_of(page)), 40)
        self.assertTrue(self.repo.content_of(page)[0])


class GithubTest(RepoTest):

    @classmethod
    def _repository(cls):
        return _github()


class LocalGitTest(RepoTest):

    @classmethod
    def _repository(cls):
        return _localgit()
