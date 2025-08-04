import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import MSpaUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.CLIMATE,
    Platform.NUMBER
]

SERVICES = [
    "set_temperature",
    "set_heater",
    "set_filter",
    "set_bubble",
    "set_jet",
    "set_bubble_level"
]

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the MSpa integration from configuration.yaml (if used)."""
    return True

def _register_services(hass, coordinator):
    for service in SERVICES:
        hass.services.async_register(DOMAIN, service, getattr(coordinator, service))
        _LOGGER.debug('MSpa registered "%s" service', service)

def _unregister_services(hass):
    for service in SERVICES:
        hass.services.async_remove(DOMAIN, service)
        _LOGGER.debug('MSpa unregistered "%s" service', service)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up MSpa from a config entry."""
    _LOGGER.setLevel(logging.DEBUG)
    coordinator = MSpaUpdateCoordinator(hass, entry)
    await coordinator.api.async_init()
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    _LOGGER.debug("MSpa integration %s setup %s %s", DOMAIN, entry.title, entry.entry_id)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _LOGGER.debug("MSpa coordinator set up and initial data fetched")

    _register_services(hass, coordinator)
    _LOGGER.info("MSpa integration %s setup complete", DOMAIN)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    _LOGGER.debug("Unloading MSpa integration %s for entry %s", DOMAIN, entry.entry_id)
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        _unregister_services(hass)
        _LOGGER.debug("MSpa integration %s unloaded successfully for entry %s", DOMAIN, entry.entry_id)
    return unload_ok