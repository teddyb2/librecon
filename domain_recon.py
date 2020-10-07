# This is the domain recon module for librecon
# The purpose of this module is to parse an dump of apache's vhost
# for the top level domain 'TLD' of the domain of interest.

import sys
import re

from utils import do_cmd as bash_cmd


def get_domain_config_path(domain):
    ret, vhost = bash_cmd(f'httpd -S | grep -i "{domain}"')
    if ret == 1:
        print(f'Domain: {domain} not found, exiting.')
        sys.exit(1)
    elif len(domain) == 0:
        print(f'No TLD provided, exiting.')
        sys.exit(1)
    
    final = vhost.split('\n')
    paths = list(set([line.split('(')[-1].split(':')[0] for line in final if '(' in line]))
 
    # DEBUG: prints the absolute path(s) of the vhosts for the requested tld
    # print(f'DEBUG_PATH_AFTER: {paths}')
    return paths


# ========== Raw Vhost Parsing And Extraction ============================
def vhosts_extraction(extracted_paths):

    # Regex to find the opening <VirtualHost *:443/80> and closing </VirtualHost> tags and grab
    # everything inbetween
    vhost_reg = re.compile(r"(<VirtualHost.+?>.*?</VirtualHost>)",re.DOTALL)

    # List containing string contents of each config file.
    apache_config_files = []
    for path in extracted_paths:
        with open(path, 'r') as config_file:
           config_contents = config_file.read()
           apache_config_files.append(config_contents)

    extracted_vhosts = []
    for apache_config_file in apache_config_files:

        config_lines_without_comments = []
        for line in apache_config_file.split('\n'):
            line = line.strip()
            if not line.startswith('#'):
                config_lines_without_comments.append(line)

        config_without_comments = '\n'.join(config_lines_without_comments)
        vhost_matches = vhost_reg.findall(config_without_comments)

        for vhost in vhost_matches:
            extracted_vhosts.append(vhost)

    # DEBUG: prints the regex matched contents of an extracted vhost(s) w/o disabled directives
    # print(f'DEBUG EXTRACTED VHOST: {extracted_vhosts}')
    
    return extracted_vhosts

# ========================================


class ApacheVirtualHost(object):
    def __init__(self, raw_config=None):
        self.raw_config  = raw_config
        self.clean_config_list = []

        # When the class is instantiated, the _parse_config() method will
        # automatically be called to clean up raw_config.
        self._parse_config()


    def _parse_config(self):
        
        # print('DEBUG: ApacheVirtualHost class ingested raw vhost:')
        # print(self.raw_config)
        
        clean_config = [l.strip() for l in self.raw_config.split('\n')]
        non_blank_config = [l for l in clean_config if l != '' and not l.startswith('#')]

        self.clean_config_list = non_blank_config

        # DEBUG: prints the processed vhost configuration
        # print(f'DEBUG_CLEAN_CONF: {self.clean_config_list}')
        

    def document_root(self):
        return [l for l in self.clean_config_list if 'DocumentRoot' in l][-1].split(' ')[-1]


    def error_log(self):
        return [l for l in self.clean_config_list if 'ErrorLog' in l][-1].split(' ')[-1]


    def server_name(self):
        return [l for l in self.clean_config_list if 'ServerName' in l][-1].split(' ')[-1]


# testing
# domain = 'teamfire.org.conf'
domain = input('Initializing Domain Recon.. Please enter the TLD to recon: ')

# extracts the absolute path of the vhost config for the specified TLD
extracted_paths = get_domain_config_path(domain)

# extracting raw vhost information
raw_vhosts = vhosts_extraction(extracted_paths)

vhost_objects = []
for raw_vhost in raw_vhosts:
    vhost_objects.append(ApacheVirtualHost(raw_config=raw_vhost))

for vhost in vhost_objects:
     print('Document Root: ', vhost.document_root())
     print('Error Log: ', vhost.error_log())
     print('Server Name:', vhost.server_name())

# DEBUG: prints the absolute path(s) for reconned vhost(s)
# print(f"DEBUG_EXTRACTED_PATHS: {extracted_paths}")
