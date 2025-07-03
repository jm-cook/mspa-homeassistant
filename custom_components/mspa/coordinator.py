"""DataUpdateCoordinator for MSpa integration."""
import logging
from datetime import timedelta
from .mspa_api import MSpaApiClient

from typing import Any, Dict
import asyncio

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    ATTR_TEMPERATURE,
    ATTR_STATE,
)

_LOGGER = logging.getLogger(__name__)

class MSpaUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from MSpa Hot Tub."""

    def __init__(self, hass: HomeAssistant, config_entry: Dict[str, Any]) -> None:
        """Initialize."""
        _LOGGER.debug(f"MSpaUpdateCoordinator initializing {config_entry.data}")
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.config = config_entry.data
        self.account_email = self.config["account_email"]
        self.password = self.config["password"]  # Already MD5 hashed

        self._last_data = {}
        self.api = MSpaApiClient(
            hass=hass,
            account_email=self.account_email,
            password=self.password,
            coordinator=self,
        )
        self._update_lock = asyncio.Lock()


    async def async_request_refresh(self) -> None:
        async with self._update_lock:
            await asyncio.sleep(10)  # Wait for 10 seconds before proceeding so that any pending commands will have time to complete
            await super().async_request_refresh()


    async def _async_update_data(self) -> Dict[str, Any]:
        """Update data via direct function call."""
        try:
            async with self._update_lock:
                # Directly call the hot_tub status function
                status_data = await self.hass.async_add_executor_job(self.api.get_hot_tub_status, None)

                transformed_data = {
                    "water_temperature": float(status_data.get("water_temperature", 0))/2,
                    "target_temperature": float(status_data.get("temperature_setting", 0))/2,
                    "heater": "on" if status_data.get("heater_state", 0) else "off",
                    "filter": "on" if status_data.get("filter_state", 0) else "off",
                    "bubble": "on" if status_data.get("bubble_state", 0) else "off",
                    "jet": "on" if status_data.get("jet_state", 0) else "off",
                    "ozone": "on" if status_data.get("ozone_state", 0) else "off",
                    "uvc": "on" if status_data.get("uvc_state", 0) else "off",
                    "bubble_level": status_data.get("bubble_level", 1)
                }

                self._last_data = transformed_data
                _LOGGER.debug("Fetched MSpa status_data: %s", status_data)
                _LOGGER.debug("Fetched MSpa transformed data: %s", transformed_data)
                return transformed_data

        except Exception as err:
            _LOGGER.error("Error updating MSpa data: %s", str(err))
            raise UpdateFailed(f"Update failed: {str(err)}")


    # Map of features to their respective API methods
    FEATURE_API_MAP = {
        "heater": "set_heater_state",
        "filter": "set_filter_state",
        "bubble": "set_bubble_state",
        "jet": "set_jet_state",
        "ozone": "set_ozone_state",
        "uvc": "set_uvc_state",
    }

    async def set_feature_state(self, feature: str, state: str) -> None:
        """Set a feature state using the API map."""
        _LOGGER.debug(f"Setting MSpa feature {feature} to {state}")
        try:
            if state.lower() not in ["on", "off"]:
                raise ValueError("State must be 'on' or 'off'")
            numerical_state = 1 if state.lower() == "on" else 0
            api_method = getattr(self.api, self.FEATURE_API_MAP[feature])
            await self.hass.async_add_executor_job(api_method, numerical_state)
            await self.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set %s to %s: %s", feature, state, str(err))
            raise

    async def set_temperature(self, service: ServiceCall) -> None:
        """Set the target temperature."""
        try:
            temperature = service.data.get(ATTR_TEMPERATURE)
            _LOGGER.debug("Setting temperature to %s", temperature)
            await self.hass.async_add_executor_job(self.api.set_temperature_setting, temperature)
            await self.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set temperature: %s", str(err))
            raise

    async def set_bubble_level(self, service: ServiceCall) -> None:
        """Set the bubble level only if bubble is on, else show a notification."""
        try:
            bubble_level = service.data.get("level")
            if self._last_data.get("bubble") != "on":
                _LOGGER.warning("Cannot set bubble level: Bubble is not on.")
                await self.hass.services.async_call(
                    "persistent_notification",
                    "create",
                    {
                        "title": "MSpa Bubble Level",
                        "message": "Cannot set bubble level because the bubble feature is not on.",
                    },
                    blocking=True,
                )
                return
            _LOGGER.debug("Setting bubble level to %s", bubble_level)
            await self.hass.async_add_executor_job(self.api.set_bubble_level, bubble_level)
            await self.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set bubble level: %s", str(err))
            raise

    # Generic service handler for features
    async def handle_feature_service(self, service: ServiceCall) -> None:
        feature = service.service.replace("set_", "")
        state = service.data.get(ATTR_STATE)
        await self.set_feature_state(feature, state)

    # Register these as service handlers in __init__.py:
    # set_heater, set_filter, set_bubble, set_jet, set_ozone, set_uvc
    set_heater = handle_feature_service
    set_filter = handle_feature_service
    set_bubble = handle_feature_service
    set_jet = handle_feature_service
    set_ozone = handle_feature_service
    set_uvc = handle_feature_service

    @property
    def last_data(self) -> dict:
        return self._last_data
