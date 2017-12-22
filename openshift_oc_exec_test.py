import unittest
import yaml
import openshift_oc_exec


class OCExecTest(unittest.TestCase):

    def setUp(self):
        with open('openshift_oc_exec_test.yaml') as f:
            self.config = yaml.load(f)

            self.clusters = self.config['clusters']
            self.commands = self.config['commands']

    def test_get_commands_to_process(self):
        commands_to_exec = openshift_oc_exec.process_commands(self.commands)


        self.assertIn('oc set env dc app1 TZ=America/Argentina/Buenos_Aires -n prod', commands_to_exec)
        self.assertIn('oc set env dc app2 TZ=America/Argentina/Buenos_Aires -n prod', commands_to_exec)
