import requests
import re
from ui import run_ui, ui_print, get_client_credentials

# Configuration
JAMF_URL = "https://xxxxx.jamfcloud.com"
CLIENT_ID = "your_client_id_here"
CLIENT_SECRET = "your_client_secret_here"
DEST_PRESTAGE_ID = 9999  

# devices[0][i] = asset tag
# devices[1][i] = serial number
# devices[2][i] = JAMF ID
# devices[3][i] = current PreStage ID
devices = [[], [], [], []]

def get_access_token():
    url = f"{JAMF_URL}/api/oauth/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    response = requests.post(url, headers=headers, data=data)
    try:
        response.raise_for_status()
    except:
        ui_print("An error occurred getting access token. Check client credentials and try again.")
    return response.json()["access_token"]

def get_prestage_scope(token, prestage_id):
    url = f"{JAMF_URL}/api/v2/mobile-device-prestages/{prestage_id}/scope"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def remove_devices_from_prestage(token, devices):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    prestage_map = {}

    for i in range(len(devices[0])):
        prestage_id = devices[3][i]
        serial = devices[1][i]
        if prestage_id not in prestage_map:
            prestage_map[prestage_id] = []
        prestage_map[prestage_id].append(serial)

    for prestage_id, serials in prestage_map.items():
        scope = get_prestage_scope(token, prestage_id)
        version_lock = scope.get("versionLock", 1)
        url = f"{JAMF_URL}/api/v2/mobile-device-prestages/{prestage_id}/scope/delete-multiple"
        payload = {
            "serialNumbers": serials,
            "versionLock": version_lock
        }
        response = requests.delete(url, headers=headers, json=payload)
        response.raise_for_status()
        ui_print(f"Removed {len(serials)} devices from PreStage ID {prestage_id}.")

def add_devices_to_prestage(token, devices, dest_prestage_id):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    scope = get_prestage_scope(token, dest_prestage_id)
    version_lock = scope.get("versionLock", 1)
    serials = devices[1]

    url = f"{JAMF_URL}/api/v2/mobile-device-prestages/{dest_prestage_id}/scope"
    payload = {
        "serialNumbers": serials,
        "versionLock": version_lock
    }
    response = requests.put(url, headers=headers, json=payload)
    response.raise_for_status()
    ui_print(f"Added {len(serials)} devices to PreStage ID {dest_prestage_id}.")

def fetch_device_data(token, asset_tag):
    url = f"{JAMF_URL}/JSSResource/mobiledevices/match/{asset_tag}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
    except:
        ui_print("An error occurred fetching device data. Check client credentials.")
    data = response.json()
    serial = data.get("serial_number")
    jamf_id = data.get("id")
    current_prestage_id = fetch_device_prestage(token, data.get("device_name"))
    return serial, jamf_id, current_prestage_id

def fetch_device_prestage(token, name):
    prestage_id = 0
    nameparts = name.split('-')
    prestage_name = "NISD-"
    for part in nameparts:  
        prestage_name += str(part)
    prestage_name += "-PEP"

    url = "https://nisdmobile.jamfcloud.com/api/v2/mobile-device-prestages?sort=name%3Aasc"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    for item in data.get("results", []):
        if item.get("displayName") == prestage_id:
            return item.get("id")
    
    return prestage_id

def resolve_prestage_name(token, name_hint):
    url = f"{JAMF_URL}/api/v2/mobile-device-prestages"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    prestages = response.json()["results"]

    name_hint = name_hint.lower().strip()
    hint_parts = re.split(r"[-\s_]+", name_hint)

    matches = []
    for ps in prestages:
        name = ps["displayName"].lower()
        score = sum(1 for part in hint_parts if part in name)
        if score > 0:
            matches.append((score, ps["id"], ps["displayName"]))

    if not matches:
        raise ValueError(f"No PreStages found matching '{name_hint}'.")

    matches.sort(reverse=True)
    top_score = matches[0][0]
    top_matches = [m for m in matches if m[0] == top_score]

    if len(top_matches) > 1:
        ui_print("\n⚠️ Multiple PreStages matched your input:")
        for idx, (_, pid, display_name) in enumerate(top_matches):
            ui_print(f"  [{idx + 1}] ID {pid}: {display_name}")
        while True:
            choice = input(f"\nSelect a PreStage by number (1-{len(top_matches)}): ")
            if choice.isdigit():
                choice = int(choice)
                if 1 <= choice <= len(top_matches):
                    selected = top_matches[choice - 1]
                    ui_print(f"\n✅ Using PreStage: ID {selected[1]} -> {selected[2]}")
                    return selected[1]
            ui_print("Invalid selection. Please try again.")
    else:
        ui_print(f"✅ Matched PreStage: ID {matches[0][1]} -> {matches[0][2]}")
        return matches[0][1]

def main():
    global CLIENT_ID, CLIENT_SECRET

    # Ask user for API credentials via UI
    CLIENT_ID, CLIENT_SECRET = get_client_credentials()

    token = get_access_token()

    devices[0], prestage_input = run_ui(token)
    devices[1] = [None] * len(devices[0])
    devices[2] = [None] * len(devices[0])
    devices[3] = [None] * len(devices[0])

    try:
        DEST_PRESTAGE_ID = int(prestage_input)
    except ValueError:
        DEST_PRESTAGE_ID = resolve_prestage_name(token, prestage_input)

    for i in range(len(devices[0])):
        serial, jamf_id, prestage_id = fetch_device_data(token, devices[0][i])
        devices[1][i] = serial
        devices[2][i] = jamf_id
        devices[3][i] = prestage_id

    remove_devices_from_prestage(token, devices)
    add_devices_to_prestage(token, devices, DEST_PRESTAGE_ID)

if __name__ == "__main__":
    main()
