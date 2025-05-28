import hashlib
import time
import random
import string
import requests
import json
import sys

# Relevant ids and secrets:
# The App ID is sent in each HTTP request header from the Mspa app.
app_id = ""
# The App Secret can be determined by decompiling the Mspa app.
app_secret = ""
# Account E-Mail
account_email = ""
# MD5 hash of the actual password
password = ""
# The Device ID and Product ID is sent in each HTTP request header from the Mspa app.
device_id = ""
product_id = ""

def generate_nonce(length=32):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def current_ts():
    return str(int(time.time()))

def build_signature(app_id, nonce, ts, app_secret):
    raw = app_id + "," + app_secret + "," + nonce + "," + ts
    return hashlib.md5(raw.encode("utf-8")).hexdigest().upper()

def get_former_token():
    try:
        with open("token.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return ""

def write_token(token):
    with open("token.txt", "w") as file:
        file.write(token)

def authenticate():
    nonce = generate_nonce()
    ts = current_ts()
    sign = build_signature(app_id, nonce, ts, app_secret)
    headers = {
        "push_type": "Android",
        "authorization": "token",
        "appid": app_id,
        "nonce": nonce,
        "ts": ts,
        "lan_code": "de",
        "sign": sign,
        "content-type": "application/json; charset=UTF-8",
        "accept-encoding": "gzip",
        "user-agent": "okhttp/4.9.0"
    }
    payload = {
        "account": account_email,
        "app_id": app_id,
        "password": password,
        "brand": "",
        "registration_id": "",
        "push_type": "android",
        "lan_code": "EN",
        "country": ""
    }
    token_request_url = "https://api.iot.the-mspa.com/api/enduser/get_token/"
    response = requests.post(token_request_url, headers=headers, json=payload).json()
    token = response.get("data", {}).get("token")
    if token != None:
        write_token(token)
        return token
    else:
        get_former_token()

def send_device_command(desired_dict, retry=False, bubble_level=-1):
    token = get_former_token()
    nonce = generate_nonce()
    ts = current_ts()
    sign = build_signature(app_id, nonce, ts, app_secret)
    headers = {
        "push_type": "Android",
        "authorization": "token " + token,
        "appid": app_id,
        "nonce": nonce,
        "ts": ts,
        "lan_code": "de",
        "sign": sign,
        "content-type": "application/json; charset=UTF-8",
        "accept-encoding": "gzip",
        "user-agent": "okhttp/4.9.0"
    }
    if bubble_level < 0:
        payload = {
            "device_id": device_id,
            "product_id": product_id,
            "desired": json.dumps({"state": {"desired": desired_dict}})
        }
    else:
        payload = {
            "device_id": device_id,
            "product_id": product_id,
            "desired": json.dumps({"state": {"desired": desired_dict, "bubble_level": bubble_level}})
        }
    url = "https://api.iot.the-mspa.com/api/device/command"
    response = requests.post(url, headers=headers, json=payload).json()
    if (response.get('message') != 'SUCCESS') and (retry == False):
        token = authenticate()
        if bubble_level < 0:
            return send_device_command(desired_dict, True)
        else:
            return send_device_command(desired_dict, True, bubble_level)

    if (desired_dict.get("heater_state")) == 0:
        set_filter_state(0)
    return response

def set_heater_state(state: int): return send_device_command({"heater_state": state})
def set_temperature_setting(temp: int): return send_device_command({"temperature_setting": temp})
def set_bubble_state(state: int, level: int): return send_device_command({"bubble_state": state, "bubble_level": level})
def set_bubble_level(level: int): return send_device_command({"bubble_level": level})
def set_jet_state(state: int): return send_device_command({"jet_state": state})
def set_filter_state(state: int): return send_device_command({"filter_state": state})

def getHotTubStatus(retry=False):
    nonce = generate_nonce()
    ts = current_ts()
    sign = build_signature(app_id, nonce, ts, app_secret)
    headers = {
        "push_type": "Android",
        "authorization": "token " + get_former_token(),
        "appid": app_id,
        "nonce": nonce,
        "ts": ts,
        "lan_code": "de",
        "sign": sign,
        "content-type": "application/json; charset=UTF-8",
        "accept-encoding": "gzip",
        "user-agent": "okhttp/4.9.0"
    }
    payload = {
        "device_id": device_id,
        "product_id": product_id
    }
    url = "https://api.iot.the-mspa.com/api/device/thing_shadow/"
    response = requests.post(url, headers=headers, json=payload).json()
    if not response.get("data") and not retry:
        token = authenticate()
        write_token(token)
        return getHotTubStatus(True)
    data = response["data"]
    return data

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("No command provided.")
        sys.exit(1)

    cmd = args[0]

    if cmd == "authenticate":
        print(authenticate())

    elif cmd == "status":
        print(json.dumps(getHotTubStatus(), indent=2))

    elif cmd == "heater_on":
        print(set_heater_state(1))
    elif cmd == "heater_off":
        print(set_heater_state(0))

    elif cmd == "set_temp" and len(args) == 2:
        print(set_temperature_setting(int(args[1])))

    elif cmd == "bubble_on":
        print(set_bubble_state(1, 3))
    elif cmd == "bubble_off":
        print(set_bubble_state(0, -1))

    elif cmd == "jet_on":
        print(set_jet_state(1))
    elif cmd == "jet_off":
        print(set_jet_state(0))

    elif cmd == "filter_on":
        print(set_filter_state(1))
    elif cmd == "filter_off":
        print(set_filter_state(0))

    else:
        print("Unknown command.")
