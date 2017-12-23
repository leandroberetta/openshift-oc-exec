import unittest
import openshift_oc_exec
import os
import subprocess

from unittest.mock import patch


commands_executed = []


def execute_command(command):
    commands_executed.append(command)


def execute_command_error(command):
    raise subprocess.CalledProcessError(-1, command)


class OpenShiftOCExecTest(unittest.TestCase):

    def test_get_commands_to_process(self):
        clusters, commands = openshift_oc_exec.get_commands_from_yaml('openshift_oc_exec_test.yaml')

        commands_to_exec = openshift_oc_exec.process_commands(commands)

        self.assertIn('oc set env dc app1 TZ=America/Argentina/Buenos_Aires -n prod', commands_to_exec)
        self.assertIn('oc set env dc app2 TZ=America/Argentina/Buenos_Aires -n prod', commands_to_exec)

        self.assertIn('oc rollout latest dc app1 -n prod', commands_to_exec)
        self.assertIn('oc rollout latest dc app2 -n prod', commands_to_exec)

        self.assertEqual(4, len(commands_to_exec))

    def test_get_config_file(self):
        clusters, commands = openshift_oc_exec.get_commands_from_yaml('openshift_oc_exec_test.yaml')

        self.assertIsNotNone(clusters)
        self.assertIsNotNone(commands)

    def test_get_login_command(self):
        command = openshift_oc_exec.get_login_command('https://cluster1:8443', 'token')

        self.assertEqual('oc login https://cluster1:8443 --token=token', command)

    @patch('openshift_oc_exec.execute_command', execute_command)
    def test_execute_commands_by_cluster(self):
        clusters, commands = openshift_oc_exec.get_commands_from_yaml('openshift_oc_exec_test.yaml')

        os.environ['TOKEN_CLUSTER1'] = 'token'
        os.environ['TOKEN_CLUSTER2'] = 'token'

        commands_to_exec = openshift_oc_exec.process_commands(commands)
        openshift_oc_exec.execute_commands_by_clusters(commands_to_exec, clusters)

        commands_to_exec.append('oc login https://cluster1:8443 --token=token')
        commands_to_exec.append('oc login https://cluster2:8443 --token=token')

        for command_to_exec in commands_to_exec:
            self.assertIn(command_to_exec, commands_executed)

    @patch('openshift_oc_exec.execute_command', execute_command)
    def test_get_token_exception(self):
        clusters, commands = openshift_oc_exec.get_commands_from_yaml('openshift_oc_exec_test.yaml')

        del os.environ['TOKEN_CLUSTER1']
        del os.environ['TOKEN_CLUSTER2']

        commands_to_exec = openshift_oc_exec.process_commands(commands)

        self.assertRaises(openshift_oc_exec.TokenException, openshift_oc_exec.execute_commands_by_clusters, commands_to_exec, clusters)

    def test_get_key_error_in_commands(self):
        clusters, commands = openshift_oc_exec.get_commands_from_yaml('openshift_oc_exec_commands_error_test.yaml')

        os.environ['TOKEN_CLUSTER1'] = 'token'
        os.environ['TOKEN_CLUSTER2'] = 'token'

        self.assertRaises(KeyError, openshift_oc_exec.process_commands, commands)

    @patch('openshift_oc_exec.execute_command', execute_command)
    def test_get_key_error_in_clusters(self):
        clusters, commands = openshift_oc_exec.get_commands_from_yaml('openshift_oc_exec_clusters_error_test.yaml')

        os.environ['TOKEN_CLUSTER1'] = 'token'
        os.environ['TOKEN_CLUSTER2'] = 'token'

        commands_to_exec = openshift_oc_exec.process_commands(commands)

        self.assertRaises(KeyError, openshift_oc_exec.execute_commands_by_clusters, commands_to_exec, clusters)

    @patch('openshift_oc_exec.execute_command', new=execute_command_error)
    def test_get_called_process_error(self):
        clusters, commands = openshift_oc_exec.get_commands_from_yaml('openshift_oc_exec_test.yaml')

        os.environ['TOKEN_CLUSTER1'] = 'token'
        os.environ['TOKEN_CLUSTER2'] = 'token'

        commands_to_exec = openshift_oc_exec.process_commands(commands)

        self.assertRaises(subprocess.CalledProcessError, openshift_oc_exec.execute_commands_by_clusters, commands_to_exec, clusters)


if __name__ == '__main__':
    unittest.main()