#!/usr/bin/env python3

import yaml
import argparse
import subprocess
import os
import logging


def get_commands_from_yaml(commands_file):
    with open(commands_file) as f:
        config = yaml.load(f)

        clusters = config['clusters']
        commands = config['commands']

        return clusters, commands


def execute_command(command): # pragma: no cover
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
        try:
            for parameterGroups in command['parameterGroups']:
                    command_to_exec = command['template'].format(*parameterGroups['parameters'])
                    commands_to_exec.append(command_to_exec)
                    logging.info('command: "{}"'.format(command_to_exec))
        except KeyError:
            logging.error('command file is malformed')
            raise

    return commands_to_exec


def execute_commands_by_clusters(commands, clusters):
    logging.info('executing commands...')

    try:
        for cluster in clusters:
            try:
                execute_command(get_login_command(cluster['url'], get_token_for_cluster(cluster['name'])))
            except KeyError:
                logging.error('command file is malformed')
                raise

            for command in commands:
                    execute_command(command)
    except subprocess.CalledProcessError as e:
        logging.error('command failed with error {}'.format(e.output))

        raise


if __name__ == '__main__':  # pragma: no cover
    logging.basicConfig(filename='openshift_oc_exec.log', level=logging.INFO)

    logging.info('openshift oc exec process starting...')

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('commands_file', metavar='commands_file', type=str, help='commands file')
    parameters = parser.parse_args()

    logging.info('getting commands file from {}'.format(parameters.commands_file))

    clusters, commands = get_commands_from_yaml(parameters.commands_file)

    commands_to_exec = process_commands(commands)

    execute_commands_by_clusters(commands_to_exec, clusters)
