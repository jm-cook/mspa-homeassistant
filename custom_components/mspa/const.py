"""Constants for the MSpa Hot Tub integration."""
from homeassistant.const import  UnitOfTemperature

DOMAIN = "mspa"
DEFAULT_SCAN_INTERVAL = 60
RAPID_SCAN_INTERVAL = 1  # Polling interval in seconds when waiting for changes
RAPID_POLL_TIMEOUT = 15  # Maximum time in seconds to poll rapidly
RAPID_POLL_MAX_ATTEMPTS = 15  # Maximum number of rapid polls

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

# Power consumption defaults (Watts) based on MSpa Comfort model specifications
# These are configurable per-device in the integration options
DEFAULT_PUMP_POWER = 60  # Filter pump: 2000l/t, 60W, 12V
DEFAULT_BUBBLE_POWER = 900  # Bubble generator: 900W (1.2HP)
DEFAULT_HEATER_POWER_PREHEAT = 1500  # Heating element: 1500W (preheat mode)
DEFAULT_HEATER_POWER_HEAT = 2000  # Heating element in active heating (estimated)