# -*- coding: utf-8 -*-

''' The test suite '''

from ajdweb import initialize, load_config

have_gae = False
have_redis = False
config = load_config('test.json')
try:
    from ajdweb.redistore import RedisStore
    RedisStore(config).version()
    config['redis']['db'] = 1
    have_redis = True
except Exception, e:
    print 'Disabling redis tests - no instance found: {0}.'.format(e)

try:
    import sys
    sys.path.insert(0, '/usr/local/google_appengine')
    import dev_appserver
    dev_appserver.fix_sys_path()
    have_gae = True
except Exception, e:
    print 'Disabling Google AppEngine tests - no SDK found: {0}.'.format(e)

from unittest import TestCase
from ajdweb.test.github import GithubTest
from ajdweb.test.handlers import HandlersTest
from ajdweb.test.datastore import DatastoreTest

if have_redis:


    class FsRedis(TestCase):

        def setUp(self):
            from ajdweb.filesystem import Directory
            from ajdweb.redistore import RedisStore
            self.repo = Directory(config)
            self.store = RedisStore(config)
            self.api = initialize(config, self.store, self.repo)

        def tearDown(self):
            self.store.clear()


    class HandlersFsRedis(FsRedis, HandlersTest):

        pass


    class DatastoreFsRedis(FsRedis, DatastoreTest):

        pass


if have_gae:


    class FsGae(TestCase):

        def setUp(self):
            from ajdweb.gaestore import GaeStore
            from ajdweb.filesystem import Directory
            from google.appengine.ext import testbed
            self.testbed = testbed.Testbed()
            self.testbed.activate()
            self.testbed.init_datastore_v3_stub()
            self.api = initialize(config, GaeStore(config), Directory(config))
            self.store = self.api.registry.get('datastore')
            self.repo = self.api.registry.get('repository')

        def tearDown(self):
            self.testbed.deactivate()


    class HandlersFsGae(FsGae, HandlersTest):

        pass


    class DatastoreFsGae(FsGae, DatastoreTest):

        pass
