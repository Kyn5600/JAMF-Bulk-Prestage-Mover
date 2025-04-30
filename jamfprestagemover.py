import requests
from collections import defaultdict

# Configuration
JAMF_URL = "https://xxxxx.jamfcloud.com"
CLIENT_ID = "your_client_id_here"
CLIENT_SECRET = "your_client_secret_here"
DEST_PRESTAGE_ID = 9999  

# List of serial numbers to move
serial_numbers = [
    "C02XXXXXX1",
    "C02XXXXXX2",
    "C02XXXXXX3",
]

def get_access_token():
    url = f"{JAMF_URL}/api/oauth/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def get_prestage_scopes(token):
    url = f"{JAMF_URL}/api/v2/mobile-device-prestages"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["results"]

def get_prestage_scope(token, prestage_id):
    url = f"{JAMF_URL}/api/v2/mobile-device-prestages/{prestage_id}/scope"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def remove_devices_from_prestage(token, prestage_id, serials, version_lock):
    url = f"{JAMF_URL}/api/v2/mobile-device-prestages/{prestage_id}/scope"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "serialNumbers": serials,
        "versionLock": version_lock
    }
    response = requests.delete(url, headers=headers, json=payload)
    response.raise_for_status()
    print(f"Removed {len(serials)} devices from PreStage ID {prestage_id}.")

def add_devices_to_prestage(token, prestage_id, serials, version_lock):
    url = f"{JAMF_URL}/api/v2/mobile-device-prestages/{prestage_id}/scope"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "serialNumbers": serials,
        "versionLock": version_lock
    }
    response = requests.put(url, headers=headers, json=payload)
    response.raise_for_status()
    print(f"Added {len(serials)} devices to PreStage ID {prestage_id}.")

def main():
    token = get_access_token()
    prestages = get_prestage_scopes(token)

    # Map serial numbers to their current PreStage IDs
    serial_to_prestage = {}
    for prestage in prestages:
        prestage_id = prestage["id"]
        scope = get_prestage_scope(token, prestage_id)
        for device in scope.get("assignments", []):
            serial = device.get("serialNumber")
            if serial in serial_numbers:
                serial_to_prestage[serial] = {
                    "prestage_id": prestage_id,
                    "version_lock": scope.get("versionLock")
                }

    # Group serial numbers by their current PreStage
    prestage_groups = defaultdict(list)
    for serial, info in serial_to_prestage.items():
        prestage_groups[(info["prestage_id"], info["version_lock"])].append(serial)

    # Remove devices from their current PreStages
    for (prestage_id, version_lock), serials in prestage_groups.items():
        remove_devices_from_prestage(token, prestage_id, serials, version_lock)

    # Add all devices to the destination PreStage
    dest_scope = get_prestage_scope(token, DEST_PRESTAGE_ID)
    dest_version_lock = dest_scope.get("versionLock")
    add_devices_to_prestage(token, DEST_PRESTAGE_ID, serial_numbers, dest_version_lock)

if __name__ == "__main__":
    main()
