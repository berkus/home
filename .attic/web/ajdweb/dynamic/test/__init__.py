# -*- coding: utf-8 -*-

import sys
sdk_path = '/usr/local/google_appengine/'

sys.path.insert(0, sdk_path)
import dev_appserver
dev_appserver.fix_sys_path()

from database import SqlDbTest, AppEngineTest
from repository import LocalGitTest, GithubTest
from smoke import AppEngineWithLocalGit, SqlDbWithLocalGit, AppEngineWithGithub, SqlDbWithGithub
