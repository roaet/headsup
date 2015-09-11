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
import os
import re
import shutil
import tempfile

import click

os.environ["GIT_PYTHON_TRACE"] = '1'

import git


_SPLIT = "(#)"


def mk_format(context):
    format_escapes = []
    if 'GITCOLUMNS' in context.config:
        for key, format in context.config['GITCOLUMNS'].items():
            format_escapes.append(format)
    return _SPLIT.join(format_escapes)

def check_columns(context, columns):
    unknown_columns = []
    cfg = context.config
    if 'GITCOLUMNS' in cfg and 'NEWCOLUMNS' in cfg:
        for col in columns:
            if col not in cfg['GITCOLUMNS'] and col not in cfg['NEWCOLUMNS']:
                unknown_columns.append(col)
    return unknown_columns


def line_to_dict(context, line):
    split_line = line.split(_SPLIT)
    line_dict = {}
    i = 0
    if 'GITCOLUMNS' in context.config:
        for key, format in context.config['GITCOLUMNS'].items():
            line_dict[key] = split_line[i]
            i += 1
    return line_dict


def _load_config(file):
    config = configobj.ConfigObj(file, raise_errors=True)
    return config


def _configure_trackers(context):
    context.trackers = {}
    if 'TRACKERS' in context.config:
        for tracker, regex in context.config['TRACKERS'].items():
            context.trackers[tracker] = regex
    context.tracker_urls = {}
    if 'TRACKER_URLS' in context.config:
        for tracker, prefix in context.config['TRACKERS'].items():
            context.tracker_urls[tracker] = prefix
    context.tags = {}
    if 'TAGS' in context.config:
        for tag, regex in context.config['TAGS'].items():
            context.tags[tag] = regex


def initialize_context(context, config_file):
    context.config = _load_config(config_file)
    _configure_trackers(context)
    

def get_history_dict_of_repo_and_branches(context, repo, branch1, branch2):

    current_path = tempfile.gettempdir()
    tempdir = tempfile.mkdtemp(prefix='headsup_', dir=current_path)
    if not tempdir:
        click.echo("Failed to make temporary directory %s" % tempdir)
        exit(1)
    os.chdir(tempdir)
    try:
        repo = git.Repo.clone_from(repo, tempdir, bare=True)

        pretty = "format:%s" % mk_format(context)

        git_cmd = repo.git
        try:
            output = git_cmd.log("%s..%s" % (branch1, branch2), pretty=pretty)
        except git.exc.GitCommandError as e:
            print e
            return None

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

    finally:
        if os.path.isdir(tempdir):
            shutil.rmtree(tempdir)
        os.chdir(current_path)
