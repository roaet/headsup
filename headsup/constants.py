#
# Copyright 2015 Justin Hammond
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

GITCOLUMNS = 'GITCOLUMNS'
NEWCOLUMNS = 'NEWCOLUMNS'
TRACKERS = 'TRACKERS'
REPOS = 'REPOS'
TAGS = 'TAGS'
TRACKER_URLS = 'TRACKER_URLS'

OKAY = 200

class HeadsupError(object):
    def __init__(self, msg, http_code):
        self.msg = msg
        self.code = http_code
        self.extra_msg = None

    def as_tuple(self):
        msg = self.msg
        return (msg, self.code)

    def extra(self, msg):
        self.msg = "%s: %s" % (self.msg, msg)
        return self


def webify(results):
    code = results.code
    msg = results.msg
    if code == 400:
        msg = 'Bad request:' + msg
    if code == 404:
        msg = 'Not Found Error:' + msg
    if code == 500:
        msg = 'Internal Server Error:' + msg
    return HeadsupError(msg, code)

BRANCH_NOT_FOUND = HeadsupError('Branch not found', 404)
NO_VALID_COLUMNS = HeadsupError('No valid columns', 400)
REPO_NOT_FOUND = HeadsupError('Repo not found', 404)
RANDOM_GIT_ERROR = HeadsupError('Git problem', 500)
GIT_AUTH_ERROR = HeadsupError('Git auth problem', 500)
SOCKET_ERROR = HeadsupError('Socket error', 500)
IO_ERROR = HeadsupError('IO error', 500)
TEMP_DIR_FAILED = HeadsupError('Tempdir error', 500)
