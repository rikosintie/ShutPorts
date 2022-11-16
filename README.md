# ShutPorts

## Summary
A customer wants to shut down any port that isn't in use on their procurve swithes.

There are two scripts used for this:  
* procurve-Config-Push.py 
* interface.py.

### procurve-Config-Push.py  
Connects to each switch and runs "show interfaces" with textfsm=True. That creates a text file named 01_(hostname)-config-json.txt.
The contents are a JSON formatted structure.

The key part of the output is total_bytes. If it is 0, then the port has seen no traffic and should be disabled.

It also runs any commands in the file AUSD-config-file.txt. For the initial run these commands are:

show uptime  

show interfaces  

These are printed to the screen and saved to a file - 01_(hostname)-config-output.txt. The value of uptime is that you will know if the switch
has been reloaded recently.  


### interface.py  

This script reads the json files and creates a file called 01_(hostname)-disable-output.txt.

Then it logs into devices in the device-inventory-test file and pushes the commands in the disable-output file.

It prints out the number of ports disabled and the commands sent.  

### Devices
To configure a device, add it to the file device-inventory-. The format is:

IP Address,hp_procurve,hostname,username,password

Example
192.168.10.52,hp_procurve,ANTO-IDF1,mhubbard,7Snb7*BF^8

### Setting up the environment
These scripts require the netmiko libraries and the Google text FSM templates.

The instructions for setting up netmiko and textFSM can be found [here](https://pynet.twb-tech.com/blog/netmiko-and-textfsm.html)
