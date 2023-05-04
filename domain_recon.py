# This is the domain recon module for librecon
# The purpose of this module is to parse an dump of apache's vhost
# for the top level domain 'TLD' of the domain of interest.

import sys
import re
import argparse
import logging


from utils import do_cmd as bash_cmd


def main():
    description = 'Pull relevent Apache vhost directives for investigation, including logs and more for a given domain hosted locally.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--domain', type=str, required=True, help='Fully qualified domain name to recon locally.')
    parser.add_argument('--debug', required=False, action='store_true', help='Enable verbose debug output.')
    args = parser.parse_args()

    domain=args.domain
    debug=args.debug

    if debug == True:
        print('DEBUG Mode Enabled!')
        logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s"
        ) # You can change the logging level to INFO, DEBUG CRITICAL, ERROR, ETC
    else:
        logging.basicConfig(
        level=logging.disable(0),
        format="%(asctime)s - %(levelname)s - %(message)s"
        )

    # Calling recon method with supplied arguments from user
    recon(domain,debug)


def recon(domain,debug):
    active_vhosts = get_apache_active_vhosts()

    # extracts the absolute path of the vhost config for the specified TLD
    extracted_paths = get_apache_config_paths(active_vhosts)

    # extracting raw vhost information
    vhost_objects = []

    # {domain_name : {nested dict}}
    processed_vhosts = vhosts_extraction(extracted_paths, domain)

    # experiment
    for conf_path in processed_vhosts.keys():
        vhost_objects.append(ApacheVirtualHost(raw_config=processed_vhosts, config_path=conf_path))


   # Checks if the domain exists by checking the list of vhost objects for a vhost
   # object with a matching server_name.
   # If the domain doesn't exists, then vhost objects will not have any objects.
   # The vhosts_Extraction method returns nothing if it can't find a domain.
    if len(vhost_objects) == 0:
       print('TLD not found on server, exiting.')
       sys.exit(1)

    for vhost in vhost_objects:

        print('**************************************')
        print('Configure Path:', vhost.config_path)
        print('Server Name:', vhost.server_name())
        print('Server Alias:', vhost.server_alias())
        print('Document Root:', vhost.document_root())
        print('Error Log:', vhost.error_log())
        print('Custom Log:', vhost.custom_log())
        print('SSL Cert:', vhost.ssl_cert())
        print('SSL Key:', vhost.ssl_key())
        print('SSL Chain:', vhost.ssl_chain())
        print('\n')


# TODO implement get_nginx_vhosts()
# def get_nginx_active_vhosts():
#   command or commands to dump nginx
# return nginx_vhosts


def get_apache_active_vhosts():
    '''Dumps the active apache vhosts via httpd -S into a string'''
    ret, vhosts = bash_cmd('httpd -S')
    if ret == 1:
        print(f'Apache failed to dump vhosts, exiting.')
        sys.exit(1)
    return vhosts


def get_apache_config_paths(active_vhosts):
    '''Takes the active vhost dump 'httpd -S' and extracts vhost configuration paths
       as a list of absolute paths'''
    # Split the vhost string blob on new line character into seperate strings
    final = active_vhosts.split('\n')

    # paths is a list of strings containing the absolute paths of vhost configuration files.
    # Unfiltered output from httpd -S
    # port 443 namevhost teamfire.org (/etc/httpd/conf.d/teamfire.org.conf:36)

    # The list is iterated, each path split on the first '(' and split on the ':'
    # This strips away the unnecessary info, resulting in a usable absolute path to the vhost configuration:
    # /etc/httpd/conf.d/teamfire.org.conf
    paths = list(set([line.split('(')[-1].split(':')[0] for line in final if '(' in line]))

    # DEBUG: prints the absolute path(s) of the active vhosts
    logging.debug(f'EXTRACTED_VHOST_PATHS: {paths}')

    return paths


