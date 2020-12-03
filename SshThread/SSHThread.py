"""
--------------------------------------------------------------------
Michigan  Technological University: Blue Marble Security Enterprise
--------------------------------------------------------------------
SSHThread.py

Code Based on Demo: https://github.com/paramiko/paramiko/

Author: Corbin Holz
Date last modified: 12/1/2020
"""

__author__ = 'Blue Marble Security Enterprise'
__version__ = '1.0'

# Import base 64 if using a secure SSH
# import base64
import threading
import time
import paramiko
import sys

class SSHThread(threading.Thread):

    def __init__(self):

        # Create the default variables
        # Define the host, username, and password
        self.client = paramiko.SSHClient()
        self.hostname = 'localhost'
        self.user = 'niryo'
        self.userpass = 'robotics'
        self._command_list = []

        # Since SSH allows for secure connections with keys, allow to auto accept keys without passwords
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Otherwise uncomment and add keys
        # key = paramiko.RSAKey(data=base64.b64decode(b'AAA...'))
        # client.get_host_keys().add('ssh.example.com', 'ssh-rsa', key)

    def run(self):
        self.client.connect(self.hostname, username=self.user, password=self.userpass)
        
        # Move the listener script
        ftp_client = self.client.open_sftp()
        remotepath = '/home'
        ftp_client.put('listener.py', remotepath)
        ftp_client.close()

        # Exec the python script
        stdin, stdout, stderr = self.client.exec_command('source ~/catkin_ws/devel/setup.bash && export PYTHONPATH=${PYTHONPATH}:/home/niryo/catkin_ws/src/niryo_one_python_api/src/niryo_python_api && python listener.py')

        # Write commands
        userIn = ""
        while (userIn != "QUIT"):
            # Wait until "WAIT" is recieved
            output = stdout.readlines()
            while (output[-1] != "WAIT"):
                # Don't poll as soon as possible for performance
                # Only poll every second
                time.sleep(1)
                output = stdout.readlines()

            # Wait for commands (loop if empty)
            while (not self._command_list):
                time.sleep(1)

            # FIFO commands
            stdin.write(self._command_list.pop(0))
            stdin.flush()

                
        self.client.close()

    """
    _append_command
    Appends passed command to the command list
    input: new_command
    """
    def _append_command(new_command):
        if (new_command not in self._command_list):
            self._command_list.append(new_command)