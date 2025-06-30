from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    ClimateEntityFeature,
    HVACMode,
)
from .const import DOMAIN, TEMP_UNIT
from .entity import MSpaEntity

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MSpaClimate(coordinator)])

class MSpaClimate(MSpaEntity, ClimateEntity):
    _attr_name = "MSpa Climate"
    _attr_temperature_unit = TEMP_UNIT
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_min_temp = 20
    _attr_max_temp = 40

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"mspa_climate_{getattr(coordinator, 'device_id', 'unknown')}"

    @property
    def current_temperature(self):
        return self.coordinator._last_data.get("water_temperature")

    @property
    def target_temperature(self):
        return self.coordinator._last_data.get("target_temperature")

    async def async_set_temperature(self, **kwargs):
        temperature = kwargs.get("temperature")
        if temperature is not None:
            await self.coordinator.set_temperature(type("ServiceCall", (), {"data": {"temperature": temperature}})())

    @property
    def hvac_mode(self):
        return HVACMode.HEAT if self.coordinator._last_data.get("heater") == "on" else HVACMode.OFF

    async def async_set_hvac_mode(self, hvac_mode):
        if hvac_mode == HVACMode.HEAT:
            await self.coordinator.set_feature("heater", "on")
        elif hvac_mode == HVACMode.OFF:
            await self.coordinator.set_feature("heater", "off")