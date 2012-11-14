# -*- coding: utf-8 -*-

from json import loads
from urllib2 import urlopen
from os.path import splitext
from base64 import b64decode


class Github:

    ''' A content repository based on a repository in Github. '''

    def __init__(self, config):
        self.repo = config['github']['repo']
        self.branch = config['github']['branch']
        self.refresh()

    def refresh(self):
        ''' Loads the repository from github '''

        self.pages = {}

        r = urlopen('{0}/commits?path={1}&per_page=1'.format(self.repo, self.branch)).read()
        r = urlopen(loads(r)[0]['commit']['tree']['url']).read()
        for b in self.branch.split('/'):
            for t in loads(r)['tree']: #pragma: no branch
                if t['path'] == b:
                    r = urlopen(t['url']).read()
                    break
        self.root = loads(r)

        r = urlopen('{0}?recursive=1'.format(self.root['url'])).read()
        for t in [t for t in loads(r)['tree'] if t['type'] == 'blob' and t['path'].endswith('.txt')]:
            self.pages[splitext(t['path'])[0]] = (t['sha'], t['url'])

    def version(self):
        return self.root['sha']

    def ids(self):
        return set(self.pages.iterkeys())

    def content_of(self, p):
        url = self.pages[p][1]
        return b64decode(loads(urlopen(url).read())['content']).split('\n')

    def version_of(self, p):
        return self.pages[p][0]
