#!/usr/bin/env python3

import yaml
import argparse
import subprocess
import os
import logging


def config_logging():
    logging.basicConfig(filename='openshift_oc_exec.log', level=logging.INFO)


def get_config_from_yaml(config_file):
    return yaml.load(open(config_file))


def create_parser():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('config_file', metavar='config_file', type=str, help='configuration file')

    return parser


def execute_command(command):
    logging.info('executing command "{}"'.format(command))

    output = subprocess.check_output(command.split(' '), stderr=subprocess.STDOUT)

    logging.info('command output is "{}"'.format(output))


def get_login_command(url, token):
    return 'oc login {} --token={}'.format(url, token)


class TokenException(Exception):
    pass


def get_token_for_cluster(cluster):
    env_var_name = 'TOKEN_' + cluster.upper()
    env_var_value = os.environ.get(env_var_name)

    logging.info('looking for env var {} in os'.format(env_var_name))

    if env_var_value is None:
        message = 'env var {} is not defined'.format(env_var_name)

        logging.error(message)

        raise TokenException(message)

    logging.info('env var {} found in os'.format(env_var_name))

    return os.environ.get(env_var_name)


def process_commands(commands):
    commands_to_exec = []

    for command in commands:
        logging.info('gathering commands for {}'.format(command['name']))

        for parameterGroups in command['parameterGroups']:
            try:
                command_to_exec = command['template'].format(*parameterGroups['parameters'])
                commands_to_exec.append(command_to_exec)
                logging.info('command: "{}"'.format(command_to_exec))
            except KeyError:
                logging.error('error')

    return commands_to_exec


def execute_commands_by_clusters(commands, clusters):
    logging.info('executing commands...')

    for cluster in clusters:
        execute_command(get_login_command(cluster['url'], get_token_for_cluster(cluster['name'])))

        for command in commands:
            execute_command(command)


if __name__ == '__main__':
    config_logging()

    logging.info('openshift oc exec process starting...')
    parser = create_parser()
    parameters = parser.parse_args()

    logging.info('getting configuration file from {}'.format(parameters.config_file))

    # Gets the YAML configuration
    config = get_config_from_yaml(parameters.config_file)

    clusters = config['clusters']
    commands = config['commands']

    commands_to_exec = process_commands(commands)

    execute_commands_by_clusters(commands_to_exec, clusters)
