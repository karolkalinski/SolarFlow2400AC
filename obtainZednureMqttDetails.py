# python version of https://github.com/nograx/ioBroker.zendure-solarflow/blob/main/src/services/zenWebService.ts
import base64
import json
import sys
import time
import random
import hashlib
import requests

CLIENT_ID = "zenHa"
CLIENT_SECRET = "C*dafwArEOXK"

def create_signature(body: dict, timestamp: int, nonce: int) -> str:
    sign_params = {**body, "timestamp": timestamp, "nonce": nonce}
    body_str = "".join(f"{k}{sign_params[k]}" for k in sorted(sign_params.keys()))
    sign_str = f"{CLIENT_SECRET}{body_str}{CLIENT_SECRET}"
    sha1_hash = hashlib.sha1(sign_str.encode("utf-8")).hexdigest().upper()

    return sha1_hash

if len(sys.argv) < 2:
    print("Error: No auth cloud key provided.\nUsage: python script.py <argument>")
    sys.exit(1)

auth_cloud_key = sys.argv[1]

# Decode the Base64 string
decoded_bytes = base64.b64decode(auth_cloud_key)

# Convert bytes to string (UTF-8)
decoded = decoded_bytes.decode('utf-8')

parts = decoded.rsplit('.', 1)   # the "1" ensures only first dot splits

if len(parts) == 2:
    api_url, app_key = parts
    data = {"appKey": app_key}
else:
    print("Decoded string does not contain two parts separated by a dot.")
    sys.exit(1)

# --- Main request function ---
def get_device_list(api_url: str, body: dict = None):
    if body is None:
        body = {}

    timestamp = int(time.time())
    nonce = random.randint(10000, 99999)
    sign = create_signature(body, timestamp, nonce)
    headers = {
        "Content-Type": "application/json",
        "timestamp": str(timestamp),
        "nonce": str(nonce),
        "clientid": CLIENT_ID,
        "sign": sign,
    }

    device_list_url = f"{api_url}/api/ha/deviceList"

    response = requests.post(
        device_list_url,
        data=json.dumps(body),
        headers=headers,
        timeout=10,
    )

    response.raise_for_status()  # Raise error if HTTP request failed
    data = response.json()
    return data.get("data").get('mqtt')

print(json.dumps(get_device_list(api_url, data), indent=4, sort_keys=True))
