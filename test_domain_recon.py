# Unit Test cases for domain recon. The tests contained within the test_domain class
# test core mechanics of the vhost parsers for accuracy when present with a wide variety 
# of vhosts

import unittest
import sys
import domain_recon

class test_domain_input(unittest.TestCase):


    def test_CAPITAL_domain(self):
        domain = 'CLUSTERA.COM'
        actual = domain_recon.get_domain_config_path(domain)
        expected = ["/etc/httpd/conf.d/cluster_buster.conf"]
        self.assertEqual(expected, actual)
        

    def test_mixedCASE_domain(self):
        domain = 'HIDEOUT.teamrocket.com'
        actual = domain_recon.get_domain_config_path(domain)
        expected = ["/etc/httpd/conf.d/hideout.teamrocket.com.conf"]
        self.assertEqual(expected, actual)


    # TODO - suppress stdout messages    
    def test_incorrect_tld_domain(self):
        domain = "teamsocket.net"
        with self.assertRaises(SystemExit) as cm:
            domain_recon.get_domain_config_path(domain)
        self.assertEqual(cm.exception.code, 1)
    

    # TODO - suppress stdout messages
    def test_no_input(self):
        domain = ""
        with self.assertRaises(SystemExit) as cm:
            domain_recon.get_domain_config_path(domain)
        self.assertEqual(cm.exception.code, 1)


if __name__ == '__main__':
    unittest.main()
