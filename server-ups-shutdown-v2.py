 #------------------------------------------------------------------------------------
# Developed by MalkasianGroup, LLC - Open Source server shutdown script for multiple MacMini's Running on
# a local network.
# Free for personal use only – for enterprise or business use, please email malkasian(a)dsm.studio
#---------------------------------------------------------------------------------------
# NOTES: I need to test and make sure the hypervisor is authorized to run sudo commands
# for the shutdown and it sees the other devices on the network.




__version__ = "2.0"

#--------------------------------------IMPORTS------------------------------------------
import os
import time
import subprocess
import re
import logging
import threading
import datetime
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

#--------------------------------------FUNCTIONS-----------------------------------------

lock = threading.Lock()

# Configure logging #UPDATE THE PATH(!!!)
logging.basicConfig(filename='PATH_WHERE_YOU_WANT_TO_SAVE_THE_LOGS', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

def get_battery_levels():
    try:
        output = subprocess.check_output(['pmset', '-g', 'batt'])
        output = output.decode('utf-8')
        
        macbook_battery = None
        ups_battery = None
        
        if 'InternalBattery' in output:
            macbook_match = re.search(r'InternalBattery-\d+\s+\(id=\d+\)\s+(\d+)%', output)
            if macbook_match:
                macbook_battery = int(macbook_match.group(1))
            else:
                print("MacBook battery level not found in the output.")
        
        if 'Back-UPS' in output:
            ups_match = re.search(r'Back-UPS.*\s+(\d+)%', output)
            if ups_match:
                ups_battery = int(ups_match.group(1))
                print(f"UPS battery level found: {ups_battery}%")
            else:
                print("UPS battery level not found in the output.")
        
        return macbook_battery, ups_battery

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")
        return None, None

#UPDATE THE PATH IF YOU HAVE AN ALARM SOUND OTHERWISE COMMENT THIS FUNCTION OUT(!!!)
def play_alarm():
    while not lock.locked():
        os.system('afplay PATH_TO_ALARM_SOUND_EFFECT')
        time.sleep(10)

def shutdown_workstations():
    other_computers = {
        'YOUR_COMPUTER_NAME': 'IP_ADDRESS',
        'YOUR_COMPUTER_NAME': 'IP_ADDRESS',
        'YOUR_COMPUTER_NAME': 'IP_ADDRESS',
        'YOUR_COMPUTER_NAME': 'IP_ADDRESS',
    }
    for username, ip in other_computers.items():
        try:
            subprocess.run(f'ssh {username}@{ip} sudo shutdown -h now', timeout=5, shell=True)
            logging.info(f"Shutdown command sent to {username}@{ip}")
        except (subprocess.TimeoutExpired, Exception):
            logging.error(f"Could not shut down {username}@{ip} within the timeout period.")
            continue

def shutdown_host():
    os.system('sudo shutdown -h now')
    logging.info("Shutting down the host")

def disconnect_egpu():
    try:
        # Identify eGPU
        egpu_info = subprocess.check_output(['system_profiler', 'SPDisplaysDataType']).decode('utf-8')
        if 'eGPU' in egpu_info:
            print("eGPU detected, attempting to disconnect...")
            logging.info("eGPU detected, attempting to disconnect...")
            # Attempt to eject the eGPU using SafeEjectGPU tool
            subprocess.run(['/usr/bin/SafeEjectGPU', 'gpuid', '0xad9c', 'Initiate'], check=True)
            subprocess.run(['/usr/bin/SafeEjectGPU', 'gpuid', '0xad9c', 'Finalize'], check=True)
            print("Successfully disconnected eGPU.")
            logging.info("Successfully disconnected eGPU.")
        else:
            print("No eGPU detected.")
            logging.info("No eGPU detected.")
    except Exception as e:
        logging.error(f"An error occurred while attempting to disconnect eGPU: {e}")
        print(f"An error occurred while attempting to disconnect eGPU: {e}")

def unmount_nas(volume_name):
    try:
        subprocess.run(['diskutil', 'unmount', f'/Volumes/{volume_name}'], check=True)
        logging.info(f"Successfully unmounted /Volumes/{volume_name}")
        print(f"Successfully unmounted /Volumes/{volume_name}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to unmount /Volumes/{volume_name}: {e}")
        print(f"Failed to unmount /Volumes/{volume_name}: {e}")

nas_unmounted = False
egpu_disconnected = False

def main_function():
    while True:
        macbook_battery, ups_battery = get_battery_levels()
        if macbook_battery is None or ups_battery is None:
            time.sleep(30)
            continue
        
        if macbook_battery == 'AC Power':
            time.sleep(30)
            continue

        if macbook_battery is not None:
            if macbook_battery <= 10:
                with lock:
                    print(f"Shutting down the supervisor. MacBook battery at: {macbook_battery}%")
                    logging.info(f"Shutting down the supervisor. MacBook battery at: {macbook_battery}%")
                    shutdown_host()
                    break
            elif macbook_battery <= 80:
                print("MacBook battery at: {macbook_battery}%")
            elif macbook_battery > 80:
                print("MacBook battery at: {macbook_battery}%")
                time.sleep(60)
        if ups_battery is not None:
            if ups_battery <= 30:
                print(f"UPS battery critically low: {ups_battery}%. Shutting down other systems.")
                logging.info(f"UPS battery critically low: {ups_battery}%. Shutting down other systems.")
                shutdown_workstations()
            elif ups_battery <= 50:
                if not nas_unmounted:
                    unmount_nas('NAS')  # Replace 'NAS' with your actual NAS volume name
                    nas_unmounted = True
                if not egpu_disconnected:
                    disconnect_egpu()
                    egpu_disconnected = True
                if not lock.locked():
                    alarm_thread = threading.Thread(target=play_alarm)
                    alarm_thread.start()
                print(f"WARNING: UPS battery getting low. Current Level: {ups_battery}%")
                logging.warning(f"WARNING: UPS battery getting low. Current Level: {ups_battery}%")
                time.sleep(10)
            elif ups_battery <= 98:
                print(f"Power Outage Detected: UPS Battery Level: {ups_battery}%")
                logging.warning(f"Power Outage Detected. UPS Battery Level: {ups_battery}%")
            elif ups_battery >= 99:
                print(f"UPS Battery Level: {ups_battery}%")
                logging.info(f"UPS Battery Level: {ups_battery}%")
                time.sleep(60)


#--------------------------------------TEST-----------------------------------------


# Call the function for debugging purposes
macbook_battery, ups_battery = get_battery_levels()
print(f"MacBook Battery: {macbook_battery}%")
print(f"UPS Battery: {ups_battery}%")
