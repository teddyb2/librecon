# This is the domain recon module for librecon
# The purpose of this module is to parse an dump of apache's vhost
# for the top level domain 'TLD' of the domain of interest.

import sys

from utils import do_cmd as bash_cmd


# TODO: Remove comments once the final refactor for the vhost parser is complete

def get_domain_config_path(domain):
    ret, vhost = bash_cmd(f'httpd -S | grep "{domain}"')
    if ret == 1: 
        print(f'Domain: {domain} not found, exiting.')
        sys.exit(1)
    elif len(domain) == 0:
        print(f'No TLD provided, exiting.')
        sys.exit(1)
    # print(f'DEBUG_VHOST_RAW: {vhost}')    
    #domain_config_path = vhost.split('(')[-1].split(':')[0]
    domain_config_path = vhost.split('\n') 
    # print(f'DEBUG_PATH_AFTER: {domain_config_path}')
    return domain_config_path


# testing
# domain = 'teamfire.org'
domain = input('Initializing Domain Recon.. Please enter the TLD to recon: ')


# extracts the absolute path of the vhost config for the specified TLD
# need to work with extracted paths and break it into a dict of port 80/443 vhost paths
extracted_path = get_domain_config_path(domain)


# {domain - top level dict} : {http}
#                           : {https}


domain = { 'http' : {'vhost_config': ''}, 'https' : {'vhost_config': ''}}

#  vhost path extraction for 80/443, itemizing into respective dictionary
for line in range(len(extracted_path)):
    # print(f'DEBUG_LINE = {line}')
    if 'port 443' in extracted_path[line]:
        domain['https']['vhost_config'] = extracted_path[line].split('(')[-1].split(':')[0]
        print(f'Vhost 443: {extracted_path[line]}')
    elif 'port 80' in extracted_path[line]:
        domain['http']['vhost_config'] = extracted_path[line].split('(')[-1].split(':')[0]
        print(f'Vhost 80: {extracted_path[line]}')

# END VHOST PATH EXTRACTION

# HTTPS/HTTP dict debug:
# https_debug = domain['https']['vhost_config']
# http_debug = domain['http']['vhost_config']

# print(f'HTTPS_VHOST_PATH: {https_debug}')
# print(f'HTTP_VHOST_PATH: {http_debug}')


# Iterate over the sub-dicts http and https. If the vhost_config key is
# not blank, then I should iterate over the entire sub-dict and populate the various
# keys "access_log, custom_log, server_alias, etc"

http_clean_domain_info = list()
https_clean_domain_info = list()

# Discovery markers
DOCUMENT_ROOT_MARKER = 'DocumentRoot'
CUSTOM_LOG_MARKER = 'CustomLog'
ERROR_LOG_MARKER = 'ErrorLog'

# Vhost Information Extraction
for key, directive in domain.items():
    
    if 'https' in key and directive['vhost_config'] != '':
        # print(f'DEBUG_HTTPS_DIRECTIVE: {directive}')
        # print(f'DEBUG HTTPS_KEY: {key}')
        extracted_path = domain['https']['vhost_config']
        # print(f'HTTPS EXTRACT_PATH: {extracted_path}')
        ret, https_domain_info = bash_cmd(f'grep -i \'document\|log\' {extracted_path}')

        for item in https_domain_info.split('\n'):
            # print(f'DEBUG: {item}')
            # itermediate variable to strip item of whitespace
            clean_item = item.strip()
            # if the string length of clean_item > 0, and the string does not
            # start with "#"," append the substring to the 
            # clean_domain_info variable 
            if len(clean_item) > 0 and not clean_item.startswith("#"):
                https_clean_domain_info.append(clean_item)
        # iterating over domain_info, splitting into substrings on \n
        for line in https_clean_domain_info:
            if DOCUMENT_ROOT_MARKER in line:
                info = line.split(' ')
                domain['https']['document_root'] = info[1]
            elif CUSTOM_LOG_MARKER in line:
                info = line.split(' ')
                domain['https']['custom_log'] = info[1]
            elif ERROR_LOG_MARKER in line:
                info = line.split(' ')
                domain['https']['error_log'] = info[1]

    elif 'http' in key and directive['vhost_config'] != '':
        # print(f'DEBUG_HTTP_DIRECTIVE: {directive}')
        # print(f'DEBUG_HTTP_KEY: {key}')
        extracted_path = domain['http']['vhost_config']
        # print(f'HTTP EXTRACT_PATH: {extracted_path}')
        ret, http_domain_info = bash_cmd(f'grep -i \'document\|log\' {extracted_path}')
        # iterating over domain_info, splitting into substrings on \n
        for item in http_domain_info.split('\n'):
            # print(f'DEBUG: {item}')
            # itermediate variable to strip item of whitespace
            clean_item = item.strip()
            # if the string length of clean_item > 0, and the string does not
            # start with "#"," append the substring to the 
            # clean_domain_info variable 
            if len(clean_item) > 0 and not clean_item.startswith("#"):
                http_clean_domain_info.append(clean_item)
        for line in http_clean_domain_info:
            if DOCUMENT_ROOT_MARKER in line:
                info = line.split(' ')
                domain['http']['document_root'] = info[1]
            elif CUSTOM_LOG_MARKER in line:
                info = line.split(' ')
                domain['http']['custom_log'] = info[1]
            elif ERROR_LOG_MARKER in line:
                info = line.split(' ')
                domain['http']['error_log'] = info[1]


# created an empty list to store strings that contains cleaned up output
# from the apache vhost dump

# item is an list that contains the following:
# -document_root
# -custom/access logs
# -error logs

# http = {}

print(f'\n')
print(f'The following information was reconned:')
print(f'Vhost Configuration: {extracted_path}')


# testing new print statements

# printer_iteration = 0
printed_443 = False
printed_80 = False

for key, directive in domain.items():
    #printer_iteration += 1
    if domain['https']['vhost_config'] != '' and printed_443 != True:
        # print(f'HTTPS Vhost Info: ')
        # print(f'DEBUG_HTTPS_DOMAIN: {DEBUG_HTTPS_DOMAIN}')
        printed_443 = True
        print('PRINT 443:')
        for vhost, directive in domain['https'].items():
            print(f"{vhost} : {directive}")
    
    elif domain['http']['vhost_config'] != '' and printed_80 != True:
        print('PRINT 80:')
        # print(f'HTTP Vhost Info: ')
        printed_80 = True
        # print(f'DEBUG_HTTP_DOMAIN: {domain}')
        for vhost, directive in domain['http'].items():
            print(f"{vhost} : {directive}")

# print(f'Printer Iterations: {printer_iteration}')
