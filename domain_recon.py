# This is the domain recon module for librecon
# The purpose of this module is to parse an dump of apache's vhost
# for the top level domain 'TLD' of the domain of interest.

import sys
import re

from utils import do_cmd as bash_cmd


def main():
    domain = input('Initializing Domain Recon.. Please enter the TLD to recon: ')
    
    # extracts the absolute path of the vhost config for the specified TLD
    extracted_paths = get_domain_config_path(domain)
    
    # extracting raw vhost information
    vhost_objects = []
    for path in extracted_paths:
        raw_vhosts = vhosts_extraction(path, domain)
        for raw_vhost in raw_vhosts:
            vhost_objects.append(ApacheVirtualHost(raw_config=raw_vhost, config_path=path))

    for vhost in vhost_objects:
            
        print(f'**************************************')
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
def vhosts_extraction(extracted_paths, domain):

    # Regex to find the opening <VirtualHost *:443/80> and closing </VirtualHost> tags and grab
    # everything inbetween
    vhost_reg = re.compile(r"(<VirtualHost.+?>.*?</VirtualHost>)",re.DOTALL)

    # List comprised of strings containing contents of each config file.
    apache_config_files = []

    with open(extracted_paths, 'r') as config_file:
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

    # checks that the extracted vhost block matches the specified domain by searching for the domain name in the vhost block
        for vhost in vhost_matches:
            if domain.lower() in vhost.lower():
                extracted_vhosts.append(vhost)

    # DEBUG: prints the regex matched contents of an extracted vhost(s) w/o disabled directives
    #print(f'DEBUG EXTRACTED VHOST: {extracted_vhosts}')
    
    return extracted_vhosts


# ========== Class for crawling extracted_vhosts for desired directives ===
class ApacheVirtualHost(object):
    def __init__(self, raw_config=None, config_path=None):
        self.raw_config  = raw_config
        self.clean_config_list = []
        self.config_path = config_path

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
                return 'Not Set'


if __name__ == '__main__':
     main()
