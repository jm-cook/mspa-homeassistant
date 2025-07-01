from homeassistant.helpers.entity import Entity
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

class MSpaEntity(Entity):
    def __init__(self, coordinator):
        self.coordinator = coordinator

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "mspa_hottub")},
            "name": f"MSpa Hot Tub {getattr(self.coordinator, 'series', 'unknown')} series",
            "manufacturer": "MSpa",
            "model": getattr(self.coordinator, "model", None),
            "sw_version": getattr(self.coordinator, "software_version", "unknown"),
        }