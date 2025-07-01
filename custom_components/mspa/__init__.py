import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .coordinator import MSpaUpdateCoordinator
from homeassistant.const import Platform

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.SWITCH, Platform.CLIMATE]
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
    _LOGGER.debug("MSpa integration %s setup complete", DOMAIN)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True