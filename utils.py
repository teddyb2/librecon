#Evan Gray's bash cmd method for executing bash commands from python

import subprocess
def do_cmd(command):
    print('[+] running cmd: %s' % command)
    return_code = 0
    try:
        output = subprocess.check_output([command], shell=True,
                                         stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        print('[!] Error running cmd: %s' % command)
        output = err.output
        return_code = err.returncode
    print('[+] command output: %s' % output)
    return (return_code, output)