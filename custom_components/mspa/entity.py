from homeassistant.helpers.entity import Entity
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

class MSpaEntity(Entity):
    _attr_has_entity_name = True

    def __init__(self, coordinator):
        _LOGGER.debug("Initializing %s", self.__class__.__name__)
        self.coordinator = coordinator
        # Set a separate internal name for the entity
        self._attr_name = f"mspa {self.name}".strip()
        _LOGGER.debug("internal name set to: %s", self._attr_name)

    @property
    def device_info(self):
        name = getattr(self.coordinator, "device_alias", f"MSpa {getattr(self.coordinator, 'series', 'unknown')} {getattr(self.coordinator, 'model', '')}")
        return {
            "identifiers": {(DOMAIN, "mspa_hottub")},
            "manufacturer": "MSpa",
            "model": getattr(self.coordinator, "model", None),
            "name": f"MSpa {getattr(self.coordinator, 'series', 'unknown')} {getattr(self.coordinator, 'model', '')}",
            "sw_version": getattr(self.coordinator, "software_version", "unknown"),
        }

    @property
    def entity_picture(self):
        # Replace with your actual image URL or logic
        return getattr(self.coordinator, "product_pic_url", None)