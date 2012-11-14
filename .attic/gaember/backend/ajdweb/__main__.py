# -*- coding: utf-8 -*-

''' Standalone Python Server '''

from paste import httpserver
from redistore import RedisStore
from filesystem import Directory
from ajdweb import initialize, load_config
from os.path import join, abspath, dirname

config = load_config('paste.json')
app = initialize(config, RedisStore(config), Directory(config))
httpserver.serve(app, host=app.config['paste']['host'], port=app.config['paste']['port'])
