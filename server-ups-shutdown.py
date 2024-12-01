#------------------------------------------------------------------------------------
# Developed by Carpathian, LLC - Open Source server shutdown script for multiple MacMini's Running on
# a local network.
# Free for personal use only – for enterprise or business use, please email malkasian(a)dsm.studio
#---------------------------------------------------------------------------------------

__version__ = "1.0"

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

def get_battery_level():
    try:
        output = subprocess.check_output(['pmset', '-g', 'batt'])
        output = output.decode('utf-8')
        if 'AC Power' in output:
            return 'AC Power'
        match = re.search(r'(\d+)%', output)
        if match:
            return int(match.group(1))
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None

#UPDATE THE PATH IF YOU HAVE AN ALARM SOUND OTHERWISE COMMENT THIS FUNCTION OUT(!!!)
def play_alarm():
    while not lock.locked():
        os.system('afplay PATH_TO_ALARM_SOUND_EFFECT')
        time.sleep(10)

def show_popup(title, message):
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                formatted_message = f"{message} {timestamp}"
                messagebox.showinfo(title=title, message=formatted_message)

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

while True:
    level = get_battery_level()
    if level == 'AC Power':
        time.sleep(30)
        continue
    if level is not None:
        if level <= 10:
            with lock:
                print(f"Shutting down the supervisor. Battery at: {level}%")
                logging.info(f"Shutting down the supervisor. Battery at: {level}%")
                shutdown_host()
                break
        elif level <= 30:
            print(f"Battery critically low: {level}%. Shutting down other systems.")
            logging.info(f"Battery critically low: {level}%. Shutting down other systems.")
            shutdown_workstations()
        elif level <= 50:
            if not lock.locked():
                alarm_thread = threading.Thread(target=play_alarm)
                alarm_thread.start()
            print(f"WARNING: BATTERY GETTING LOW. Current Level: {level}%")
            logging.warning(f"WARNING: BATTERY GETTING LOW. Current Level: {level}%")
            time.sleep(10)
        elif level <= 98:
            show_popup("Power Outage Detected", "Power Outage Detected!")
            print(f"Power Outage Detected: Current Level: {level}%")
            logging.warning(f"Power Outage Detected. Current Level: {level}%")
        elif level >= 99:
            print(f"Current Level: {level}%")
            logging.info(f"Current Level: {level}%")
            time.sleep(60)
