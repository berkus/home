# -*- coding: utf-8 -*-

import sys
sdk_path = '/usr/local/google_appengine/'

sys.path.insert(0, sdk_path)
import dev_appserver
dev_appserver.fix_sys_path()

# from github import GithubTest
# from localgit import LocalGitTest
# from appengine import AppEngineTest
from smoke import SmokeTest
