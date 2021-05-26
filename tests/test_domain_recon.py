# Unit Test cases for domain recon. The tests contained within the test_domain class
# test core mechanics of the vhost parsers for accuracy when present with a wide variety 
# of vhosts

from unittest.mock import patch
from unittest import mock
import unittest
import sys

from domain_recon import vhosts_extraction
from domain_recon import ApacheVirtualHost
from utils import do_cmd as bash_cmd
from domain_recon import get_apache_config_paths


# NOTE - This class might not accurately represent the goal of parsing a raw httpd -S dump
class MockGetDomainConfig(unittest.TestCase):

    domain_map = {'CLUSTERA.com' : 'tests/assets/cluster_buster.conf',
                              'clusterb.com' : 'tests/assets/cluster_buster.conf',
                              'clusterc.com' : 'tests/assets/cluster_buster.conf',
                              'teamfire.org' : 'tests/assets/teamfire.org.conf',
                              'teamrocket.org' : 'tests/assets/teamrocket.org.conf',
                              'hideout.teamrocket.org' : 'tests/assets/hideout.teamrocket.org.conf',
                              '' : ''}

    # reads the the vhost configuration file from the domain_map. Returns a tuple[return_code, 
    # vhost_contents, extracted_path "from domain_map" ]
    def bash_cmd_mock(self, domain):
        '''Pretends to do what bash_cmd would do when called with "httpd -S" by reading a file
        '''
        try:
            with open(self.domain_map[domain], 'r') as f:
                return_code = 0
                command_output = str(f.read())
                extracted_path = self.domain_map[domain]
                return return_code, command_output, extracted_path 
        except GeneratorExit:
            print(f"FAILURE, 404 ON THE DOMAIN")
            return_code = 1
            return return_code
     
    
# Tests domain_recon input argument handling for valid and invalid input
class TestDomainInput(MockGetDomainConfig):
    
    def test_invalid_tld(self):
        with self.assertRaises(KeyError):
            MockGetDomainConfig.bash_cmd_mock(self, domain = "duck.io")    

    def test_no_input(self):
        with self.assertRaises(FileNotFoundError):
            MockGetDomainConfig.bash_cmd_mock(self, domain = '') 

    def test_valid_tld(self):
        self.assertEqual(MockGetDomainConfig.bash_cmd_mock(self, domain = 'teamfire.org')[2], 'tests/assets/teamfire.org.conf')


# single 80 vhost test and vhost crawler test
# the unittest,TestCase library is inheirentied from the MockGetDomainConfig, which
# is inherieted by the TestVhostCrawlers class.
class TestVhostCralwers(MockGetDomainConfig):
    
    # Instaniate an instance of the vhost parser and the resulting processed vhost
    def setUp(self):
        self.domain = 'teamrocket.org'
        self.extracted_path = MockGetDomainConfig.bash_cmd_mock(self, domain = self.domain)[2]
        self.raw_vhosts = vhosts_extraction(self.extracted_path, self.domain)
        self.vhost_object = ApacheVirtualHost(raw_config=self.raw_vhosts[0], config_path=self.extracted_path)
        
    def test_conf_path(self):
        self.assertEqual(MockGetDomainConfig.bash_cmd_mock(self, domain = 'teamfire.org')[2], 'tests/assets/teamfire.org.conf')    
        
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
class TestClusteredVhosts(MockGetDomainConfig):
    
    # Instaniate an instance of the vhost parser and the resulting processed vhost
    def setUp(self):
        self.domain = 'clusterb.com'
        self.extracted_path = MockGetDomainConfig.bash_cmd_mock(self, domain = self.domain)[2]
        self.raw_vhosts = vhosts_extraction(self.extracted_path, self.domain)
        self.vhost_object = ApacheVirtualHost(raw_config=self.raw_vhosts[0], config_path=self.extracted_path)


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
class TestSubDomainVhost(MockGetDomainConfig):
    
    # Instaniate an instance of the vhost parser and the resulting processed vhost
    def setUp(self):
        self.domain = 'hideout.teamrocket.org'
        self.extracted_path = MockGetDomainConfig.bash_cmd_mock(self, domain = self.domain)[2]
        self.raw_vhosts = vhosts_extraction(self.extracted_path, self.domain)
        self.vhost_object = ApacheVirtualHost(raw_config=self.raw_vhosts[0], config_path=self.extracted_path)

    
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
class Test443_80Vhosts(MockGetDomainConfig):
    
    # Instaniate an instance of the vhost parser and the resulting processed vhost
    def setUp(self):
        self.domain = 'teamfire.org'
        self.extracted_path = MockGetDomainConfig.bash_cmd_mock(self, domain = self.domain)[2]
   
        # For a given configuration path, a vhost_object can contain one or two vhost configurations, 
        # which entirely depends if both 443/80 blocks are present. In this test, the second vhost (443)
        # is being pulled from the vhost_object. The first vhost is 80. 
        self.raw_vhosts = vhosts_extraction(self.extracted_path, self.domain)
        self.vhost_object = ApacheVirtualHost(raw_config=self.raw_vhosts[1], config_path=self.extracted_path)


    def test_source_config_path(self):
        self.assertEqual(self.vhost_object.source_config_path(), 'tests/assets/teamfire.org.conf')

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
class Test_80Vhosts(MockGetDomainConfig):
    
    # Instaniate an instance of the vhost parser and the resulting processed vhost
    def setUp(self):
        self.domain = 'teamfire.org'
        self.extracted_path = MockGetDomainConfig.bash_cmd_mock(self, domain = self.domain)[2]

        # For a given configuration path, a vhost_object can contain one or two vhost configurations, 
        # which entirely depends if both 443/80 blocks are present. In this test, the second vhost (443)
        # is being pulled from the vhost_object. The first vhost is 80. 
        self.raw_vhosts = vhosts_extraction(self.extracted_path, self.domain)
        self.vhost_object = ApacheVirtualHost(raw_config=self.raw_vhosts[0], config_path=self.extracted_path)


    def test_source_config_path(self):
        self.assertEqual(self.vhost_object.source_config_path(), 'tests/assets/teamfire.org.conf')

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
