from unittest.mock import patch
import unittest
import sys

from domain_recon import get_domain_config_path


class TestGetDomainConfigPathWithMockedCmd(unittest.TestCase):

    @staticmethod
    def bash_cmd_mock():
        '''Pretends to do what bash_cmd would do when called with "httpd -S | grep -i 'domain'" by reading a file
        '''

        with open('tests/assests/httpd_dash_s_output.txt', 'r') as f:
            return_code = 0
            command_output = str(f.read())
            return return_code, command_output

    def test_get_domain_config_path_with_valid_argument(self):
        with patch('domain_recon.bash_cmd') as patched:
            patched.return_value = self.bash_cmd_mock()
            actual = get_domain_config_path('valid argument')
            expected = ["/etc/httpd/conf.d/cluster_buster.conf"]
            self.assertEqual(expected, actual)

    def test_get_domain_config_path_with_invalid_argument(self):
        with self.assertRaises(SystemExit) as condition:
            with patch('domain_recon.bash_cmd') as patched:
                patched.return_value = self.bash_cmd_mock()
                actual = get_domain_config_path([])
                expected = ["/etc/httpd/conf.d/cluster_buster.conf"]
                self.assertEqual(expected, actual)
        self.assertEqual(condition.exception.code, 1)
