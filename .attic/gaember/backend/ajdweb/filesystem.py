# -*- coding: utf-8 -*-

from os import walk
from hashlib import sha1
from os.path import join, basename


class Directory:

    ''' A content repository based on a directory on the filesystem. '''

    def __init__(self, config):
        self.ver = None
        self.contents = {}
        self.root = config['filesystem']['root']
        self.refresh()

    def refresh(self):
        ''' Walks the directory tree and populates the content tree '''

        self.ver = sha1()
        self.contents = {}
        extension = '.txt'
        for (root, dirs, files) in walk(self.root):
            for f in [join(root, x) for x in files if x.endswith(extension)]:
                data = open(f).read()
                version = sha1(data).hexdigest()
                data = data.split('\n')
                self.ver.update(f)
                self.ver.update(version)
                self.contents[f[len(self.root + '/'):-1 * len(extension)]] = (version, data) # pragma: no branch

        self.ver = self.ver.hexdigest()

    def version(self):
        ''' Returns the current repository version '''

        return self.ver

    def ids(self):
        ''' Returns the set of entries in the repository '''

        return set(self.contents.keys())

    def content_of(self, e):
        ''' Returns the content of the given entry '''

        return self.contents[e][1]

    def version_of(self, e):
        ''' Returns the version of the given entry '''

        return self.contents[e][0]
