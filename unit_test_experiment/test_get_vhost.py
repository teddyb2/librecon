
import unittest
from get_vhost import get_domain_config_paths

class TestDomain(unittest.TestCase):

    def test_get_domain_config_path(self):
        domain = 'hideout.teamrocket.org'
        expected_config_path = ["/etc/httpd/conf.d/hideout.teamrocket.com.conf"]
        actual_config_path = get_domain_config_paths(domain = domain)


        self.assertEqual(expected_config_path, actual_config_path)

    def test_with_invalid_domain(self):
        domain = 'nothing.nope'
        expected_config_path = [""]
        actual_config_path = get_domain_config_paths(domain = domain)


        self.assertEqual(expected_config_path, actual_config_path)

if __name__ == '__main__':
    unittest.main()


