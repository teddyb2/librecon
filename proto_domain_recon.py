# Prototype version of domain recon that uses the whole vhost parser

import sys

from utils import do_cmd as bash_cmd


# TODO: Remove comments once the final refactor for the vhost parser is complete

conf_match = '.conf'
abs_vhosts = []

ret, active_vhosts = bash_cmd(f'httpd -S')
seperated_active_vhosts = active_vhosts.split('\n')

# parses the seperated_active_vhosts list and stores the 
# absolute path of any active vhost in the abs_vhosts list
for line in seperated_active_vhosts:
    if conf_match in line:
        #print(line.split('(')[-1].split(':')[0])
        cleaned = line.split('(')[-1].split(':')[0]
        abs_vhosts.append(cleaned)
