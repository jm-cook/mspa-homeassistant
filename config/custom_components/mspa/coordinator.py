"""DataUpdateCoordinator for MSpa integration."""
import logging
from datetime import timedelta
import subprocess
import json
import asyncio
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

class MSpaUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from MSpa Hot Tub."""

    def __init__(self, hass: HomeAssistant, script_path: str, config: Dict[str, Any]) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.script_path = script_path
        self.config = config
        self._last_data = {}

    async def _async_run_script(self, command: str, extra_args: list = None) -> Dict[str, Any]:
        """Run the hot_tub.py script with given command."""
        try:
            cmd = [self.script_path, command]
            if extra_args:
                cmd.extend(extra_args)

            _LOGGER.debug("Running command: %s", " ".join(cmd))

            process = await self.hass.async_add_executor_job(
                subprocess.run,
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            try:
                return json.loads(process.stdout)
            except json.JSONDecodeError as err:
                _LOGGER.error("Failed to parse script output: %s", process.stdout)
                raise UpdateFailed(f"Invalid JSON response from script: {err}")

        except subprocess.CalledProcessError as err:
            _LOGGER.error("Script execution failed: %s", err.stderr)
            raise UpdateFailed(f"Script execution failed: {err.stderr}")
        except Exception as err:
            _LOGGER.error("Unexpected error running script: %s", str(err))
            raise UpdateFailed(f"Unexpected error: {str(err)}")

    async def _async_update_data(self) -> Dict[str, Any]:
        """Update data via script."""
        try:
            # Get the current status from the hot tub
            status_data = await self._async_run_script("status")

            # Transform the data into our expected format
            transformed_data = {
                "temperature": float(status_data.get("water_temp", 0)),
                "target_temp": float(status_data.get("target_temp", 0)),
                "heater": status_data.get("heater", "off") == "on",
                "filter": status_data.get("filter", "off") == "on",
                "bubble": status_data.get("bubble", "off") == "on",
                "jet": status_data.get("jet", "off") == "on",
            }

            self._last_data = transformed_data
            return transformed_data

        except Exception as err:
            _LOGGER.error("Error updating MSpa data: %s", str(err))
            raise UpdateFailed(f"Update failed: {str(err)}")

    async def set_temperature(self, temperature: float) -> None:
        """Set the target temperature."""
        try:
            await self._async_run_script("set_temperature", [str(temperature)])
            await self.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set temperature: %s", str(err))
            raise

    async def set_feature(self, feature: str, state: str) -> None:
        """Set a feature state (heater, filter, bubble, jet)."""
        try:
            await self._async_run_script(f"set_{feature}", [state])
            await self.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set %s to %s: %s", feature, state, str(err))
            raise

    async def handle_service(self, service: str, data: Dict[str, Any]) -> None:
        """Handle services calls."""
        try:
            if service == "set_temperature":
                await self.set_temperature(float(data[ATTR_TEMPERATURE]))
            elif service in ["set_heater", "set_filter", "set_bubble", "set_jet"]:
                feature = service.replace("set_", "")
                await self.set_feature(feature, data[ATTR_STATE])
            else:
                _LOGGER.error("Unknown service: %s", service)
                raise ValueError(f"Unknown service: {service}")

            # Request a refresh to update the states
            await self.async_request_refresh()

        except Exception as err:
            _LOGGER.error("Service call failed: %s", str(err))
            raise