"""Sensor platform for MSpa integration."""
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, TEMP_UNIT

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up MSpa sensors based on a config entry."""
    _LOGGER.debug("Setting up sensors for MSpa")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = [
        MSpaTemperatureSensor(coordinator, "water_temperature"),
        MSpaTemperatureSensor(coordinator, "target_temperature"),
    ]
    
    async_add_entities(sensors)

class MSpaTemperatureSensor(CoordinatorEntity, SensorEntity):
    """Representation of a MSpa Temperature Sensor."""

    def __init__(self, coordinator, sensor_type):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.sensor_type = sensor_type
        self._attr_native_unit_of_measurement = TEMP_UNIT
        _LOGGER.debug("MSpaTemperatureSensor initialized")

    @property
    def name(self):
        """Return the name of the sensor."""
        _LOGGER.debug("Getting name for sensor %s", self.sensor_type)
        return f"MSpa {self.sensor_type.replace('_', ' ').title()}"

    @property
    def unique_id(self):
        """Return a unique ID."""
        _LOGGER.debug("Getting unique ID for sensor %s", self.sensor_type)
        return f"mspa_{self.sensor_type}"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        _LOGGER.debug("Getting native value for sensor %s", self.sensor_type)
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self.sensor_type.replace("water_", ""))