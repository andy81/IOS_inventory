

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
scriptname = sys.argv[0:]
#print(ipinput)

#Display message about PATH variable requirements
print("This script requires PATH variables called PY_OUTPUTS (for file output) and NET_TEXTFSM for TEXTFSM template files).")
print("--------------------------------------------------------------------------------------------------------------------\n\n")

#Get username and password
username = input("Username? ")
password = getpass.getpass("Password? ")

#get node name and create text file name
nodename = input("Please enter node name, e.g WGH Node40: ")
py_output_dir = os.environ['PY_OUTPUTS'] + "\\inventory\\"
inventory_file = (py_output_dir + nodename + " - inventory.txt")
print("The inventroy file will stored here: " + inventory_file)

# Set template to use for parsing cli output
fsm_template_folder = os.environ["NET_TEXTFSM"]
inv_template = fsm_template_folder + "\\cisco_ios_show_inventory.template"
print("The following Textfsm template will be used:\n" + inv_template)


def runcmd(net_connect, ip):
    
    
    #Find hostname
    global hostname
    hostname = net_connect.find_prompt()
    print ('Connecting to device: ' + hostname)
    
    # Define cisco ios command
    inventory_cmd = ("show inventory")
    #Now to run the inventory command 
    global inventory_raw
    inventory_raw = net_connect.send_command(inventory_cmd)
  
    print(type(inventory_raw))
    print("inventory_raw output:\n" + inventory_raw)
    return inventory_raw, hostname

def format_cli(inv_template, inventory_raw):
    print("now inside format_cli")
    print("inv_template is:\n" + inv_template)
    print("inventory_raw is:\n" + inventory_raw)
    #inventory_template = open(fsm_template_folder + "cisco_ios_show_inventory.template")
    with open(inv_template, 'r') as f:
        template = textfsm.TextFSM(f)

    # Run the output through TextFSM
    inventory_data = template.ParseText(inventory_raw)
    print(type(inventory_data))
    print(inventory_data)
    
    writefile(inventory_file, inventory_data, template)
    

def writefile(inventory_file, inventory_data, template):
    print("\nNow to joining data values with headers...")
    #Column header from templte file
    header = ', '.join(template.header)
    #Each row of the table
    """Write ouput to csv formatted file"""
    with open(inventory_file, "a") as f:
        f.writelines(hostname + '\n')
        f.writelines(header + '\n')
        for row in inventory_data:
            data = ', '.join(row) + '\n'
            f.writelines(data)


netdevice = {}

for i in ipinput:
    
    try:
       
        inventory_raw = ''
        #we need to set the various options Netmiko is expecting. 
        #We use the variables we got from the user input earlier
        netdevice['ip'] = i
        netdevice['device_type'] = 'cisco_ios_ssh'
        netdevice['username'] = username   
        netdevice['password'] = password
        #netdevice['secret'] = enablepw
        #print(netdevice)
        #This command is when we are attempting to connect. If it fails, it will move on to the except block below
        net_connect = ConnectHandler(**netdevice)
        runcmd(net_connect, i)
        print("inventory_raw just after runcmd() is:\n" + inventory_raw)
        #Send output to textfsm for re formating
        format_cli(inv_template, inventory_raw)

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
            print ("Plese check your username and password")
            exit()
        #continue
else:
    print('All done. A file called ' + inventory_file + ' has been created.')
    #net_connect.enable()

