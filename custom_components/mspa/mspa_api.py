import asyncio
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
        self.product_pic_url = None
        self._last_status = None

    async def async_init(self):
        _LOGGER.info("DIAGNOSTIC: Starting MSpaApiClient initialization")
        device_list = await self.get_device_list()
        _LOGGER.info("DIAGNOSTIC: device_list result: %s", device_list)

        if not device_list:
            _LOGGER.error("DIAGNOSTIC: device_list is None or empty!")
            _LOGGER.error("No devices found. Please check your credentials and network connection.")
            raise RuntimeError("MSpaApiClient initialization failed: No devices found.")

        if not isinstance(device_list, dict):
            _LOGGER.error("DIAGNOSTIC: device_list is not a dict! Type: %s, Value: %s", type(device_list), device_list)
            raise RuntimeError("MSpaApiClient initialization failed: Unexpected device_list format.")

        if "list" not in device_list:
            _LOGGER.error("DIAGNOSTIC: 'list' key not found in device_list! Keys: %s", device_list.keys())
            raise RuntimeError("MSpaApiClient initialization failed: No 'list' in device_list.")

        devices = device_list["list"]

        if not devices or len(devices) == 0:
            _LOGGER.error("DIAGNOSTIC: Device list is empty! Full device_list: %s", device_list)
            raise RuntimeError("MSpaApiClient initialization failed: Device list is empty.")

        _LOGGER.info("DIAGNOSTIC: Found %d device(s). First device: %s", len(devices), devices[0])
        self.product_id = devices[0]["product_id"] if "product_id" in devices[0] else None
        self.device_id = devices[0]["device_id"] if "device_id" in devices[0] else None
        self.series = devices[0]["product_series"] if "product_series" in devices[0] else None
        self.model = devices[0]["product_model"] if "product_model" in devices[0] else None
        self.software_version = devices[0]["software_version"] if "software_version" in devices[0] else None
        self.product_pic_url = devices[0]["url"] if "url" in devices[0] else None

        self.device_alias = devices[0]["device_alias"] if "device_alias" in devices[0] else None
        self.coordinator.model = self.model
        self.coordinator.series = self.series
        self.coordinator.software_version = self.software_version
        self.coordinator.product_pic_url = self.product_pic_url
        self.coordinator.device_id = self.device_id
        self.coordinator.product_id = self.product_id
        self.coordinator.device_alias = self.device_alias

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


    async def authenticate(self):
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

        _LOGGER.info("DIAGNOSTIC: Attempting authentication to %s", token_request_url)
        _LOGGER.info("DIAGNOSTIC: Account email: %s", self.account_email)

        try:
            response = await self.hass.async_add_executor_job(
                functools.partial(requests.post, token_request_url, headers=headers, json=payload, timeout=30)
            )
            _LOGGER.info("DIAGNOSTIC: Authentication HTTP status code: %s", response.status_code)
            _LOGGER.info("DIAGNOSTIC: Authentication raw response: %s", response.text)

            response_json = response.json()
            _LOGGER.info("DIAGNOSTIC: Authentication parsed response: %s", response_json)

            token = response_json.get("data", {}).get("token")
            if token is not None:
                _LOGGER.info("DIAGNOSTIC: Token successfully received (length: %d)", len(token))
                self.set_token_in_hass(token)
                return token
            else:
                _LOGGER.warning("DIAGNOSTIC: No token in response. Response data: %s", response_json.get("data"))
                _LOGGER.warning("DIAGNOSTIC: Full response: %s", response_json)
                return self.get_token_from_hass()
        except requests.exceptions.Timeout:
            _LOGGER.error("DIAGNOSTIC: Authentication request timed out after 30 seconds")
            raise
        except requests.exceptions.ConnectionError as e:
            _LOGGER.error("DIAGNOSTIC: Connection error during authentication: %s", str(e))
            raise
        except Exception as e:
            _LOGGER.error("DIAGNOSTIC: Unexpected error during authentication: %s", str(e), exc_info=True)
            raise

    async def send_device_command(self, desired_dict, retry=False):
        _LOGGER.debug("send_device_command: %s, retry %s", desired_dict, retry)
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
        payload = {
            "device_id": self.device_id,
            "product_id": self.product_id,
            "desired": json.dumps({"state": {"desired": desired_dict}})
        }

        url = "https://api.iot.the-mspa.com/api/device/command"
        _LOGGER.debug("send_device_command: %s, url: %s", desired_dict, url)
        response = await self.hass.async_add_executor_job(
            functools.partial(requests.post, url, headers=headers, json=payload)
        )
        response = response.json()
        if (response.get('message') != 'SUCCESS') and (not retry):
            token = await self.authenticate()
            return await self.send_device_command(desired_dict, True)

        # Poll for expected state if provided
        for _ in range(5):
            await asyncio.sleep(3)
            status = await self.get_hot_tub_status()
            if all(status.get(k) == v for k, v in desired_dict.items()):
                self._last_status = status  # Cache latest status
                break

        if (desired_dict.get("filter_state")) == 0:
            await self.set_heater_state(0)

        # Trigger coordinator refresh after command completes
        await self.coordinator.async_request_refresh()

        return response



    async def set_heater_state(self, state: int):
        return await self.send_device_command({"heater_state": state})

    async def set_bubble_state(self, state: int, level: int):
        return await self.send_device_command({"bubble_state": state, "bubble_level": level})

    async def set_bubble_level(self, level: int):
        return await self.send_device_command({"bubble_level": level})

    async def set_jet_state(self, state: int):
        return await self.send_device_command({"jet_state": state})

    async def set_filter_state(self, state: int):
        return await self.send_device_command({"filter_state": state})

    async def set_ozone_state(self, state: int):
        return await self.send_device_command({"ozone_state": state})

    async def set_uvc_state(self, state: int):
        return await self.send_device_command({"uvc_state": state})

    async def set_temperature_setting(self, temp: int):
        return await self.send_device_command({"temperature_setting": temp*2})

    async def get_hot_tub_status(self, retry=False):
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
        response = await self.hass.async_add_executor_job(
            functools.partial(requests.post, url, headers=headers, json=payload)
        )
        response = response.json()
        if not response.get("data") and not retry:
            await self.authenticate()
            return await self.get_hot_tub_status(True)
        data = response["data"]
        _LOGGER.debug("get_hot_tub_status %s", data)
        return data

    async def get_device_list(self, retry=False):
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

        _LOGGER.info("DIAGNOSTIC: Attempting to get device list from %s (retry=%s)", url, retry)
        _LOGGER.info("DIAGNOSTIC: Using token (first 20 chars): %s...", self.get_former_token()[:20] if self.get_former_token() else "None")

        try:
            response = await self.hass.async_add_executor_job(
                functools.partial(requests.get, url, headers=headers, timeout=30)
            )
            _LOGGER.info("DIAGNOSTIC: Device list HTTP status code: %s", response.status_code)
            _LOGGER.info("DIAGNOSTIC: Device list raw response: %s", response.text)

            response_json = response.json()
            _LOGGER.info("DIAGNOSTIC: Device list parsed response: %s", response_json)

            if not response_json.get("data") and not retry:
                _LOGGER.warning("DIAGNOSTIC: No data in device list response, re-authenticating...")
                await self.authenticate()
                return await self.get_device_list(True)

            data = response_json["data"]
            device_count = len(data.get("list", [])) if isinstance(data, dict) else 0
            _LOGGER.info("DIAGNOSTIC: Device list returned successfully. Number of devices: %d", device_count)

            if device_count == 0:
                _LOGGER.error("DIAGNOSTIC: Device list is empty! Full data structure: %s", data)
            else:
                _LOGGER.info("DIAGNOSTIC: First device info: %s", data.get("list", [])[0] if data.get("list") else "No list key")

            return data
        except requests.exceptions.Timeout:
            _LOGGER.error("DIAGNOSTIC: Device list request timed out after 30 seconds")
            raise
        except requests.exceptions.ConnectionError as e:
            _LOGGER.error("DIAGNOSTIC: Connection error getting device list: %s", str(e))
            raise
        except Exception as e:
            _LOGGER.error("DIAGNOSTIC: Unexpected error getting device list: %s", str(e), exc_info=True)
            raise
