"""KBase Software Development Kit

Usage:
  kb-sdk (-h | --help)
  kb-sdk init <name> [<directory>]
  kb-sdk status
  kb-sdk test [<module.Class.method>] [--skip-validation]
  kb-sdk validate

Commands:
  init       Initialize a new SDK app
  status     Run the status server
  test       Run tests for an app
  validate   Validate your configuration

Options:
  -h --help    Show this screen.
  --version    Show version.
"""

import os
import yaml
from docopt import docopt
from dotenv import load_dotenv

import kb_sdk.cli.init as init
import kb_sdk.cli.status as status
import kb_sdk.cli.test as test
import kb_sdk.cli.validate as validate
from kb_sdk.logger import logger

load_dotenv(dotenv_path='./.env')


# A registry of each of our CLI command handlers
commands = {
    'test': test,
    'status': status,
    'validate': validate
}


def main():
    """ This function is the entrypoint that gets called by the CLI """
    args = docopt(__doc__, version='0.0.1', help=True)
    env = os.environ.copy()
    env['MODULE_DIR'] = os.getcwd()
    if args['init']:
        # `init` is a special case; don't load config
        logger.info('Initializing a new app...')
        init.execute(args, env)
    for cmd, fn in commands.items():
        if args[cmd]:
            logger.debug('Running `kb-sdk ' + cmd + '`')
            config = _load_config()
            fn.execute(args, config, env)
            exit(0)


def _load_config():
    """ Load the YAML configuration file into a python dictionary """
    if not os.path.isfile('./kbase.yaml'):
        logger.error("Whoops, it doesn't look like we are in an SDK app directory")
        exit(1)
    with open('./kbase.yaml', 'r') as stream:
        logger.debug('Attempting to parse the YAML configuration')
        try:
            yaml_config = yaml.load(stream)
        except yaml.YAMLError as err:
            logger.debug('Error found as YAMLError')
            logger.error('Error loading YAML configuration: ' + err.problem)
            logger.error(err.problem_mark)
            exit(1)
        if not isinstance(yaml_config, dict):
            logger.error('Invalid YAML format for kbase.yaml')
            logger.error(yaml_config)
            exit(1)
    return yaml_config
