# Unit Test cases for domain recon. The tests contained within the test_domain class
# test core mechanics of the vhost parsers for accuracy when present with a wide variety 
# of vhosts

import unittest
import sys

from domain_recon import get_domain_config_path
from domain_recon import vhosts_extraction
from domain_recon import ApacheVirtualHost

# Tests domain_recon input argument handling for valid and invalid input
class TestDomainInput(unittest.TestCase):


    def test_capital_domain(self):
        domain = 'CLUSTERA.COM'
        actual = get_domain_config_path(domain)
        expected = ["/etc/httpd/conf.d/cluster_buster.conf"]
        self.assertEqual(expected, actual)
        

    def test_mixed_case_domain(self):
        domain = 'HIDEOUT.teamrocket.org'
        actual = get_domain_config_path(domain)
        expected = ["/etc/httpd/conf.d/hideout.teamrocket.org.conf"]
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


# single 80 vhost test and vhost crawler test
class TestVhostCralwers(unittest.TestCase):
    # Instaniate an instance of the vhost parser and the resulting processed vhost
    def setUp(self):
        self.domain = 'teamrocket.org'
        self.extracted_path = "/etc/httpd/conf.d/teamrocket.org.conf"

        self.raw_vhosts = vhosts_extraction(self.extracted_path, self.domain)
        self.vhost_object = ApacheVirtualHost(raw_config=self.raw_vhosts[0], config_path=self.extracted_path)
        

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


# Clustered 80 vhost test - pulling the correct vhost block from a cluster vhost confs
class TestClusteredVhosts(unittest.TestCase):
    # Instaniate an instance of the vhost parser and the resulting processed vhost
    def setUp(self):
        self.domain = 'clusterb.com'
        self.extracted_paths = get_domain_config_path(self.domain)
           
        self.raw_vhosts = vhosts_extraction(str(self.extracted_paths[0]), self.domain)
        self.vhost_object = ApacheVirtualHost(raw_config=self.raw_vhosts[0], config_path=self.extracted_paths)


    def test_servername(self):
        self.assertEqual(self.vhost_object.server_name(), 'clusterB.com')

    def test_alias(self):
        self.assertEqual(self.vhost_object.server_alias(), None)

    def test_document_root(self):
        self.assertEqual(self.vhost_object.document_root(), '/var/www/vhosts/clusterB.com')

    def test_error_log(self):
        self.assertEqual(self.vhost_object.error_log(), '/var/log/httpd/clusterB_error.log')

    def test_custom_log(self):
        self.assertEqual(self.vhost_object.custom_log(), '/var/log/httpd/clusterB_access.log')

    def test_ssl_cert(self):
        self.assertEqual(self.vhost_object.ssl_cert(), None)

    def test_ssl_key(self):
        self.assertEqual(self.vhost_object.ssl_key(), None)

    def test_ssl_chain(self):
        self.assertEqual(self.vhost_object.ssl_chain(), None)


# Subdomain 80 vhost test - search for subdomain vhost and extract information from a subdomain
class TestSubDomainVhost(unittest.TestCase):
    # Instaniate an instance of the vhost parser and the resulting processed vhost
    def setUp(self):
        self.domain = 'hideout.teamrocket.org'
        self.extracted_paths = get_domain_config_path(self.domain)
        
        # Iterates through the vhosts confs parsed from the hideout.teamrocket.org conf
        self.vhost_object = []
        for self.path in self.extracted_paths:
            self.raw_vhosts = vhosts_extraction(self.path, self.domain)
            for self.raw_vhost in self.raw_vhosts:
                tmp = ApacheVirtualHost(raw_config=self.raw_vhost, config_path=self.path)
                self.vhost_object = tmp

     
    def test_servername(self):
        self.assertEqual(self.vhost_object.server_name(), 'hideout.teamrocket.org')

    def test_alias(self):
        self.assertEqual(self.vhost_object.server_alias(), 'stealth.com')

    def test_document_root(self):
        self.assertEqual(self.vhost_object.document_root(), '/var/www/vhosts/hideout.teamrocket.org')

    def test_error_log(self):
        self.assertEqual(self.vhost_object.error_log(), '/var/log/httpd/hideout_teamrocket_error.log')

    def test_custom_log(self):
        self.assertEqual(self.vhost_object.custom_log(), '/var/log/httpd/hideout_teamrocket_access.log')

    def test_ssl_cert(self):
        self.assertEqual(self.vhost_object.ssl_cert(), None)

    def test_ssl_key(self):
        self.assertEqual(self.vhost_object.ssl_key(), None)

    def test_ssl_chain(self):
        self.assertEqual(self.vhost_object.ssl_chain(), None)


