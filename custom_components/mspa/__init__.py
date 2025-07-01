import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .coordinator import MSpaUpdateCoordinator
from homeassistant.const import (
    Platform,
)
_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the MSpa integration from configuration.yaml (if used)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up MSpa from a config entry."""
    coordinator = MSpaUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    _LOGGER.debug("MSpa integration %s setup %s %s", DOMAIN, entry.title, entry.entry_id)

    await hass.config_entries.async_forward_entry_setups(
        entry,
        [
            Platform.SENSOR,
            Platform.SWITCH,
            Platform.CLIMATE
        ]
    )
    _LOGGER.debug("MSpa coordinator set up and initial data fetched")

    # Register services
    hass.services.async_register(
        DOMAIN,
        "set_temperature",
        coordinator.set_temperature
    )
    _LOGGER.debug("MSpa registered \"set_temperature\" service")

    hass.services.async_register(
        DOMAIN,
        "set_heater",
        coordinator.set_heater
    )
    _LOGGER.debug("MSpa registered \"set_heater\" service")

    hass.services.async_register(
        DOMAIN,
        "set_filter",
        coordinator.set_filter
    )
    _LOGGER.debug("MSpa registered \"set_filter\" service")

    hass.services.async_register(
        DOMAIN,
        "set_bubble",
        coordinator.set_bubble
    )
    _LOGGER.debug("MSpa registered \"set_bubble\" service")
    hass.services.async_register(
        DOMAIN,
        "set_jet",
        coordinator.set_jet
    )
    _LOGGER.debug("MSpa registered \"set_jet\" service")

    hass.services.async_register(
        DOMAIN,
        "set_bubble_level",
        coordinator.set_bubble_level
    )
    _LOGGER.debug("MSpa registered \"set_bubble_level\" service")

    _LOGGER.debug("MSpa integration %s setup complete", DOMAIN)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    # Clean up resources here
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True