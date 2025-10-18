"""Sensor platform for MSpa integration."""
import logging
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.helpers.entity import EntityCategory
from homeassistant.const import UnitOfPower

from .const import DOMAIN
from .entity import MSpaSensorEntity, MSpaBinarySensorEntity

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
    # Pass the config entry so the heater power sensor can read per-device options
    async_add_entities([MSpaHeaterPowerSensor(coordinator, entry)], update_before_add=True)

    diagnostic_sensors = [
        MSpaDiagnosticSensor(coordinator, key, f"{key.replace('_', ' ').title()}")
        for key in DIAGNOSTIC_KEYS
    ]
    async_add_entities(diagnostic_sensors)


class MSpaSensor(MSpaSensorEntity):
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
class MSpaDiagnosticSensor(MSpaSensorEntity):
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
class MSpaFaultSensor(MSpaDiagnosticSensor):
    name = "Fault"
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
class MSpaFilterSensor(MSpaDiagnosticSensor):
    name = "Filter status"
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

class MSpaHeaterTimerBinarySensor(MSpaBinarySensorEntity):
    name = "Heater timer"

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

class MSpaHeaterTimerTimeSensor(MSpaSensorEntity):
    name = "Heater timer remaining"
    _attr_native_unit_of_measurement = "h"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"mspa_heater_timer_remaining_{getattr(coordinator, 'device_id', 'unknown')}"
        self._attr_device_info = self.device_info

    @property
    def native_value(self):
        return self.coordinator._last_data.get("heat_time", 0)

class MSpaHeaterPowerSensor(MSpaSensorEntity):
    """Sensor to report current heater power consumption based on heat state and per-device options."""
    name = "Heater Power"
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.POWER

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"mspa_heater_power_{getattr(coordinator, 'device_id', 'unknown')}"
        self._attr_device_info = self.device_info
        self._config_entry = config_entry

    def _get_option_int(self, key: str, default: int) -> int:
        opts = getattr(self._config_entry, "options", {}) or {}
        val = opts.get(key, default)
        try:
            ival = int(val)
            if ival < 0:
                raise ValueError
            return ival
        except (TypeError, ValueError):
            return default

    @property
    def native_value(self):
        """Return the power consumption based on heat state using per-device options."""
        heat_state = self.coordinator._last_data.get("heat_state")
        heater_on = self.coordinator._last_data.get("heater") == "on"

        if not heater_on:
            return 0

        preheat_w = self._get_option_int("heater_power_preheat", 1500)
        heat_w = self._get_option_int("heater_power_heat", 2000)

        if heat_state == 2:
            return preheat_w
        elif heat_state == 3:
            return heat_w
        elif heat_state == 4:
            return 0
        else:
            return 0

    @property
    def icon(self):
        power = self.native_value
        return "mdi:lightning-bolt" if power > 0 else "mdi:power-plug-off"