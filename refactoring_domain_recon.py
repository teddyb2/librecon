# This is the domain recon module for librecon
# The purpose of this module is to parse an dump of apache's vhost
# for the top level domain 'TLD' of the domain of interest.

import sys
import re

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
    print(f'DEBUG_VHOST_RAW: {vhost}')

    #domain_config_path = vhost.split('(')[-1].split(':')[0]
    final = vhost.split('\n')
    paths = list(set([line.split('(')[-1].split(':')[0] for line in final if '(' in line]))

    #domain_config_path = vhost.split('(')[-1].split(':')[0]
    #domain_config_path = vhost.split('\n') 
    #print(f'DEBUG_PATH_AFTER: {domain_config_path}')
    return paths


# testing
domain = 'teamfire.org'
#domain = input('Initializing Domain Recon.. Please enter the TLD to recon: ')


# extracts the absolute path of the vhost config for the specified TLD
# need to work with extracted paths and break it into a dict of port 80/443 vhost paths
extracted_paths = get_domain_config_path(domain)

print(f"Debug: {extracted_paths}")

# ========== Raw Vhost Parsing And Extraction ============================
def vhosts_extraction(extracted_paths):

    # Regex to find the opening <VirtualHost *:443/80> and closing </VirtualHost> tags and grab
    # everything inbetween 
    vhost_reg = re.compile(r"(<VirtualHost.+?>.*?</VirtualHost>)",re.DOTALL)

    # instaniates the file reader in read-only mode
    # f = open(extracted_paths[1], 'r')
    
    # temporary holding list for the raw vhost data
    temp_results = []

    for item in range(len(extracted_paths)):
        f = open(extracted_paths[item], 'r')
        raw_vhosts = f.read()
        temp_results.append(raw_vhosts)

    # results is a list that contains all parsed vhosts blocks and 
    results = vhost_reg.findall(raw_vhosts)

    # Debug
    # print(f'RES_DEBUG: {results}')

    # itemizing the retrieved 443/80 vhosts into their respective sub-dicts in domain top level dict
    # {domain - top level dict} : {http}
    #                           : {https}
    raw_domain_info = { 'http' : {'vhost_config': ''}, 'https' : {'vhost_config': ''}}

    # Takes the raw 443/80 vhosts and assigns them to the respectiive https/http sub-dicts in the domain dict
    for line in range(len(results)):
        # print(f'DEBUG_LINE = {line}')
        if ':443' in results[line]:
            raw_domain_info['https']['vhost_config'] = results[line].split('\n')
            print(f'Vhost 443: {results[line]}')
        elif ':80' in results[line]:
            raw_domain_info['http']['vhost_config'] = results[line].split('\n')
            print(f'Vhost 80: {results[line]}')

    return raw_domain_info
  
# ========================================

# extracting raw vhost information
raw_domain_info = vhosts_extraction(extracted_paths)

# class vhost_info which contains various methods to pull specific information from the vhost
# example usage:

# method that will be used by other methods to seek information from the vhosts
# takes two arguments, the raw_domain dict and directive, which will be an user specified
# search term such as Server Alias, ErrorLog, etc 
# def info_seeker(raw_domain_info, directive):
def info_seeker(directive):

    # intermediate holding lists
    http_clean_domain_info = list()
    https_clean_domain_info = list()

    for key, directive in raw_domain_info.items():
        # detects if 'https' subdict in raw_domain_info is populated
        if 'https' in key and directive['vhost_config'] != '':
            print('HTTPS DETECT')

        for item in raw_domain_info:
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
            print(f'DEBUG_CLEAN_INFO_DIRECTIVE: {directive}')
            print(f'DEBUG_LINE: {line}')
            #if directive in line:
            if line in directive:
                info = line.split(' ')
                raw_domain_info['https'][directive] = info[1]



directive = 'DocumentRoot'
# test call to info seeker - finding DocumentRoot
doc_root = info_seeker(directive)

print(f'The DocumentRoot is: {doc_root}')

# TODO: copy the vhost extraction section from the current version of domain_recon.py
# transform it into a method that allows you specify the vhost directive to seek
# remove hard coding for the DOCUMENT_ROOT_MARKER, the method will be dynamic and should be able to
# accept any vhost directive as an argument which will substitute DOCUMENT_ROOT_MARKER, search for 
# it and if found, append it to the appropiate sub-dict in raw_domain_info dict

# results.logs --> returns the domain's log file directivies
# results.redirect --> returns the domain's redirect rules
# results.name --> return the domain's ServerName and all aliases

# logs

# method that grabs Redirects