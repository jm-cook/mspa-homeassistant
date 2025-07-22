"""Sensor platform for MSpa integration."""
import logging
from homeassistant.components.sensor import SensorEntity, SensorStateClass, SensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN
from .entity import MSpaEntity

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    "water_temperature": ["Water Temperature", "°C", SensorStateClass.MEASUREMENT, SensorDeviceClass.TEMPERATURE],
    "target_temperature": ["Target Temperature", "°C", SensorStateClass.MEASUREMENT, SensorDeviceClass.TEMPERATURE] #,
    # "heater": ["Heater", None, None],
    # "filter": ["Filter", None, None],
    # "bubble": ["Bubble", None, None],
    # "jet": ["Jet", None, None],
    # "uvc": ["UVC", None, None],
    # "ozone": ["Ozone", None, None]
}

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        MSpaSensor(coordinator, key)
        for key in SENSOR_TYPES
    ]

    async_add_entities(entities)
    async_add_entities([MSpaFaultSensor(coordinator)], update_before_add=True)


class MSpaSensor(CoordinatorEntity, MSpaEntity, SensorEntity):
    def __init__(self, coordinator, key):
        super().__init__(coordinator)

        if not key in SENSOR_TYPES:
            _LOGGER.error("Unknown sensor key: %s", key)
            return
        self._key = key
        self._attr_name = SENSOR_TYPES[key][0]
        self._attr_native_unit_of_measurement = SENSOR_TYPES[key][1]
        self._attr_unique_id = f"mspa_{key}_{getattr(coordinator, 'device_id', 'unknown')}"
        self._attr_state_class = SENSOR_TYPES[key][2]
        self._attr_device_class = SENSOR_TYPES[key][3]
        self._attr_device_info = self.device_info

    @property
    def native_value(self):
        return self.coordinator._last_data.get(self._key)

    @property
    def available(self):
        return self.coordinator.last_update_success

class MSpaFaultSensor(CoordinatorEntity, MSpaEntity, SensorEntity):
    _attr_name = "Fault"
    # _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator):
        super().__init__(coordinator)

        self._attr_device_info = self.device_info
        self._attr_unique_id = f"mspa_fault_{getattr(coordinator, 'device_id', 'unknown')}"
        _LOGGER.debug("Initializing MSpaFaultSensor with unique_id: %s", self._attr_unique_id)

    @property
    def state(self):
        # Replace with actual fault state retrieval logic
        return self.coordinator._last_data.get("fault", "OK")

    @property
    def icon(self):
        return "mdi:alert" if self.state != "OK" else "mdi:check-circle"

    @property
    def entity_picture(self):
        return None