# ========== Raw Vhost Parsing And Extraction ============================
def vhosts_extraction(extracted_paths, domain):

    # Regex to find the opening <VirtualHost *:443/80> and closing </VirtualHost> tags and grab
    # everything inbetween
    vhost_reg = re.compile(r"(<VirtualHost.+?>.*?</VirtualHost>)",re.DOTALL)

    # List comprised of strings containing contents of each config file.
    apache_config_files = {}

    # Populates a list of raw apache config files read from disk

    print(f"DEBUG-EXTRACTED-PATHz: {extracted_paths}")
    print(f"DEBUG PATH OBJECT TYPE {type(extracted_paths)}")
    for path in extracted_paths:
        with open(path, 'r') as config_file:
            config_contents = config_file.read()
            apache_config_files[path] = config_contents # seems to work for storing {'config_path: 'vhost_content'}

    extracted_vhosts = {}

    for path in apache_config_files:

        config_lines_without_comments = []
        for line in apache_config_files[path].split('\n'):
            line = line.strip()
            if not line.startswith('#'):
                config_lines_without_comments.append(line)

        config_without_comments = '\n'.join(config_lines_without_comments)
        vhost_matches = vhost_reg.findall(config_without_comments)

    # checks that the extracted vhost block matches the specified domain by searching for the domain name in the vhost block
    # compares the search tld in lowercase against the paresed domain's in lowercase.
        for vhost in vhost_matches:
            if domain.lower() in vhost.lower():
                extracted_vhosts.update({path : vhost}) # <--This overwrites a vhosts. If a TLD has two vhosts in the same vhost
                                                        # configuration file, one of them will be over written!
                                                        # Check if "SSLEngine On" is set. The presense of this directive definitively defines an https vhost

    return extracted_vhosts


# ========== Class for crawling extracted_vhosts for desired directives ===
class ApacheVirtualHost(object):
    def __init__(self, raw_config, config_path=None):
        self.clean_config_list = []
        self.config_path = config_path
        print("### DOMAIN RECON DEBUBG ###")
        print(f"DEBUG DOMAIN-RECON CONFIG PATH: {config_path}")
        print(f"DEBUG DOMAIN-RECON RAW_CONFIG: {raw_config}")
        self.raw_config  = raw_config[config_path]

        logging.debug(f'VHOST PATH: {config_path}')
        # When the class is instantiated, the _parse_config() method will
        # automatically be called to clean up a raw_config.
        self._parse_config()


    def _parse_config(self):
        # DEBUG: Unmodified ApacheVirtualHost object
        logging.debug(f'RAW VHOST: \n{self.raw_config}\n')

        clean_config = [l.strip() for l in (self.raw_config).split('\n')]
        non_blank_config = [l for l in clean_config if l != '' and not l.startswith('#')]
        self.clean_config_list = non_blank_config

        # DEBUG: prints the processed vhost configuration
        logging.debug(f'PROCESSED VHOST CONFIGURATION: {self.clean_config_list}\n')


    def source_config_path(self):
        return self.config_path

    def server_name(self):
        return self._find_directive('ServerName')

    def server_alias(self):
        return self._find_directive('ServerAlias')

    def document_root(self):
        return self._find_directive('DocumentRoot')

    def error_log(self):
        return self._find_directive('ErrorLog')

    def custom_log(self):
        return self._find_directive('CustomLog')

    def ssl_cert(self):
        return self._find_directive('SSLCertificateFile')

    def ssl_key(self):
        return self._find_directive('SSLCertificateKeyFile')

    def ssl_chain(self):
        return self._find_directive('SSLCertificateChainFile')

    # checks if the directive exists in the parsed vhost. Sets directive as 'not set' if missing
    def _find_directive(self, directive):

        # adjusts the list comprehension to offset by -2 to grab the abs path to the log instead of log facility
        if directive == 'CustomLog':
            return [l for l in self.clean_config_list if directive in l][-1].split(' ')[-2]
        else:
            try:
                return [l for l in self.clean_config_list if directive in l][-1].split(' ')[-1]
            except IndexError:
                return None


if __name__ == '__main__':
     main()
