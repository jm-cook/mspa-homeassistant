import hashlib
import time
import random
import string
import requests
import json
import sys
import os
import logging

_LOGGER = logging.getLogger(__name__)

# Relevant ids and secrets:
# The App ID is sent in each HTTP request header from the Mspa app.
app_id = "e1c8e068f9ca11eba4dc0242ac120002"
# The App Secret can be determined by decompiling the Mspa app.
app_secret = "87025c9ecd18906d27225fe79cb68349"


class MSpaApiClient:
    def __init__(self, account_email, password, device_id, product_id, token_file="token.txt"):
        self.account_email = account_email
        self.password = password
        self.device_id = device_id
        self.product_id = product_id
        self.app_id = app_id
        self.app_secret = app_secret
        self.token_file = token_file

    @staticmethod
    def generate_nonce(length=32):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    @staticmethod
    def current_ts():
        return str(int(time.time()))

    def build_signature(self, nonce, ts):
        raw = self.app_id + "," + self.app_secret + "," + nonce + "," + ts
        return hashlib.md5(raw.encode("utf-8")).hexdigest().upper()

    def get_former_token(self):
        try:
            with open(self.token_file, "r") as file:
                return file.read().strip()
        except FileNotFoundError:
            return ""

    def write_token(self, token):
        with open(self.token_file, "w") as file:
            file.write(token)

    def authenticate(self):
        nonce = self.generate_nonce()
        ts = self.current_ts()
        sign = self.build_signature(nonce, ts)
        headers = {
            "push_type": "Android",
            "authorization": "token",
            "appid": self.app_id,
            "nonce": nonce,
            "ts": ts,
            "lan_code": "de",
            "sign": sign,
            "content-type": "application/json; charset=UTF-8",
            "accept-encoding": "gzip",
            "user-agent": "okhttp/4.9.0"
        }
        payload = {
            "account": self.account_email,
            "app_id": self.app_id,
            "password": self.password,
            "brand": "",
            "registration_id": "",
            "push_type": "android",
            "lan_code": "EN",
            "country": ""
        }
        token_request_url = "https://api.iot.the-mspa.com/api/enduser/get_token/"
        response = requests.post(token_request_url, headers=headers, json=payload).json()
        token = response.get("data", {}).get("token")
        if token is not None:
            self.write_token(token)
            return token
        else:
            return self.get_former_token()

    def send_device_command(self, desired_dict, retry=False, bubble_level=-1):
        token = self.get_former_token()
        nonce = self.generate_nonce()
        ts = self.current_ts()
        sign = self.build_signature(nonce, ts)
        headers = {
            "push_type": "Android",
            "authorization": "token " + token,
            "appid": self.app_id,
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
                "device_id": self.device_id,
                "product_id": self.product_id,
                "desired": json.dumps({"state": {"desired": desired_dict}})
            }
        else:
            payload = {
                "device_id": self.device_id,
                "product_id": self.product_id,
                "desired": json.dumps({"state": {"desired": desired_dict, "bubble_level": bubble_level}})
            }
        url = "https://api.iot.the-mspa.com/api/device/command"
        response = requests.post(url, headers=headers, json=payload).json()
        if (response.get('message') != 'SUCCESS') and (not retry):
            token = self.authenticate()
            if bubble_level < 0:
                return self.send_device_command(desired_dict, True)
            else:
                return self.send_device_command(desired_dict, True, bubble_level)

        if (desired_dict.get("heater_state")) == 0:
            self.set_filter_state(0)
        return response

    def set_heater_state(self, state: int):
        return self.send_device_command({"heater_state": state})

    def set_bubble_state(self, state: int):
        return self.send_device_command({"bubble_state": state})

    def set_bubble_level(self, level: int):
        return self.send_device_command({"bubble_level": level})

    def set_jet_state(self, state: int):
        return self.send_device_command({"jet_state": state})

    def set_filter_state(self, state: int):
        return self.send_device_command({"filter_state": state})

    def set_temperature_setting(self, temp: int):
        return self.send_device_command({"temperature_setting": temp*2})

    def get_hot_tub_status(self, retry=False):
        nonce = self.generate_nonce()
        ts = self.current_ts()
        sign = self.build_signature(nonce, ts)
        headers = {
            "push_type": "Android",
            "authorization": "token " + self.get_former_token(),
            "appid": self.app_id,
            "nonce": nonce,
            "ts": ts,
            "lan_code": "de",
            "sign": sign,
            "content-type": "application/json; charset=UTF-8",
            "accept-encoding": "gzip",
            "user-agent": "okhttp/4.9.0"
        }
        payload = {
            "device_id": self.device_id,
            "product_id": self.product_id
        }
        url = "https://api.iot.the-mspa.com/api/device/thing_shadow/"
        response = requests.post(url, headers=headers, json=payload).json()
        if not response.get("data") and not retry:
            token = self.authenticate()
            self.write_token(token)
            return self.get_hot_tub_status(True)
        data = response["data"]
        _LOGGER.debug("get_hot_tub_status %s", data)
        return data
