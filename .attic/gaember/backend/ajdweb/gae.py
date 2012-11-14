# -*- coding: utf-8 -*-

''' Entrypoint for the Google App Engine '''

from json import load
from github import Github
from gaestore import GaeStore
from ajdweb import initialize, load_config
from os.path import join, abspath, dirname

config = load_config('gae.json')
app = initialize(config, GaeStore(config), Github(config))