# single 443 vhost test - teamfire.org
class Test443_80Vhosts(unittest.TestCase):
    # Instaniate an instance of the vhost parser and the resulting processed vhost
    def setUp(self):
        self.domain = 'teamfire.org'
        self.extracted_paths = '/etc/httpd/conf.d/teamfire.org.conf'
   
        # For a given configuration path, a vhost_object can contain one or two vhost configurations, 
        # which entirely depends if both 443/80 blocks are present. In this test, the second vhost (443)
        # is being pulled from the vhost_object. The first vhost is 80. 
        self.raw_vhosts = vhosts_extraction(self.extracted_paths, self.domain)
        self.vhost_object = ApacheVirtualHost(raw_config=self.raw_vhosts[1], config_path=self.extracted_paths)


    def test_source_config_path(self):
        self.assertEqual(self.vhost_object.source_config_path(), '/etc/httpd/conf.d/teamfire.org.conf')

    def test_servername(self):
        self.assertEqual(self.vhost_object.server_name(), 'teamfire.org')

    def test_alias(self):
        self.assertEqual(self.vhost_object.server_alias(), '1000degrees.com')

    def test_document_root(self):
        self.assertEqual(self.vhost_object.document_root(), '/var/www/vhosts/teamfire.org')

    def test_error_log(self):
        self.assertEqual(self.vhost_object.error_log(), '/var/log/httpd/teamfire_ssl_error.log')

    def test_custom_log(self):
        self.assertEqual(self.vhost_object.custom_log(), '/var/log/httpd/teamfire_ssl_access.log')

    def test_ssl_cert(self):
        self.assertEqual(self.vhost_object.ssl_cert(), '/etc/pki/tls/certs/teamfire.crt')

    def test_ssl_key(self):
        self.assertEqual(self.vhost_object.ssl_key(), '/etc/pki/tls/private/teamfire.key')

    def test_ssl_chain(self):
        self.assertEqual(self.vhost_object.ssl_chain(), None)


# single 80 vhost test - teamfire.org
class Test_80Vhosts(unittest.TestCase):
    # Instaniate an instance of the vhost parser and the resulting processed vhost
    def setUp(self):
        self.domain = 'teamfire.org'
        self.extracted_paths = '/etc/httpd/conf.d/teamfire.org.conf'
   
        # For a given configuration path, a vhost_object can contain one or two vhost configurations, 
        # which entirely depends if both 443/80 blocks are present. In this test, the second vhost (443)
        # is being pulled from the vhost_object. The first vhost is 80. 
        self.raw_vhosts = vhosts_extraction(self.extracted_paths, self.domain)
        self.vhost_object = ApacheVirtualHost(raw_config=self.raw_vhosts[0], config_path=self.extracted_paths)


    def test_source_config_path(self):
        self.assertEqual(self.vhost_object.source_config_path(), '/etc/httpd/conf.d/teamfire.org.conf')

    def test_servername(self):
        self.assertEqual(self.vhost_object.server_name(), 'teamfire.org')

    def test_alias(self):
        self.assertEqual(self.vhost_object.server_alias(), '1000degrees.com')

    def test_document_root(self):
        self.assertEqual(self.vhost_object.document_root(), '/var/www/vhosts/teamfire.org')

    def test_error_log(self):
        self.assertEqual(self.vhost_object.error_log(), '/var/log/httpd/teamfire_error.log')

    def test_custom_log(self):
        self.assertEqual(self.vhost_object.custom_log(), '/var/log/httpd/teamfire_access.log')

    def test_ssl_cert(self):
        self.assertEqual(self.vhost_object.ssl_cert(), None)

    def test_ssl_key(self):
        self.assertEqual(self.vhost_object.ssl_key(), None)

    def test_ssl_chain(self):
        self.assertEqual(self.vhost_object.ssl_chain(), None)


if __name__ == '__main__':
    unittest.main()
