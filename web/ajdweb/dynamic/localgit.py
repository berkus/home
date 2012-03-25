# -*- coding: utf-8 -*-

from git import Repo


class LocalGit:

    def __init__(self, config):
        repo = config.get('REPO')
        branch = config.get('BRANCH')

    def version(self):
        pass

    def pages(self):
        pass

    def version_of(self, p):
        pass

    def content_of(self, p):
        pass
