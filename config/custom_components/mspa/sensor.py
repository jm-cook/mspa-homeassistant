"""Sensor platform for MSpa integration."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up MSpa sensors based on a config entry."""
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
        self._attr_native_unit_of_measurement = TEMP_CELSIUS

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"MSpa {self.sensor_type.replace('_', ' ').title()}"

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"mspa_{self.sensor_type}"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self.sensor_type.replace("water_", ""))