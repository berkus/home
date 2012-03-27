# -*- coding: utf-8 -*-


def _appengine():
    from appengine import AppEngine
    return AppEngine()


def _github():
    from github import GitHub
    config = {'REPO': 'https://api.github.com/repos/aldrin/home', 'BRANCH': 'web/html'}
    return GitHub(config)


def _localgit():
    from localgit import LocalGit
    config = {'REPO': '/tmp/dummy', 'BRANCH': 'pages/html'}
    return LocalGit(config)


def _sqldb():
    from sqldb import SqlDb
    config = {'DB': 'sqlite:///:memory:', 'DEBUG': False}
    return SqlDb(config)


def database():
    return _appengine()


def repository():
    return _github()
