"""Constants for the MSpa Hot Tub integration."""
from homeassistant.const import  UnitOfTemperature

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

# Default values
TEMP_UNIT = UnitOfTemperature.CELSIUS
MAX_TEMP = 40
MIN_TEMP = 20