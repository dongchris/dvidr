import paramiko
import os
from ocr import *

def login_server(hostname, username, key):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    k = paramiko.RSAKey.from_private_key_file(key)
    ssh.connect(hostname=hostname,
                username=username, 
                pkey=k)
    print('Connected!')
    return ssh

def setup_server(ssh, script):
    stdin, stdout, stderr = ssh.exec_command(f"sudo python {script}")
    print('Server launched!')

def deploy():
    ssh = login_server(hostname, username, key)
    setup_server(ssh, server_script)
    ssh.close()
    print('Done!')

if __name__ == '__main__':
	hostname = 'ec2-34-212-189-39.us-west-2.compute.amazonaws.com'
	username = 'ec2-user'
	key  = 'zhengjxu-west.pem'
	server_script = '/home/ec2-user/group-assignment-2-dvidr/code/websites/server.py'

	deploy()