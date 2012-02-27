# -*- coding: utf-8 -*-

import webapp2
import thirdparty

app = webapp2.WSGIApplication(debug=True)
app.router.add(webapp2.Route(r'/update', handler='ajdweb.handlers.UpdateHandler'))
app.router.add(webapp2.Route(r'/<path:.*>', handler='ajdweb.handlers.PageHandler'))
