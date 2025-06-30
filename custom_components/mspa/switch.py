from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN
from .entity import MSpaEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import MSpaUpdateCoordinator
import logging

_LOGGER = logging.getLogger(__name__)
# Switches for MSpa features
# These switches control the heater, filter, bubble, and jet features of the MSpa hot tub.

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the MSpa switch entities."""
    coordinator: MSpaUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        MSpaHeaterSwitch(coordinator),
        MSpaFilterSwitch(coordinator),
        MSpaBubbleSwitch(coordinator),
        MSpaJetSwitch(coordinator),
        MSpaOzoneSwitch(coordinator),
        MSpaUVCSwitch(coordinator)
        # Add other switches here if needed
    ]
    async_add_entities(entities)


class MSpaHeaterSwitch(CoordinatorEntity, MSpaEntity, SwitchEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Heater"
        self._attr_icon = "mdi:hot-tub"
        self._attr_unique_id = f"mspa_heater_{getattr(coordinator, 'device_id', 'unknown')}"

    @property
    def is_on(self):
        _LOGGER.debug("heater is %s", self.coordinator._last_data.get("heater"))
        return True if self.coordinator._last_data.get("heater") == "on" else False

    async def async_turn_on(self, **kwargs):
        _LOGGER.debug("Turning on heater")
        await self.coordinator.set_feature(feature="heater", state="on")

    async def async_turn_off(self, **kwargs):
        _LOGGER.debug("Turning off heater")
        await self.coordinator.set_feature(feature="heater", state="off")

class MSpaFilterSwitch(MSpaEntity, SwitchEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Filter"
        self._attr_icon = "mdi:air-filter"
        self._attr_unique_id = f"mspa_filter_{getattr(coordinator, 'device_id', 'unknown')}"

    @property
    def is_on(self):
        _LOGGER.debug("filter is %s", self.coordinator._last_data.get("filter"))
        return True if self.coordinator._last_data.get("filter") == "on" else False

    async def async_turn_on(self, **kwargs):
        await self.coordinator.set_feature(feature="filter", state="on")

    async def async_turn_off(self, **kwargs):
        await self.coordinator.set_feature(feature="filter", state="off")

class MSpaBubbleSwitch(MSpaEntity, SwitchEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Bubble"
        self._attr_icon = "mdi:chart-bubble"
        self._attr_unique_id = f"mspa_bubble_{getattr(coordinator, 'device_id', 'unknown')}"

    @property
    def is_on(self):
        _LOGGER.debug("bubble is %s", self.coordinator._last_data.get("bubble"))
        return True if self.coordinator._last_data.get("bubble") == "on" else False

    async def async_turn_on(self, **kwargs):
        await self.coordinator.set_feature(feature="bubble", state="on")

    async def async_turn_off(self, **kwargs):
        await self.coordinator.set_feature(feature="bubble", state="off")

class MSpaJetSwitch(MSpaEntity, SwitchEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Jet"
        # self._attr_icon = "mdi:jet"
        self._attr_unique_id = f"mspa_jet_{getattr(coordinator, 'device_id', 'unknown')}"

    @property
    def is_on(self):
        _LOGGER.debug("jet is %s", self.coordinator._last_data.get("jet"))
        return True if self.coordinator._last_data.get("jet") == "on" else False

    async def async_turn_on(self, **kwargs):
        await self.coordinator.set_feature(feature="jet", state="on")

    async def async_turn_off(self, **kwargs):
        await self.coordinator.set_feature(feature="jet", state="off")

class MSpaOzoneSwitch(MSpaEntity, SwitchEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Ozone"
        self._attr_icon = "mdi:weather-hazy"

        self._attr_unique_id = f"mspa_ozone_{getattr(coordinator, 'device_id', 'unknown')}"
        coordinator.has_ozone_switch = True

    @property
    def is_on(self):
        _LOGGER.debug("ozone is %s", self.coordinator._last_data.get("ozone"))
        return True if self.coordinator._last_data.get("ozone") == "on" else False

    async def async_turn_on(self, **kwargs):
        await self.coordinator.set_feature(feature="ozone", state="on")

    async def async_turn_off(self, **kwargs):
        await self.coordinator.set_feature(feature="ozone", state="off")

class MSpaUVCSwitch(MSpaEntity, SwitchEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "UVC"
        self._attr_icon = "mdi:weather-sunny-alert"
        self._attr_unique_id = f"mspa_uvc_{getattr(coordinator, 'device_id', 'unknown')}"
        coordinator.has_uvc_switch = True

    @property
    def is_on(self):
        _LOGGER.debug("uvc is %s", self.coordinator._last_data.get("uvc"))
        return True if self.coordinator._last_data.get("uvc") == "on" else False

    async def async_turn_on(self, **kwargs):
        await self.coordinator.set_feature(feature="uvc", state="on")

    async def async_turn_off(self, **kwargs):
        await self.coordinator.set_feature(feature="uvc", state="off")