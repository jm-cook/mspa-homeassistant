import hashlib
import time
import random
import string
import requests
import json

import logging
import functools


_LOGGER = logging.getLogger(__name__)

# Relevant ids and secrets:
# The App ID is sent in each HTTP request header from the Mspa app.
app_id = "e1c8e068f9ca11eba4dc0242ac120002"
# The App Secret can be determined by decompiling the Mspa app.
app_secret = "87025c9ecd18906d27225fe79cb68349"


class MSpaApiClient:
    def __init__(self, hass, account_email, password, coordinator, token=None):
        self.account_email = account_email
        self.password = password
        self.app_id = app_id
        self.app_secret = app_secret
        self.hass = hass
        self._token = token or self.get_token_from_hass()
        self.coordinator = coordinator
        self.product_id = None
        self.device_id = None
        self.series = None
        self.model = None
        self.software_version = None

    async def async_init(self):
        device_list = await self.async_get_device_list()
        _LOGGER.debug("device_list: %s", device_list)
        if not device_list:
            _LOGGER.error("No devices found. Please check your credentials and network connection.")
            raise RuntimeError("MSpaApiClient initialization failed: No devices found.")
        devices = device_list["list"]
        self.product_id = devices[0]["product_id"]
        self.device_id = devices[0]["device_id"]
        self.series = devices[0]["product_series"]
        self.model = devices[0]["product_model"]
        self.software_version = devices[0]["software_version"]

        self.coordinator.model = self.model
        self.coordinator.series = self.series
        self.coordinator.software_version = self.software_version

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
        return self._token or self.get_token_from_hass() or ""


    def get_token_from_hass(self):
        return self.hass.data.get("mspa_token")

    def set_token_in_hass(self, token):
        self.hass.data["mspa_token"] = token
        self._token = token

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
        _LOGGER.debug("authenticate response: %s", response)
        if token is not None:
            self.set_token_in_hass(token)
            return token
        else:
            return self.get_token_from_hass()

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

    def set_ozone_state(self, state: int):
        return self.send_device_command({"ozone_state": state})

    def set_uvc_state(self, state: int):
        return self.send_device_command({"uvc_state": state})

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
            self.authenticate()
            return self.get_hot_tub_status(True)
        data = response["data"]
        _LOGGER.debug("get_hot_tub_status %s", data)
        return data


    async def async_get_device_list(self, retry=False):
        return await self.hass.async_add_executor_job(functools.partial(self.get_device_list, retry))

    def get_device_list(self, retry=False):
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
        url = "https://api.iot.the-mspa.com/api/enduser/devices/"
        response = requests.get(url, headers=headers).json()
        if not response.get("data") and not retry:
            self.authenticate()
            return self.get_device_list(True)
        data = response["data"]
        _LOGGER.debug("get_device_list %s", data)
        return data

