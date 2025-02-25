#------------------------------------------------------------------------------------
# Developed by Carpathian, LLC - Open Source Minecraft Server Manager.
# Free for personal use only – for business use, please email malkasian(a)dsm.studio
#------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------
"""
========================== MINECRAFT SERVER MONITOR (TEMPLATE) ==========================
This script automatically monitors a Minecraft server using the MCSRVSTAT API.
If the server is offline, it:
1) Gracefully shuts down any existing Minecraft servers (Java processes),
2) Closes Terminal windows (on macOS),
3) Restarts the servers by running .command files.

INSTRUCTIONS:
---------------------------------------------------------------------------
1) Install Python 3.x and the 'requests' library on macOS.
   - pip3 install --break-system-packages requests
2) Fill in your server IP or domain, the .command file paths, and any time delays
   you wish to configure.
3) Run the script or schedule it with cron to keep your server online.

HELP & TROUBLESHOOTING:
---------------------------------------------------------------------------
- On newer macOS versions, you may need to bypass "externally-managed" restrictions.
- If you have other Java apps, refine the "pgrep" command or filter differently.
- For questions, consult: https://api.mcsrvstat.us

============================================================================
"""

import os
import time
import subprocess
import requests
from datetime import datetime
import socket

# ---------------------- CONFIGURATION ----------------------
# 1) Your Minecraft server's IP or domain name
SERVER_IP = "<YOUR_SERVER_IP_OR_DOMAIN>"

# 2) The list of .command files to start each server instance
START_COMMANDS = [
    "/path/to/start.command-1",
    "/path/to/start.command-2",
    # Add more as needed... (copy the path of your start.command for each server)
]

# 3) General timing settings
CHECK_INTERVAL = 60            # How often (in seconds) to check server status
LOG_FILE = "/Users/server_monitor.log" 
# Make sure to update this if you want it saving a log to a specific location. I'm assuming this is running on MacOS

# 4) Graceful shutdown settings
MAX_SHUTDOWN_ATTEMPTS = 5      # Number of repeated SIGINT attempts
ATTEMPT_DELAY = 10             # Delay (in seconds) between each attempt
POST_SHUTDOWN_DELAY = 10       # After servers shut down, wait before closing windows

# 5) Post-restart boot delay
# Time (in seconds) to allow servers to fully start before next check
POST_RESTART_BOOT_DELAY = 60

# ---------------------- HELPER FUNCTIONS ----------------------
def log_event(message):
    """
    Logs a message with a timestamp to both console and a file for auditing.
    """
    with open(LOG_FILE, "a") as log:
        log.write(f"{datetime.now()} - {message}\n")
    print(message)

def is_server_online():
    """
    Uses the MCSRVSTAT API to check if the server is online.
    Change <SERVER_IP> to your domain or IP.
    """
    api_url = f"https://api.mcsrvstat.us/2/{SERVER_IP}"
    try:
        response = requests.get(api_url, timeout=10)
        data = response.json()
        return data.get("online", False)
    except requests.RequestException:
        return False

def is_internet_available():
    """
    Simple DNS check to confirm internet connectivity.
    """
    try:
        socket.gethostbyname("google.com")
        return True
    except socket.gaierror:
        return False

def get_minecraft_pids():
    """
    Finds all Java processes with '-Xmx' (typical for Minecraft).
    Adapt if you have multiple Java apps you DON'T want to kill.
    """
    output = subprocess.getoutput("pgrep -f 'java -Xmx'")
    return [pid.strip() for pid in output.splitlines() if pid.strip()]

def send_sigint_to_all_minecraft_servers():
    """
    Sends SIGINT (Ctrl+C) to *all* Java processes using killall -2.
    This presumes any Java processes are your Minecraft servers.
    """
    log_event("Sending SIGINT (Ctrl+C) to all Java processes (killall -2 java).")
    os.system("killall -2 java")

def attempt_graceful_shutdown(max_attempts=MAX_SHUTDOWN_ATTEMPTS, delay=ATTEMPT_DELAY):
    """
    Repeatedly tries to shut down all MC servers by sending SIGINT until no
    Java processes remain or we exceed max_attempts. Returns True if successful.
    """
    for attempt in range(1, max_attempts + 1):
        pids = get_minecraft_pids()
        if not pids:
            log_event("All Minecraft processes have shut down.")
            return True
        log_event(f"Attempt {attempt}/{max_attempts}: Processes still running: {pids}")
        send_sigint_to_all_minecraft_servers()
        time.sleep(delay)

    # Final check after attempts
    if not get_minecraft_pids():
        log_event("All servers shut down after repeated attempts.")
        return True
    else:
        log_event("Some servers are still running after max attempts.")
        return False

def disable_terminal_confirmation():
    """
    Disables macOS Terminal "Confirm Closing" so windows close automatically.
    """
    log_event("Disabling Terminal confirmation dialogs (defaults write).")
    os.system("defaults write com.apple.Terminal ConfirmClosing -bool false")

def close_minecraft_terminal_windows():
    """
    Closes Terminal windows with titles containing "java".
    """
    log_event("Closing Terminal windows that contain 'java' in their title.")
    os.system('osascript -e \'tell application "Terminal" to close (every window whose name contains "java")\'')

def restart_servers():
    """
    Launches each .command file in a new Terminal window.
    """
    log_event("Restarting Minecraft servers from .command files...")
    for command_file in START_COMMANDS:
        if os.path.exists(command_file):
            log_event(f"Starting server from: {command_file}")
            os.system(f'open "{command_file}"')
        else:
            log_event(f"Could not find .command file: {command_file}")
    log_event("Servers restarted.")

# ---------------------- MAIN MONITOR FUNCTION ----------------------
def monitor_server():
    """
    The main loop that:
    - Checks server status
    - If offline and internet is up, attempts graceful shutdown and restart
    - Waits a while after shutdown and then after restart
    - Repeats forever, waiting CHECK_INTERVAL seconds between checks
    """
    while True:
        if not is_server_online():
            # Server is offline
            if is_internet_available():
                log_event("Server is offline. Starting shutdown process...")
                success = attempt_graceful_shutdown()
                if success:
                    log_event(f"Waiting {POST_SHUTDOWN_DELAY} seconds post-shutdown...")
                    time.sleep(POST_SHUTDOWN_DELAY)
                    disable_terminal_confirmation()
                    close_minecraft_terminal_windows()
                    restart_servers()
                    log_event(f"Waiting {POST_RESTART_BOOT_DELAY} seconds for servers to finish booting...")
                    time.sleep(POST_RESTART_BOOT_DELAY)
                else:
                    log_event("Servers did not fully shut down. Will try again next cycle.")
            else:
                # Internet is offline, skip restart
                log_event("Internet is offline; not restarting servers.")
        else:
            # Server is online, do nothing
            log_event("Server is online. No action required.")

        # Wait before checking again
        time.sleep(CHECK_INTERVAL)

# ---------------------- SCRIPT EXECUTION ----------------------
if __name__ == "__main__":
    log_event("Starting Minecraft Server Monitor...")
    monitor_server()
