#
# Copyright 2015 Rackspace
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
import json
import logging
import sys

import click

from headsup import utils

logging.basicConfig(stream=sys.stdout, level=logging.WARNING)
LOG = logging.getLogger()
command_settings = {
    'ignore_unknown_options': True,
}

default_columns=",".join(['sha', 'author', 'email', 'description',
                          'commit_date', 'trackers',])


@click.command(context_settings=command_settings)
@click.argument('repo')
@click.option('--config', default=None, is_flag=False,
              type=click.File('rb'),
              help='Configuration file for runtime')
@click.option('--start-branch', default=None, is_flag=False,
              help='Start branch for comparison')
@click.option('--end-branch', default=None, is_flag=False,
              help='End branch for comparison')
@click.option('--columns', default=default_columns, is_flag=False,
              help='Comma-separated list of columns to show during output')
@click.pass_context
def run_headsup(context, repo, config, start_branch, end_branch, columns):
    columns = columns.split(',')
    utils.initialize_context(context, config)

    unknown_columns = utils.check_columns(context, columns)
    if len(unknown_columns) == len(columns):
        click.echo("No valid columns for output. Exiting.")
        exit(1)

    history = utils.get_history_dict_of_repo_and_branches(context, repo,
                                                          start_branch,
                                                          end_branch)
    if history is None:
        print "Error detected"
        exit(1)
    history_list = []
    for element in history:
        datas = {}
        for column in columns:
            if column in element:
                datas[column] = element[column]
        history_list.append(datas)

    history_json = json.dumps(dict(history=history_list))

    print history_json
