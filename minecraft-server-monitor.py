import requests
import os
import time
import subprocess
from datetime import datetime

# Configurations
SERVER_IP = "midwestblocks.com"
API_URL = f"https://api.mcsrvstat.us/2/{SERVER_IP}"
CHECK_INTERVAL = 60  # Check every 60 seconds
LOG_FILE = "/path/to/server_monitor.log"  # Update with actual path
START_COMMANDS = [
    "tmux new-session -d -s mc_server_1 '/usr/bin/java -Xms10G -Xmx10G -jar paper-1.21.4-53.jar nogui'",
    "tmux new-session -d -s mc_server_2 '/usr/bin/java -Xms2G -Xmx2G -jar paper-1.21.4-118.jar nogui'",
    "tmux new-session -d -s mc_server_3 '/usr/bin/java -Xmx1G -jar paper-1.21.4-53.jar nogui'",
    "tmux new-session -d -s mc_bungee '/usr/bin/java -Xms2G -Xmx2G -jar BungeeCord.jar'",
]

def log_event(message):
    """Logs events with timestamps."""
    with open(LOG_FILE, "a") as log:
        log.write(f"{datetime.now()} - {message}\n")
    print(message)

def is_server_online():
    """Checks if the Minecraft server is online via API."""
    try:
        response = requests.get(API_URL, timeout=10)
        data = response.json()
        return data.get("online", False)
    except requests.RequestException:
        return False

def close_existing_servers():
    """Kills all running Minecraft Java processes."""
    log_event("Stopping all Minecraft servers...")
    os.system("pkill -f 'java -Xmx'")  # Kills only Java processes related to Minecraft
    time.sleep(5)  # Give time to shut down

def restart_servers():
    """Starts the Minecraft servers using tmux sessions."""
    log_event("Restarting Minecraft servers...")
    for cmd in START_COMMANDS:
        subprocess.run(cmd, shell=True)
    log_event("Servers restarted.")

def monitor_server():
    """Continuously monitors the server and restarts if offline."""
    while True:
        if not is_server_online():
            log_event("Server is offline. Restarting...")
            close_existing_servers()
            restart_servers()
        else:
            log_event("Server is online.")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    log_event("Starting server monitor...")
    monitor_server()
