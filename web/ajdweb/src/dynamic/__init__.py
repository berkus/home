# -*- coding: utf-8 -*-

import sys
from os.path import join, abspath, dirname
sys.path.append(abspath(join(dirname(__file__),'lib')))

import webapp2
app = webapp2.WSGIApplication(debug=True)
app.router.add(webapp2.Route(r'/update', handler='dynamic.handlers.UpdateHandler'))
app.router.add(webapp2.Route(r'/<path:.*>', handler='dynamic.handlers.PageHandler'))
