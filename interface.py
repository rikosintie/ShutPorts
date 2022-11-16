'''
Import a json file of port status created by procurve-Config-Push.py
create a file to disable any port that is down
File name - 01_[hostname]-interface-disable.txt
read the file and send the commands to disable ports.
create a log file 01_[hostname]-disable-output.txt

See procurve-Config-Push.py docstring for more information
python interface.py -s <site name>

---Error Handling ---
The connect handler is wrapped in a try/except block.
If a time out occurs when connecting to a switch it is trapped
but the  script halts.

References:
https://linuxhandbook.com/python-write-list-file/
https://www.tutorialspoint.com/python3/python_dictionary.htm
 '''

__author__ = "Michael Hubbard"
__author_email__ = "mhubbard@vectorusa.com"
__copyright__ = ""
__license__ = "Unlicense"

from datetime import datetime
from netmiko import ConnectHandler
from netmiko import exceptions
from paramiko.ssh_exception import SSHException
import os
import argparse
import sys
import json

def remove_empty_lines(filename):
    if not os.path.isfile(filename):
        print("{} does not exist ".format(filename))
        return
    with open(filename) as filehandle:
        lines = filehandle.readlines()

    with open(filename, 'w') as filehandle:
        lines = filter(lambda x: x.strip(), lines)
        filehandle.writelines(lines)


parser = argparse.ArgumentParser()
parser.add_argument("-s", "--site", help="Site name - ex. MVMS")
args = parser.parse_args()
site = args.site

if site is None:
    print('-s site name is a required argument')
    sys.exit()
else:
    dev_inv_file = 'device-inventory-' + site

# check if site's device inventory file exists
if not os.path.isfile(dev_inv_file):
    print("{} doesn't exist ".format(dev_inv_file))
    sys.exit()

remove_empty_lines(dev_inv_file)

with open(dev_inv_file) as devices_file:
    fabric = devices_file.readlines()

print('-' * (len(dev_inv_file) + 23))
print(f'Reading devices from: {dev_inv_file}')
print('-' * (len(dev_inv_file) + 23))

#  Create the interface-disable files
for line in fabric:
    line = line.strip("\n")
    ipaddr = line.split(",")[0]
    vendor = line.split(",")[1]
    hostname = line.split(",")[2]
    username = line.split(",")[3]
    password = line.split(",")[4]
    if vendor.lower() == "hp_procurve":
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        print((str(date_time) +
              " Creating disable file for {}".format(hostname)))
        print('Configuring {}'.format(hostname))
        cfg_file = '01_' + hostname + "-config-json.txt"
        print()
        with open(cfg_file, 'r') as json_file:
            interfaces = json.load(json_file)
        ports = []
        count = 0
        for interface in interfaces:
            if interface['total_bytes'] == '0':
                count += 1
                #    print(interface['port'])
                ports.append('interface ' + interface['port'] +
                             ' disable' + '\n')
        print(f'Number of ports to be diabled on {hostname}: {count}')
        disable = '01_' + hostname + '-interface-disable.txt'
        with open(disable, 'w') as file:
            for port in ports:
                file.write(port)

#  send diable commands
for line in fabric:
    line = line.strip("\n")
    ipaddr = line.split(",")[0]
    vendor = line.split(",")[1]
    hostname = line.split(",")[2]
    username = line.split(",")[3]
    password = line.split(",")[4]
    if vendor.lower() == "hp_procurve":
        print((str(datetime.now()) +
              " Creating disable file for {}".format(hostname)))
        try:
            net_connect = ConnectHandler(device_type=vendor,
                                        ip=ipaddr,
                                        username=username,
                                        password=password,
                                        )
        except (EOFError, SSHException):
            print(f'Could not connect to {hostname}, remove it'
                  ' from the device inventory file')
            break
        print(f'Configuring {hostname}')
        cfg_file = '01_' + hostname + "-interface-disable.txt"
        print(net_connect.find_prompt())
        output_text = net_connect.send_config_from_file(cfg_file)
        print(output_text)  # print the output to terminal as plain text
        #  Write log file of what pors were disabled.
        int_report = "01_" + hostname + "-disable-output.txt"
        with open(int_report, 'w') as file:
            file.write(output_text)
        print()
        net_connect.disconnect()
        print('-' * (len(hostname) + 26))
        print(f'Successfully configured {hostname}')
        print('-' * (len(hostname) + 26))
