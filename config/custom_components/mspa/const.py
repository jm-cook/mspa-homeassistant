"""Constants for the MSpa Hot Tub integration."""
from homeassistant.const import (
    UnitOfTemperature,
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_DEVICE_ID,
)

DOMAIN = "mspa"
DEFAULT_SCAN_INTERVAL = 60

# Configuration
CONF_PRODUCT_ID = "product_id"

# Services
SERVICE_SET_TEMPERATURE = "set_temperature"
SERVICE_SET_HEATER = "set_heater"
SERVICE_SET_BUBBLE = "set_bubble"
SERVICE_SET_JET = "set_jet"
SERVICE_SET_FILTER = "set_filter"

# Attributes
ATTR_TEMPERATURE = "temperature"
ATTR_STATE = "state"

TEMP_UNIT = UnitOfTemperature.CELSIUS