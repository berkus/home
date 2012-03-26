# -*- coding: utf-8 -*-
from git import Repo
from os.path import splitext
from bs4 import BeautifulSoup

class LocalGit:

    def __init__(self, config):
        repo = Repo(config.get('REPO'))
        self._branch = config.get('BRANCH')
        r = repo.head.commit.tree
        for b in self._branch.split('/'):
            for t in r:
                if t.path == b:
                    r = t
                    break
        self._root = r

    def version(self):
        return self._root.hexsha

    def pages(self):
        tree = [t for t in self._root.traverse() if t.type == 'blob']
        self._pages = { splitext(t.path)[0][len(self._branch):] : (t.hexsha, t.abspath) for t in tree }
        return set(self._pages.iterkeys())

    def version_of(self, p):
        return self._pages[p][0]

    def content_of(self, p):
        (sha, path) = self._pages[p]
        raw = BeautifulSoup(file(path).read())
        (title, summary, content) = (raw.h1, raw.p, raw.h1.parent)
        date = raw.find('meta', {'name': 'generated'})['content']
        ok = title and summary and content and date

        if ok:
            title = unicode(title.text)
            summary = unicode(summary)
            content = unicode(content)

        return (
            ok,
            date,
            title,
            summary,
            content,
            sha,
            )
