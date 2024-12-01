#------------------------------------------------------------------------------------
# Developed by MalkasianGroup, LLC - Open Source DNS updater for DynaDot® hosted domains.
# Free for personal use only – for enterprise or business use, please email malkasian(a)dsm.studio
#------------------------------------------------------------------------------------
# Legal stuff:
# DynaDot® is a registered trademark of DynaDot, LLC. All rights reserved.
#---------------------------------------------------------------------------------------
import requests
import time
from datetime import datetime

# ------------------- VARIABLES -------------------
API_KEY = 'REPLACE_WITH_YOUR_DYNADOT_API_KEY'  # Replace with your Dynadot API key
DOMAINS = ['yourdomain1.com', 'yourdomain2.com']  # List of domains to update
RECORD_TYPE = 'A'
RECORD_NAME = '@'  # '@' for root domain
CHECK_INTERVAL = 300  # Interval to check in seconds

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# ------------------- FUNCTIONS -------------------

def get_current_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_public_ip():
    services = ["https://api.ipify.org", "https://icanhazip.com", "https://ifconfig.me/ip"]
    for service in services:
        try:
            response = requests.get(service, timeout=5)
            if response.status_code == 200:
                return response.text.strip()
        except requests.RequestException as e:
            print(f"Error fetching public IP address from {service}: {e}")
    return None

def get_current_dns_ip(domain):
    url = f"https://api.dynadot.com/api3.json"
    params = {
        "command": "get_domain_dns",
        "domain": domain,
        "key": API_KEY
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            dns_data = response.json()
            return dns_data.get("dns_records", {}).get(RECORD_TYPE, {}).get(RECORD_NAME)
    except requests.RequestException as e:
        print(f"Error fetching DNS IP for {domain}: {e}")
    return None

def update_dns(domain, new_ip_address):
    url = f"https://api.dynadot.com/api3.json"
    params = {
        "command": "set_domain_dns",
        "domain": domain,
        "record_type": RECORD_TYPE,
        "record_host": RECORD_NAME,
        "record_value": new_ip_address,
        "ttl": 600,
        "key": API_KEY
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            print(f"DNS record for {domain} updated successfully to {new_ip_address}.")
        else:
            print(f"Failed to update DNS for {domain}. Status: {response.status_code}, Response: {response.text}")
    except requests.RequestException as e:
        print(f"Error updating DNS for {domain}: {e}")

def check_and_update_domains(domains):
    new_ip_address = get_public_ip()
    if not new_ip_address:
        print(f"{get_current_time()}: Failed to retrieve public IP address.")
        return
    for domain in domains:
        current_dns_ip = get_current_dns_ip(domain)
        if new_ip_address != current_dns_ip:
            print(f"{get_current_time()}: IP changed to {new_ip_address} for {domain}. Updating DNS...")
            update_dns(domain, new_ip_address)
        else:
            print(f"{get_current_time()}: IP not changed for {domain}. No update needed.")

# ------------------- MAIN PROGRAM -------------------

if __name__ == "__main__":
    while True:
        try:
            check_and_update_domains(DOMAINS)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        time.sleep(CHECK_INTERVAL)
