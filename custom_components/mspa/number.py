import logging

from homeassistant.components.number import NumberEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .entity import MSpaEntity
from .coordinator import MSpaUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator: MSpaUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MspaBubbleLevelNumber(coordinator)])

class MspaBubbleLevelNumber(CoordinatorEntity, MSpaEntity, NumberEntity):
    """Representation of the MSpa bubble level number entity."""

    name = "Bubble Level"
    icon = "mdi:chart-bubble"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"mspa_bubble_level_{getattr(coordinator, 'device_id', 'unknown')}"
        # self._attr_min_value = 1
        # self._attr_max_value = 3
        self._attr_native_min_value = 1
        self._attr_native_max_value = 3
        self._attr_native_step = 1

    @property
    def native_value(self):
        return self.coordinator._last_data.get("bubble_level", 1)

    async def async_set_native_value(self, value: int):
        value = max(self._attr_native_min_value, min(self._attr_native_max_value, int(value)))
        _LOGGER.debug("Setting bubble level to %d", value)
        await self.coordinator.set_bubble_level(type("ServiceCall", (), {"data": {"level": value}})())
        await self.coordinator.async_request_refresh()