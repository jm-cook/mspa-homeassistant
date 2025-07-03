"""Sensor platform for MSpa integration."""
import logging
from homeassistant.components.sensor import SensorEntity, SensorStateClass, SensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .entity import MSpaEntity

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    "water_temperature": ["Water Temperature", "°C", SensorStateClass.MEASUREMENT, SensorDeviceClass.TEMPERATURE] #,
    # "target_temperature": ["Target Temperature", "°C", SensorDeviceClass.TEMPERATURE],
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
    # _LOGGER.debug("ozone switch: %s", hasattr(coordinator, "has_ozone_switch"))
    # if not hasattr(coordinator, "has_ozone_switch") or not coordinator.has_ozone_switch:
    #     entities.append(MSpaSensor(coordinator, "ozone"))
    #
    # _LOGGER.debug("uvc switch: %s", hasattr(coordinator, "has_uvc_switch"))
    # if not hasattr(coordinator, "has_uvc_switch") or not coordinator.has_uvc_switch:
    #     entities.append(MSpaSensor(coordinator, "uvc"))

    async_add_entities(entities)


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
