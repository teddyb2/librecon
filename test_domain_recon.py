# Unit Test cases for domain recon. The tests contained within the test_domain class
# test core mechanics of the vhost parsers for accuracy when present with a wide variety 
# of vhosts

import unittest
import sys

from domain_recon import get_domain_config_path
from domain_recon import vhosts_extraction
from domain_recon import ApacheVirtualHost


class TestDomainInput(unittest.TestCase):


    def test_capital_domain(self):
        domain = 'CLUSTERA.COM'
        actual = get_domain_config_path(domain)
        expected = ["/etc/httpd/conf.d/cluster_buster.conf"]
        self.assertEqual(expected, actual)
        

    def test_mixed_case_domain(self):
        domain = 'HIDEOUT.teamrocket.com'
        actual = get_domain_config_path(domain)
        expected = ["/etc/httpd/conf.d/hideout.teamrocket.com.conf"]
        self.assertEqual(expected, actual)


    # TODO - suppress stdout messages    
    def test_incorrect_tld_domain(self):
        domain = "teamsocket.net"
        with self.assertRaises(SystemExit) as cm:
            get_domain_config_path(domain)
        self.assertEqual(cm.exception.code, 1)
    

    # TODO - suppress stdout messages
    def test_no_input(self):
        domain = ""
        with self.assertRaises(SystemExit) as cm:
            get_domain_config_path(domain)
        self.assertEqual(cm.exception.code, 1)


class TestVhostCralwers(unittest.TestCase):
    # Instaniate an instance of the vhost parser and the resulting processed vhost
    def setUp(self):
        self.domain = 'teamrocket.org'
        self.extracted_paths = get_domain_config_path(self.domain)
        #self.raw_vhosts = domain_recon.vhosts_extraction(self.extracted_paths, self.domain)
        
        self.vhost_object = []
        for self.path in self.extracted_paths:
            self.raw_vhosts = vhosts_extraction(self.path, self.domain)
            for self.raw_vhost in self.raw_vhosts:
                self.vhost_object = ApacheVirtualHost(raw_config=self.raw_vhost, config_path=self.path)
        

    def test_servername(self):
        self.assertEqual(self.vhost_object.server_name(), 'teamrocket.org')

    def test_alias(self):
        self.assertEqual(self.vhost_object.server_alias(), None)

    def test_document_root(self):
        self.assertEqual(self.vhost_object.document_root(), '/var/www/vhosts/teamrocket.org')

    def test_error_log(self):
        self.assertEqual(self.vhost_object.error_log(), '/var/log/httpd/teamrocket_error.log')

    def test_custom_log(self):
        self.assertEqual(self.vhost_object.custom_log(), '/var/log/httpd/teamrocket_access.log')

    def test_ssl_cert(self):
        self.assertEqual(self.vhost_object.ssl_cert(), None)

    def test_ssl_key(self):
        self.assertEqual(self.vhost_object.ssl_key(), None)

    def test_ssl_chain(self):
        self.assertEqual(self.vhost_object.ssl_chain(), None)


if __name__ == '__main__':
    unittest.main()
