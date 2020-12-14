import sys, getopt
from utils import do_cmd as bash_cmd


#domain = input('Initializing Domain Recon.. Please enter the TLD to recon: ')


# when the get_vhost.py is run directly, then run the code below
def main():

    domain = input('Initializing Domain Recon.. Please enter the TLD to recon: ')
    vhost_confs = get_domain_config_paths(domain)
    print(f'Location of Vhost Confs: {vhost_confs}')


def get_domain_config_paths(domain):
    ret, vhost = bash_cmd(f'httpd -S | grep -i "{domain}"')
    if ret == 1:
        print(f'Domain: {domain} not found, exiting.')
        sys.exit(1)
    elif len(domain) == 0:
        print(f'No TLD provided, exiting.')
        sys.exit(1)

    final = vhost.split('\n')
    paths = list(set([line.split('(')[-1].split(':')[0] for line in final if '(' in line]))
    
    return paths


#vhost_confs = get_domain_config_path(domain)
#print(f'Location of Vhost Confs: {vhost_confs}')

        #domain = input('Initializing Domain Recon.. Please enter the TLD to recon: ')
    
    #domain = input('Initializing Domain Recon.. Please enter the TLD to recon: ')
    

if __name__ == '__main__':
    main()
    #run regular INPUT for domain
# else:
#     domain = sys.argv[1]    

# need an else statement here to accept input for the domain variable to handle when this
# # script get_vhost.py is imported as an module in another script such as test_get_vhost.py     
    



