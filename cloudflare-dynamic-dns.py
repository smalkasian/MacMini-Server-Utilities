#------------------------------------------------------------------------------------
# Developed by MalkasianGroup, LLC - Open Source DNS updater for Cloudflare Inc.
# Free for personal use only – for enterprise or business use, please email malkasian(a)dsm.studio
#------------------------------------------------------------------------------------

__version__ = "1.0"

#--------------------------------------IMPORTS------------------------------------------
from requests.exceptions import RequestException
import requests
import time
from datetime import datetime


#--------------------------------------VARIABLES------------------------------------------

api_token = 'YOUR_API_TOKEN'
zone_id = 'YOUR_ZONE_ID'
record_id = 'YOUR_RECORD_ID'
record_name = 'example.com'
record_type = 'A'
CHECK_INTERVAL = 300

def get_public_ip():
    try:
        return requests.get('https://api.ipify.org').text
    except Exception as e:
        print(f"Error getting public IP: {e}")
        return None

def update_dns_record(new_ip):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}'

    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
    }

    data = {
        'type': record_type,
        'name': record_name,
        'content': new_ip,
        'ttl': 120,
        'proxied': True #Change this if you DON'T want the data to be proxied (will break any port forwarding)
    }

    response = requests.put(url, headers=headers, json=data)

    if response.status_code == 200:
        print(f"DNS record set to {new_ip}")
    else:
        print(f"Failed to update DNS record: {response.status_code} - {response.text}")

def main_loop():
    while True:
        try:
            current_ip = get_public_ip()
            if not current_ip:
                print("Could not determine current public IP. Exiting.")
                return
            print(f"Current public IP: {current_ip}")
            update_dns_record(current_ip)
        except requests.exceptions.ConnectionError as e:
            print(f"ConnectionError occurred: {e}. Retrying in {CHECK_INTERVAL} seconds...")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            time.sleep(CHECK_INTERVAL)
        
#------------------------------------MAIN PROGRAM-----------------------------------------

if __name__ == "__main__":
    main_loop()
