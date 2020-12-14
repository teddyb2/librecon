
from unittest import mock
import unittest
import sys

# from domain_recon import get_domain_config_path
# from domain_recon import vhosts_extraction
# from domain_recon import ApacheVirtualHost

#from utils import do_cmd as bash_cmd
from utils import do_cmd
import subprocess


class TestBashCMD(unittest.TestCase):
    
    # tests that do_cmd can be called with an specified argument
    @mock.patch('utils.do_cmd')
    def test_mock_cmd(self, mock_do_cmd):

        mock_do_cmd.do_cmd('echo hello')
        

        #mock_do_cmd.assert_called_with('echo hello')
        
        #mock_do_cmd.do_cmd.assert_called_with('echo hello')


        # testing that do_cmd was called
        #mock_do_cmd.do_cmd.assert_called()

        # testing that do_cmd was called with the argument 'echo hello'
        mock_do_cmd.do_cmd.assert_called_with('echo hello')


    # need to state the mock.patch for each test method. Each method/module keeps it's own imports
    # test if the do_cmd method can be called w/o arguments
    @mock.patch('utils.do_cmd')
    def test_call_do_cmd(self, mock_call_cmd):
        
        # calling the do_cmd function from utils
        mock_call_cmd.do_cmd()

        mock_call_cmd.do_cmd.assert_called()


    @mock.patch('utils.do_cmd')
    def test_invalid_args(self, mock_args_cmd):


        # mocking do_cmd return code as 0, which would indicate the command completed successfully
        #mock_args_cmd.do_cmd.return_value = 0

        # bullshit arg to do_cmd to intentially cause failure
        #mock_args_cmd.do_cmd('fluffy bunny') 

        # valid arg to do_cmd, it should change the return value to 1
        #mock_args_cmd.do_cmd('booty') 

        # checking if the command "failed" as expected
        #mock_args_cmd.do_cmd.assert_return_value(1)


        # cannot test for the return code in this manner, as for the mocked version of do_cmd 
        # litterally does not thave the functionality. Mock_args_cmd does not actually execute code, hence forth
        # it cannot return a status code.
        with self.assertRaises(SystemExit) as cm:
            mock_args_cmd.do_cmd('motddddd') 
        mock_args_cmd.do_cmd.assertEqual(cm.exception.code, 1)


        #mock_args_cmd.do_cmd.assert_equal(return_code, 127)



# scratch code:
# 
#         with self.assertRaises(SystemExit) as cm:
        #     get_domain_config_path(domain)
        # self.assertEqual(cm.exception.code, 1)        