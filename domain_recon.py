# This is the domain recon module for librecon
# The purpose of this module is to parse an dump of apache's vhost
# for the top level domain 'TLD' of the domain of interest.

import sys

from utils import do_cmd as bash_cmd


# TODO: implement error handeling for bad input, i.e no domain or domain that doesn't exist.
# The function returns two strings, ret contains the error code, 0 or 1 and the second string
# contains the information that the bash command returns
def get_domain_config_path(domain):
    ret, vhost = bash_cmd(f'httpd -S | grep "{domain}"')
    if ret == 1: 
        print(f'Domain: {domain} not found, exiting.')
        sys.exit(1)
    elif len(domain) == 0:
        print(f'No TLD provided, exiting.')
        sys.exit(1)
    domain_config_path = vhost.split('(')[-1].split(':')[0]
    return domain_config_path


# testing
# domain = 'teamfire.org'
domain = input('Initializing Domain Recon.. Please enter the TLD to recon: ')

# extracts the absolute path of the vhost config for the specified TLD
extracted_path = get_domain_config_path(domain)

ret, domain_info = bash_cmd(f'grep -i \'document\|log\' {extracted_path}')

# created an empty list to store strings that contains cleaned up output
# from the apache vhost dump
clean_domain_info = list()

# iterating over domain_info, splitting into substrings on \n
for item in domain_info.split('\n'):
    # print(f'DEBUG: {item}')
    # itermediate variable to strip item of whitespace
    clean_item = item.strip()
    # if the string length of clean_item > 0, append the substring to the 
    # clean_domain_info variable 
    if len(clean_item) > 0:
        clean_domain_info.append(clean_item)


# item is an list that contains the following:
# -document_root
# -custom/access logs
# -error logs


# Discovery markers
DOCUMENT_ROOT_MARKER = 'DocumentRoot'
CUSTOM_LOG_MARKER = 'CustomLog'
ERROR_LOG_MARKER = 'ErrorLog'

http = {}

# info is a string split on an whitespace character into two strings: keyword and /path/to/some/log
for line in clean_domain_info:
    if DOCUMENT_ROOT_MARKER in line:
        info = line.split(' ')
        http['document_root'] = info[1]
    elif CUSTOM_LOG_MARKER in line:
        info = line.split(' ')
        http['custom_log'] = info[1]
    elif ERROR_LOG_MARKER in line:
        info = line.split(' ')
        http['error_log'] = info[1]


print(f'\n')
print(f'The following information was reconned:')
print(f'Vhost Configuration: {extracted_path}')

for vhost, directive in http.items():
    print(f"{vhost} : {directive}") 
