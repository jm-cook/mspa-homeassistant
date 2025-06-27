"""DataUpdateCoordinator for MSpa integration."""
import logging
from datetime import timedelta
from .mspa_api import MSpaApiClient

from typing import Any, Dict

from homeassistant.core import HomeAssistant
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

from typing import Any, Dict
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
        self.device_id = self.config["device_id"]
        self.product_id = self.config["product_id"]
        self._last_data = {}
        self.api = MSpaApiClient(
            account_email=self.account_email,
            password=self.password,
            device_id=self.device_id,
            product_id=self.product_id
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Update data via direct function call."""
        try:
            # Directly call the hot_tub status function
            status_data = await self.hass.async_add_executor_job(self.api.get_hot_tub_status)

            transformed_data = {
                "water_temperature": float(status_data.get("water_temperature", 0))/2,
                "target_temperature": float(status_data.get("temperature_setting", 0))/2,
                "heater": "on" if status_data.get("heater_state", 0) else "off",
                "filter": "on" if status_data.get("filter_state", 0) else "off",
                "bubble": "on" if status_data.get("bubble_state", 0) else "off",
                "jet": "on" if status_data.get("jet_state", 0) else "off"
            }

            self._last_data = transformed_data
            _LOGGER.debug("Fetched MSpa status_data: %s", status_data)
            _LOGGER.debug("Fetched MSpa transformed data: %s", transformed_data)
            return transformed_data

        except Exception as err:
            _LOGGER.error("Error updating MSpa data: %s", str(err))
            raise UpdateFailed(f"Update failed: {str(err)}")

    async def set_temperature(self, temperature: float) -> None:
        """Set the target temperature."""
        try:
            _LOGGER.debug("Setting temperature to %s", temperature)
            await self.hass.async_add_executor_job(self.api.set_temperature_setting, temperature)
            await self.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set temperature: %s", str(err))
            raise

    async def set_feature(self, feature: str, state: str) -> None:
        """Set a feature state (heater, filter, bubble, jet)."""
        try:
            _LOGGER.debug("Setting %s to %s", feature, state)
            # func = getattr(hot_tub, f"set_{feature}", None)
            func = None
            if func is None:
                raise AttributeError(f"No function set_{feature} in hot_tub.py")
            await self.hass.async_add_executor_job(func, state)
            await self.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set %s to %s: %s", feature, state, str(err))
            raise

    async def handle_service(self, service: str, data: Dict[str, Any]) -> None:
        """Handle services calls."""
        try:
            _LOGGER.debug("Handling service call: %s, %s", service, data)
            if service == "set_temperature":
                await self.set_temperature(float(data[ATTR_TEMPERATURE]))
            elif service in ["set_heater", "set_filter", "set_bubble", "set_jet"]:
                feature = service.replace("set_", "")
                await self.set_feature(feature, data[ATTR_STATE])
            else:
                _LOGGER.error("Unknown service: %s", service)
                raise ValueError(f"Unknown service: {service}")

            await self.async_request_refresh()

        except Exception as err:
            _LOGGER.error("Service call failed: %s", str(err))
            raise


    def set_debug(self, enable: bool) -> None:
        """Enable or disable debug logging for this integration."""
        if enable:
            _LOGGER.setLevel(logging.DEBUG)
            _LOGGER.debug("Debug logging enabled for MSpa integration.")
        else:
            _LOGGER.setLevel(logging.INFO)
            _LOGGER.info("Debug logging disabled for MSpa integration.")