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
import configobj
import logging
import os
import re
import shutil
import socket
import tempfile

import click

os.environ["GIT_PYTHON_TRACE"] = "0"

import git

from headsup import constants

_SPLIT = "(#)"


def mk_format(context):
    format_escapes = []
    if constants.GITCOLUMNS in context.config:
        for key, format in context.config[constants.GITCOLUMNS].items():
            format_escapes.append(format)
    return _SPLIT.join(format_escapes)

def check_columns(context, columns):
    unknown_columns = []
    cfg = context.config
    if constants.GITCOLUMNS in cfg and 'NEWCOLUMNS' in cfg:
        for col in columns:
            if(col not in cfg[constants.GITCOLUMNS] and
                    col not in cfg[constants.NEWCOLUMNS]):
                unknown_columns.append(col)
    return unknown_columns


def line_to_dict(context, line):
    split_line = line.split(_SPLIT)
    line_dict = {}
    i = 0
    if constants.GITCOLUMNS in context.config:
        for key, format in context.config[constants.GITCOLUMNS].items():
            line_dict[key] = split_line[i]
            i += 1
    return line_dict


def _load_config(file):
    config = configobj.ConfigObj(file, raise_errors=True)
    return config


def _configure_trackers(context):
    context.trackers = {}
    if constants.TRACKERS in context.config:
        for tracker, regex in context.config[constants.TRACKERS].items():
            context.trackers[tracker] = regex
    context.tracker_urls = {}
    if constants.TRACKER_URLS in context.config:
        for tracker, prefix in context.config[constants.TRACKERS].items():
            context.tracker_urls[tracker] = prefix
    context.tags = {}
    if constants.TAGS in context.config:
        for tag, regex in context.config[constants.TAGS].items():
            context.tags[tag] = regex
            

def configure_repos(context):
    if constants.REPOS not in context.config:
        click.echo("No valid repos configured. Exiting")
        exit(1)
    context.repos = {}
    for repo, addr in context.config[constants.REPOS].items():
        context.repos[repo] = addr


def initialize_context(context, config_file, service=False):
    context.config = _load_config(config_file)
    context.service = service
    _configure_trackers(context)
    if context.service:
        configure_repos(context)
    

def get_history_dict_of_repo_and_branches(context, repo, branch1, branch2):

    log = logging.getLogger('git.cmd')
    log.setLevel(logging.WARNING)
    current_path = tempfile.gettempdir()
    tempdir = tempfile.mkdtemp(prefix='headsup_', dir=current_path)
    if not tempdir:
        return constants.TEMP_DIR_FAILED
    os.chdir(tempdir)
    try:
        repo = git.Repo.clone_from(repo, tempdir, bare=True)

        pretty = "format:%s" % mk_format(context)


        git_cmd = repo.git
        output = git_cmd.log("%s..%s" % (branch1, branch2), pretty=pretty)

        history = []

        for line in output.splitlines():
            line_dict = line_to_dict(context, line)
            sha = line_dict.get('sha', None)
            if sha is not None:
                message = git_cmd.log("%s" % sha, n=1, format="%B")
                if "Merge pull request" in message:
                    continue
                line_dict['trackers'] = {}
                for tracker, regex in context.trackers.iteritems():
                    if tracker not in line_dict['trackers']:
                        line_dict['trackers'][tracker] = [] 
                    line_dict['trackers'][tracker] = list(set(
                            re.findall(regex, message)))
                line_dict['tags'] = []
                for tag, regex in context.tags.iteritems():
                    tags = list(set(re.findall(regex, message, flags=re.I)))
                    if len(tags) > 0:
                        line_dict['tags'].append(tags)
                line_dict['message'] = message
            history.append(line_dict)

        return history
    except socket.error, e:
        return constants.SOCKET_ERROR
    except IOError, e:
        return constants.IO_ERROR
    except git.GitCommandError, e:
        if 'Repository not found' in e.stderr:
            return constants.REPO_NOT_FOUND.extra(e.stderr)
        if 'unknown revision or path' in e.stderr:
            return constants.BRANCH_NOT_FOUND.extra(e.stderr)
        if 'Permission denied (publickey)' in e.stderr:
            return constants.GIT_AUTH_ERROR.extra(e.stderr)
        return constants.RANDOM_GIT_ERROR.extra(e.stderr)
    finally:
        if os.path.isdir(tempdir):
            shutil.rmtree(tempdir)
        os.chdir(current_path)
