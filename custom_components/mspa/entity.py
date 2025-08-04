from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.climate import ClimateEntity

from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

class MSpaBaseEntity:
    _attr_has_entity_name = True

    def __init__(self, coordinator):
        import logging
        _LOGGER = logging.getLogger(__name__)
        _LOGGER.debug("Initializing %s", self.__class__.__name__)
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._attr_name = f"mspa {self.name}".strip()
        _LOGGER.debug("internal name set to: %s", self._attr_name)

    @property
    def device_info(self):
        name = f"MSpa {getattr(self.coordinator, 'series', 'unknown')} {getattr(self.coordinator, 'device_alias', getattr(self.coordinator, 'model', 'unknown model'))}"
        return {
            "identifiers": {(DOMAIN, "mspa_hottub")},
            "manufacturer": "MSpa",
            "model": getattr(self.coordinator, "model", None),
            "name": name,
            "sw_version": getattr(self.coordinator, "software_version", "unknown"),
        }

    @property
    def entity_picture(self):
        return getattr(self.coordinator, "product_pic_url", None)


class MSpaSensorEntity(MSpaBaseEntity, CoordinatorEntity, SensorEntity):
    pass

class MSpaClimateEntity(MSpaBaseEntity, CoordinatorEntity, ClimateEntity):
    pass

class MSpaBinarySensorEntity(MSpaBaseEntity, CoordinatorEntity, BinarySensorEntity):
    pass

class MSpaSwitchEntity(MSpaBaseEntity, CoordinatorEntity, SwitchEntity):
    pass

class MSpaNumberEntity(MSpaBaseEntity, CoordinatorEntity, NumberEntity):
    pass