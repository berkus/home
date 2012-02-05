# -*- coding: utf-8 -*-

from webapp2 import RequestHandler
from backends import database, repository


class UpdateHandler(RequestHandler):

    def get(self):
        self.response.write(str(len(self._update())))

    def _update(self):
        return database().synchronize(repository())
