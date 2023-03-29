# This Code created by TAQI Al-shamiri as a PRTG Advanced script sensor for VCG.
# Code written 15/02/2023 - This code is owned, controlled by VCG. Do not amend / copy without prior written authorisation. 

#libraries to import 
import json
import sys
from netmiko import Netmiko
from datetime import datetime, date
import os
import time

from paesslerag_prtg_sensor_api.sensor.result import CustomSensorResult
from paesslerag_prtg_sensor_api.sensor.units import ValueUnit,ValueTime,ValueSize, ValueMode


#Global variables
t = f'{date.today()}-{datetime.now().strftime("%H_%M_%S")}' # date of today
now = time.time()


def fileCounter(filelist,file):
    x = 0
    for b in filelist:
        if file in b:
            x +=1

    return x;

def fileSize(filelist,file,directory): #[i] is the list of files, [n] is the file name, [z] is the directory. 

    x = 0 #local variable to be returned

    for i in filelist:
        if file in i:
            #Remove file if its older than 30 days 
            if os.stat(directory+i).st_mtime < now - 30 * 86400:
                os.remove(directory+i)
            #If the file still in path, retrive the file size in bytes and store it to variable x
                if os.path.isfile(i):
                    bsize = os.stat(directory+i).st_size
                    bsize +=x


    return x * 0.000001; # Convert Bytes into MegaBytes, and return the value.
        
    


# main code to run 
if __name__ == "__main__":

    try:
        data = json.loads(sys.argv[1])

# SSH Connection device type and credentials as imported from device PRTG
# You would need to configure Netmiko device type in PRTG script credientals placeholder.
# SSH credientals are polled as PRTG linux SSH username / password details.  
        device = {
        #    "session_log":f'C:/netmiko.log',
            "device_type":data["scriptplaceholder1"],
            "host":data["host"],
            "username":data["linuxloginusername"],
            "password":data["linuxloginpassword"],

            }
        #SSH Connection 
        net_conn = Netmiko(**device)
        #save the running config
        if device['device_type'] == 'cisco_ios':
            net_conn.send_command ('terminal length 0', read_timeout=10)
        elif device['device_type'] == 'cisco_wlc':
            net_conn.send_command ('configure pager disable', read_timeout=10)
        elif device['device_type'] == 'cisco_asa':
            net_conn.send_command ('terminal pager 0', read_timeout=10)
            
        config = net_conn.send_command ('show run', read_timeout=60)
        #check if backup path exists, if not create it. 
        if os.path.exists(f'C:/PRTG backups/{data["scriptplaceholder2"]}') == False:
            os.makedirs(f'C:/PRTG backups/{data["scriptplaceholder2"]}')

        prompt = net_conn.find_prompt() # Get the prompt
        if '>' in prompt: # if the prompt has > or # the if and elif statements will strip it. 
            hostname = prompt.strip('>')
        elif '#' in prompt:
            hostname = prompt.strip('#')

        # directory / file naming structure     
        directory = f'C:/PRTG backups/{data["scriptplaceholder2"]}/'
        backup = f'{hostname}-{data["host"]}'
        tstamp = f'-{t}.txt'

        # PRTG Sensor description 
        csr = CustomSensorResult(text= f"This sensor runs on {hostname} - {data['host']} - backup location 'C:/PRTG backups/" )

        #write the running configuration result to a file.  
        with open(directory + backup + tstamp ,'w') as f:
            f.write(config)

        #count how many backups we have for this device in the folder directory. 
        backupCount = os.listdir(f'C:/PRTG backups/{data["scriptplaceholder2"]}')

        #FileSize
        
        
        # Sensor channels #
        #Channel backup files counts within the file for this device. 
        csr.add_primary_channel(name="How many backups",
                        value = fileCounter(backupCount, backup),
                        unit = ValueUnit.COUNT,
                        is_float = False
                       )

        csr.add_channel(name="Storage consumed",
                        value = fileSize(backupCount, backup, directory),
                        unit = ValueSize.MEGABYTE,
                       )
        '''
        csr.add_channel(name="File Name",
                        value = f'{hostname}-{data["host"]}-{t}.txt',
                        unit = ValueUnit.CUSTOM,
                        is_float = False,
                        is_limit_mode=False
                       )
        '''
      
        print(csr.json_result)
            
    except Exception as e:
        csr = CustomSensorResult(text="Python Script execution error")
        csr.error = f"Python Script execution error: f{str(e)}" 
        print(csr.json_result)


'''
csr.add_primary_channel(name="Last Backup run Date",
                                value=40,
                                unit=ValueUnit.BYTESFILE,
                                is_float=False,
                                is_limit_mode=True,
                                limit_min_error=10,
                                limit_max_error=90,
                                limit_error_msg="Percentage too high")
                                
'''
