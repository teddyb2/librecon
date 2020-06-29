#This is the domain recon module for librecon
#The purpose of this module is to parse an dump of apache's vhost
#for the top level domain "TLD" of the domain of interest.

import sys

from utils import do_cmd as bash_cmd
#to-do implement error handeling for bad input, i.e no domain or domain that doesn't exist.
#The function returns two strings, ret contains the error code, 0 or 1 and the second string
#contains the information that the bash command returns
def get_domain_config_path(domain):
    ret, vhost = bash_cmd(f'httpd -S | grep {domain}')
    if ret == 1: 
        print(f"Domain: {domain} not found, exiting.")
        sys.exit(1)
    elif ret == 2:
        print(f"No TLD provided, exiting.")
        sys.exit(1)
    return vhost.split('(')[-1].split(':')[0]

#testing, domain = "teamrocket.org"
domain = input("Initializing Domain Recon.. Please enter the TLD to recon: ")


#extracts the absolute path of the vhost config for the specified TLD
extracted_path = get_domain_config_path(domain)

ret, domain_info = bash_cmd(f'grep -i "document\|log" {extracted_path}')

#created an empty list to store strings that contains cleaned up output
#from the apache vhost dump
clean_domain_info = list()

#iterating over domain_info, splitting into substrings on \n
for item in domain_info.split('\n'):
    #itermediate variable to strip item of whitespace
    clean_item = item.strip()
    #if the string length of clean_item > 0, append the substring to the 
    #clean_domain_info variable 
    if len(clean_item) > 0:
        clean_domain_info.append(clean_item)

#list comprehension
item = [item.strip() for item in domain_info.split('\n') if len(item) > 0]

#item is an list that contains the following:
#-documentroot
#-custom/access logs
#-error logs

#to-do: create an dictionary that contains key value pairs of httpd directives to config locations absolute
vhost_info = {}

documentroot = "DocumentRoot"
customlog = "CustomLog"
errorlog = "ErrorLog"

#info is a string split into two strings: keyword and /path/to/some/log
for line in item:
    if documentroot in line:
        info = line.split(' ')
        document_root_path = info[1]
    elif customlog in line:
        info = line.split(' ')
        custom_log_path = info[1]
    elif errorlog in line:
        info = line.split(' ')
        error_log_path = info[1]

#This section returns the basic information above the domain to the user
print(f'\n')
print(f'The following information was reconned:')
print(f'Vhost Configuration: {extracted_path}') 
print(f'{documentroot}: {document_root_path}')
print(f'{customlog}: {custom_log_path}')
print(f'{errorlog}: {error_log_path}')