# -*- coding: utf-8 -*-

def _appengine():
    from appengine import AppEngine
    return AppEngine()


def _github():
    from github import GitHub
    config = {'REPO': 'https://api.github.com/repos/aldrin/home', 'BRANCH': 'web/html'}
    return GitHub(config)


def database():
    return _appengine()


def repository():
    return _github()