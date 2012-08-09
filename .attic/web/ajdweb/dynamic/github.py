# -*- coding: utf-8 -*-

import json
from urllib2 import urlopen
from os.path import splitext
from base64 import b64decode
from datetime import datetime
from bs4 import BeautifulSoup


class GitHub:

    def __init__(self, config):
        repo = config.get('REPO')
        branch = config.get('BRANCH')
        r = urlopen('{0}/commits?path={1}&per_page=1'.format(repo, branch)).read()
        r = urlopen(json.loads(r)[0]['commit']['tree']['url']).read()
        for b in branch.split('/'):
            for t in json.loads(r)['tree']:
                if t['path'] == b:
                    r = urlopen(t['url']).read()
                    break
        self._root = json.loads(r)

    def version(self):
        return self._root['sha']

    def pages(self):
        r = urlopen('{0}?recursive=1'.format(self._root['url'])).read()
        tree = [t for t in json.loads(r)['tree'] if t['type'] == 'blob']
        self._pages = { '/' + splitext(t['path'])[0] : (t['sha'], t['url']) for t in tree }
        return set(self._pages.iterkeys())

    def version_of(self, p):
        return self._pages[p][0]

    def content_of(self, p):
        (sha, url) = self._pages[p]
        raw = BeautifulSoup(b64decode(json.loads(urlopen(url).read())['content']))
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
