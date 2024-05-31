import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_rms_rig_info(rig_id):
    url = f"https://rms.volvocars.net/api/rig/{rig_id}"
    try:
        response = requests.get(url, verify=False)  # Bypass SSL verification
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to retrieve rig information. Status code: {response.status_code}")
            print("Response content:", response.text)
            return None
    except requests.exceptions.SSLError as e:
        print(f"SSL Error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_rig_info_string(rig_id):
    rig_info = get_rms_rig_info(rig_id)
    if rig_info:
        info_str = (
            f"Pool: {rig_info.get('pool')}\n"
            f"Hostname: {rig_info.get('hostname')}\n"
            f"State: {rig_info.get('state')}\n"
            f"CI: {', '.join(rig_info.get('ci', []))}\n"
            f"Lifecycle Type: {rig_info.get('lifecycleType')}\n"
            f"Lab: {rig_info.get('lab')}"
        )
        return info_str
    else:
        return "Failed to retrieve rig information"
