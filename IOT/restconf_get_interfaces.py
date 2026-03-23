import requests
import json
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

ROUTER_IP = "10.0.137.231"
USERNAME = "admin"
PASSWORD = "Admin123!"

url = f"http://{ROUTER_IP}/restconf/data/ietf-interfaces:interfaces"
headers = {
    "Accept": "application/yang-data+json"
}

response = requests.get(
    url,
    headers=headers,
    auth=HTTPBasicAuth(USERNAME, PASSWORD),
    verify=False,
    timeout=20
)

print("STATUS:", response.status_code)
print(json.dumps(response.json(), indent=2))
