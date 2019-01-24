

#import netmiko to handle connection to each device.
import netmiko
from netmiko import ConnectHandler
#getpass
import getpass
#import datetime for time stamps
from datetime import datetime
#import sys for system variables
import sys
import os
import textfsm

#get ip(s) from user
ipinput = sys.argv[1:]
#print(ipinput)

#Get username and password
username = input("Username? ")
password = getpass.getpass("Password? ")

#get node name and create text file name
nodename = input("Please enter node name, e.g WGH Node40: ")
inventory_file = (nodename + " - inventory.txt")
fsm_template_folder = os.environ["NET_TEXTFSM"]
#inventory_template = open(fsm_template_folder + "cisco_ios_show_inventory.template")
with open(fsm_template_folder + "\\cisco_ios_show_inventory.template" , 'r') as f:
    inv_template = textfsm.TextFSM(f)

#print(fsm_template_folder)
#print(inv_template)


def runcmd(net_connect, ip):
    #timestamp = str(datetime.now())
    
    #Find hostname
    hostname = net_connect.find_prompt()
    print ('Connecting to device: ' + hostname)
    
    # Define cisco ios command
    inventory_cmd = ("show inventory")
    #Now to run the inventory command 
    inventory_raw = net_connect.send_command(inventory_cmd)
  
    print(type(inventory_raw))

def format_cli(inv_template, inventory_raw):
    # Parse the cli command output using textfsm template
    re_table_inventory = textfsm.TextFSM(inv_template)
    inventory_data = re_table_inventory.ParseText(inventory_raw)
    print (inventory_data)
    

netdevice = {}

for i in ipinput:
    
    try:
       
        inventory_raw = ''
        #we need to set the various options Netmiko is expecting. 
        #We use the variables we got from the user earlier
        netdevice['ip'] = i
        netdevice['device_type'] = 'cisco_ios_ssh'
        netdevice['username'] = username   
        netdevice['password'] = password
        #netdevice['secret'] = enablepw
        #print(netdevice)
        #This command is when we are attempting to connect. If it fails, it will move on to the except block below
        net_connect = ConnectHandler(**netdevice)
        runcmd(net_connect, i)
        #Send output to textfsm for re formating
        format_cli(inv_template,inventory_raw)

    except:
        #here we are saying "if ssh failed, TRY telnet"
        try:
           #same as before, but using the 'telnet' device type
            netdevice['device_type'] = 'cisco_ios_telnet'
            netdevice['username'] = username
            netdevice['password'] = password
            #netdevice['secret'] = enablepw
            net_connect = ConnectHandler(**netdevice)
            runcmd(net_connect, i)
            #Send output to textfsm for re formating
            format_cli(inv_template,inventory_raw)
        except:
            #this is the catch all except, if NOTHING works, tell the user and continue onto the next item in the for loop.
            print ("Unable to connect to " + netdevice['ip'])
            exit()
        #continue
else:
    print('All done. A file called ' + inventory_file + ' has been created.')
    #net_connect.enable()
            
