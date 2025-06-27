"""Sensor platform for MSpa integration."""
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    "water_temperature": ["Water Temperature", "°C"],
    "target_temperature": ["Target Temperature", "°C"],
    "heater": ["Heater", None],
    "filter": ["Filter", None],
    "bubble": ["Bubble", None],
    "jet": ["Jet", None],
}

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        MSpaSensor(coordinator, key)
        for key in SENSOR_TYPES
    ]
    async_add_entities(entities)

class MSpaSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, key):
        super().__init__(coordinator)
        self._key = key
        self._attr_name = SENSOR_TYPES[key][0]
        self._attr_unit_of_measurement = SENSOR_TYPES[key][1]
        self._attr_unique_id = f"mspa_{key}_{getattr(coordinator, 'device_id', 'unknown')}"

    @property
    def state(self):
        return self.coordinator._last_data.get(self._key)

    @property
    def available(self):
        return self.coordinator.last_update_success
