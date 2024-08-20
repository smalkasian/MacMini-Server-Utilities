
import requests

api_token = 'a6Nua-bJfs2LIhzyk2nUaWMVWEg7O2fNG5LSGwPC'
zone_id = 'a6c4d861daa5627db4c34315d8f29d23'
record_name = 'midwestblocks.com'  # Replace with your DNS record name

def get_dns_records(zone_id):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get DNS records: {response.status_code} - {response.text}")
        return None

if __name__ == '__main__':
    dns_records = get_dns_records(zone_id)
    if dns_records:
        print("DNS Records:", dns_records)
        for record in dns_records.get('result', []):
            if record['name'] == record_name:
                print(f"Record ID for {record_name}: {record['id']}")
                break
        else:
            print(f"No DNS record found for {record_name}.")
