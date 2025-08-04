"""Sensor platform for MSpa integration."""
import logging
from homeassistant.components.sensor import SensorEntity, SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN
from .entity import MSpaEntity

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    "water_temperature": ["Water Temperature", "°C", SensorStateClass.MEASUREMENT, SensorDeviceClass.TEMPERATURE]
}

DIAGNOSTIC_KEYS = [
    "wifivertion", "otastatus", "mcuversion", "ConnectType", "temperature_unit",
    "auto_inflate", "filter_current", "safety_lock", "heat_time_switch", "heat_state",
    "multimcuotainfo", "heat_time", "filter_life", "trdversion", "is_online",
    "warning", "device_heat_perhour"
]


MEASUREMENT_KEYS = {
    "temperature_unit",
    "filter_current",
    "heat_state",
    "heat_time",
    "filter_life",
    "device_heat_perhour"
}

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        MSpaSensor(coordinator, key)
        for key in SENSOR_TYPES
    ]

    async_add_entities(entities)
    async_add_entities([MSpaFaultSensor(coordinator)], update_before_add=True)
    async_add_entities([MSpaFilterSensor(coordinator)], update_before_add=True)
    async_add_entities([MSpaHeaterTimerBinarySensor(coordinator)], update_before_add=True)
    async_add_entities([MSpaHeaterTimerTimeSensor(coordinator)], update_before_add=True)

    diagnostic_sensors = [
        MSpaDiagnosticSensor(coordinator, key, f"{key.replace('_', ' ').title()}")
        for key in DIAGNOSTIC_KEYS
    ]
    async_add_entities(diagnostic_sensors)


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

# This sensor is used for diagnostic purposes.
# It retrieves various diagnostic information from the MSpa system.
# The keys are defined in the DIAGNOSTIC_KEYS list.
# Each sensor has a unique ID based on its key and the device ID.
# The state class is set to MEASUREMENT for keys that are measurements.
# The entity category is set to DIAGNOSTIC.
# The entity registry is disabled by default for these sensors.
# The entity picture is set to None.
# The state is retrieved from the coordinator's last data based on the key.
# The icon is not set, but can be customized if needed.
# The entity name is derived from the key, replacing underscores with spaces and capitalizing.
# The entity is registered with the Home Assistant entity registry.
# The entity is used to provide diagnostic information about the MSpa system.
# It can be used to monitor the status of the MSpa system and troubleshoot issues.
# The entity is not intended for user interaction, but rather for monitoring and diagnostics.
class MSpaDiagnosticSensor(CoordinatorEntity, MSpaEntity, SensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator, key, name):
        super().__init__(coordinator)
        self._attr_device_info = self.device_info

        self.coordinator = coordinator
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"mspa_{key}"
        if key in MEASUREMENT_KEYS:
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def state(self):
        return self.coordinator.last_data.get(self._key)

    @property
    def entity_picture(self):
        return None

# This sensor is used to indicate faults or warnings in the MSpa system.
# It checks the "fault" key in the coordinator's last data.
# If the fault is "OK", it indicates no issues.
# Otherwise, it indicates a fault condition.
# The icon changes based on the fault state.
class MSpaFaultSensor(MSpaDiagnosticSensor):
    _attr_name = "Fault"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator):
        super().__init__(coordinator, "fault", "Fault")
        self._attr_unique_id = f"mspa_fault_{getattr(coordinator, 'device_id', 'unknown')}"

    @property
    def state(self):
        return self.coordinator._last_data.get("fault", "OK")

    @property
    def icon(self):
        return "mdi:alert" if self.state != "OK" else "mdi:check-circle"

# This sensor monitors the filter status of the MSpa device.
# It checks the "warning" key in the coordinator's last data.
# If the warning is "A0", it indicates that the filter is dirty.
# Otherwise, it indicates that the filter is OK.
# python
class MSpaFilterSensor(MSpaDiagnosticSensor):
    _attr_name = "Filter status"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator):
        super().__init__(coordinator, "filter_status", "Filter status")
        self._attr_unique_id = f"mspa_filter_status{getattr(coordinator, 'device_id', 'unknown')}"

    @property
    def state(self):
        warning = self.coordinator._last_data.get("warning", "")
        return "Dirty" if warning == "A0" else "OK"

    @property
    def icon(self):
        return "mdi:filter-remove" if self.state == "Dirty" else "mdi:filter"

class MSpaHeaterTimerBinarySensor(CoordinatorEntity, MSpaEntity, BinarySensorEntity):
    _attr_name = "Heater timer"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"mspa_heater_timer_enabled_{getattr(coordinator, 'device_id', 'unknown')}"
        self._attr_device_info = self.device_info

    @property
    def is_on(self):
        return bool(self.coordinator._last_data.get("heat_time_switch", 0))

    @property
    def icon(self):
        return "mdi:timer-outline" if self.is_on else "mdi:timer-off-outline"

class MSpaHeaterTimerTimeSensor(CoordinatorEntity, MSpaEntity, SensorEntity):
    _attr_name = "Heater timer remaining"
    _attr_native_unit_of_measurement = "h"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"mspa_heater_timer_remaining_{getattr(coordinator, 'device_id', 'unknown')}"
        self._attr_device_info = self.device_info

    @property
    def native_value(self):
        return self.coordinator._last_data.get("heat_time", 0)