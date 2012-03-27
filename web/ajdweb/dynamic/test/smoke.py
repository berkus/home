# -*- coding: utf-8 -*-

import unittest
from jinja2 import Markup
from datetime import datetime
from google.appengine.ext import testbed
from dynamic.appengine import Page, Version
from dynamic.backends import _appengine, _github, _localgit, _sqldb


class SmokeTest(unittest.TestCase):

    def test_smoke(self):
        db = self._database()
        repo = self._repository()
        db.synchronize(repo)
        self.assertTrue(db.pages())
        self.assertIsNotNone(db.content_of(iter(db.pages()).next())['title'])


class DbSql:

    def _database(self):
        return _sqldb()


class DbAppEngine(SmokeTest):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()

    def _database(self):
        return _appengine()


class RepoGithub:

    def _repository(self):
        return _github()


class RepoLocalGit:

    def _repository(self):
        return _localgit()


class AppEngineWithGithub(DbAppEngine, RepoGithub):

    pass


class AppEngineWithLocalGit(DbAppEngine, RepoLocalGit):

    pass


class SqlDbWithLocalGit(SmokeTest, DbSql, RepoLocalGit):

    pass


class SqlDbWithGithub(SmokeTest, DbSql, RepoLocalGit):

    pass
