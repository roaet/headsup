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
import json
import logging
import sys

import click

from headsup import constants
from headsup import utils

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
LOG = logging.getLogger()

command_settings = {
    'ignore_unknown_options': True,
}

default_columns=",".join(['sha', 'author', 'email', 'description',
                          'commit_date', 'trackers',])


def get_history_json(context, repo, start_branch, end_branch, columns):
    results = utils.get_history_dict_of_repo_and_branches(context, repo,
            start_branch, end_branch)
    if isinstance(results, constants.HeadsupError):
        if context.service:
            results = constants.webify(results)
        return results.as_tuple()
    history = results
    history_list = []

    for element in history:
        datas = {}
        for column in columns:
            if column in element:
                datas[column] = element[column]
        history_list.append(datas)

    history_json = json.dumps(dict(history=history_list))

    return (history_json, constants.OKAY)


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

    history, status = get_history_json(context, repo, start_branch, end_branch,
                                       columns)
    if status != constants.OKAY:
        click.echo("Error detected: %s" % history)
        exit(1)
    click.echo(history)


@click.command(context_settings=command_settings)
@click.option('--config', default=None, is_flag=False,
              type=click.File('rb'),
              help='Configuration file for runtime')
@click.pass_context
def run_as_service(context, config):
    click.echo("Running as service")
    utils.initialize_context(context, config, True)
    import flask

    from flask import request

    app = flask.Flask(__name__)

    @app.route('/<repo>/<start>/<end>')
    def handle_request(repo, start, end):
        if repo not in context.repos:
            return constants.REPO_NOT_FOUND.as_tuple()
        if not start or not end:
            return constants.BRANCH_NOT_FOUND.as_tuple()
        cols = request.args.get('cols', default_columns)
        cols = cols.split(',')
        unknown_columns = utils.check_columns(context, cols)
        if len(unknown_columns) == len(cols):
            return constants.NO_VALID_COLUMNS.as_tuple()
        repo_addr = context.repos[repo]
        return get_history_json(context, repo_addr, start, end, cols)

    app.run(debug=True)
