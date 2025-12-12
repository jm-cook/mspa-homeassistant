from homeassistant.components.select import SelectEntity
from .const import DOMAIN
from .entity import MSpaBaseEntity
from .coordinator import MSpaUpdateCoordinator
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the MSpa select entities."""
    coordinator: MSpaUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        MSpaTemperatureUnitSelect(coordinator)
    ]
    async_add_entities(entities, update_before_add=True)


class MSpaSelectEntity(MSpaBaseEntity, CoordinatorEntity, SelectEntity):
    """Base class for MSpa select entities."""
    pass


class MSpaTemperatureUnitSelect(MSpaSelectEntity):
    """Select entity to choose between Celsius and Fahrenheit."""
    
    name = "Temperature Unit"
    _attr_options = ["Celsius", "Fahrenheit"]
    
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_icon = "mdi:thermometer"
        self._attr_unique_id = f"mspa_temperature_unit_{getattr(coordinator, 'device_id', 'unknown')}"
        _LOGGER.debug("MSpaTemperatureUnitSelect initialized")

    @property
    def current_option(self) -> str:
        """Return the currently selected option."""
        unit = self.coordinator.last_data.get("temperature_unit", 0)
        return "Fahrenheit" if unit == 1 else "Celsius"

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        unit = 1 if option == "Fahrenheit" else 0
        _LOGGER.debug(f"Setting temperature unit to {option} ({unit})")
        await self.coordinator.set_temperature_unit(unit)
