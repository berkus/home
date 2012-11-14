# -*- coding: utf-8 -*-

from unittest import TestCase
from ajdweb import load_config
from ajdweb.github import Github
from ajdweb.filesystem import Directory


class GithubTest(TestCase):

    config = load_config('test.json')
    repo = Github(config)
    fsrepo = Directory(config)

    def setUp(self):
        self.repo = GithubTest.repo
        self.fsrepo = GithubTest.fsrepo

    def test_ids(self):
        self.assertEqual(len(self.repo.ids()), len(self.fsrepo.ids()))

    def test_version(self):
        self.assertEqual(len(self.repo.version()), 40)
        self.assertEqual(len(self.repo.version_of('foo/root')), 40)

    def test_content_of(self):
        self.assertEqual(self.repo.content_of('foo/root'), self.fsrepo.content_of('foo/root'))
