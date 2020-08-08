#Evan Gray's bash cmd method for executing bash commands from python

import subprocess
def do_cmd(command, verbose=False):
    if verbose is True: 
        print('[+] running cmd: %s' % command)
    return_code = 0
    try:
        output = subprocess.check_output([command], shell=True,
                                         stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        print('[!] Error running cmd: %s' % command)
        output = err.output
        return_code = err.returncode
    if verbose is True:
        print('[+] command output: %s' % output)
    return (return_code, output.decode("utf-8"))
