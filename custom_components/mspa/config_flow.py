"""Config flow for MSpa Hot Tub integration."""
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, CONF_DEVICE_ID
from .const import (
    DOMAIN, 
    CONF_PRODUCT_ID,
    CONF_REGION,
    DEFAULT_REGION,
    REGIONS,
    COUNTRY_TO_REGION,
    DEFAULT_PUMP_POWER,
    DEFAULT_BUBBLE_POWER,
    DEFAULT_HEATER_POWER_PREHEAT,
    DEFAULT_HEATER_POWER_HEAT
)
import hashlib

_LOGGER = logging.getLogger(__name__)

from typing import Any, Dict, Tuple, Optional

def detect_region_from_hass(hass) -> Tuple[str, Optional[str]]:
    """Detect region based on Home Assistant country/timezone with fallback to ROW.
    
    Returns:
        Tuple of (region, country_code) where country_code is None if not detected
    """
    # Try to get country from Home Assistant config
    try:
        country = hass.config.country
        if country:
            region = COUNTRY_TO_REGION.get(country, DEFAULT_REGION)
            _LOGGER.info(f"Auto-detected region '{region}' based on country '{country}'")
            return region, country
    except Exception as e:
        _LOGGER.debug(f"Could not detect country: {e}")
    
    # Safe fallback to ROW (Europe) for maximum compatibility
    _LOGGER.info("Using default region 'ROW' (Europe/Rest of World)")
    return DEFAULT_REGION, None

class MSpaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MSpa Hot Tub."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None ) :
        """Handle the initial step."""
        errors = {}
        
        # Auto-detect region based on HA country setting for smart default
        detected_region, detected_country = detect_region_from_hass(self.hass)
        
        # Build description for the form
        if detected_country:
            description_placeholders = {
                "detected_info": f"Auto-detected from your Home Assistant country setting ({detected_country}): {REGIONS[detected_region]}"
            }
        else:
            description_placeholders = {
                "detected_info": "No country detected, defaulting to Europe/Rest of World for maximum compatibility"
            }

        if user_input is not None:
            # Strip whitespace from email and password to prevent common user errors
            # (trailing spaces from copy/paste, etc.)
            email = user_input[CONF_EMAIL].strip()
            password = user_input[CONF_PASSWORD].strip()

            # Obfuscate for logging
            email_parts = email.split("@")
            obfuscated_email = f"{email_parts[0][:3]}***@{email_parts[1]}" if len(email_parts) == 2 else "***"

            # Check for whitespace that was removed
            if len(user_input[CONF_EMAIL]) != len(email):
                _LOGGER.warning("DIAGNOSTIC: Email had leading/trailing whitespace - removed %d characters",
                               len(user_input[CONF_EMAIL]) - len(email))
            if len(user_input[CONF_PASSWORD]) != len(password):
                _LOGGER.warning("DIAGNOSTIC: Password had leading/trailing whitespace - removed %d characters",
                               len(user_input[CONF_PASSWORD]) - len(password))

            _LOGGER.debug("User input: {'email': '%s', 'password': '%s'}", obfuscated_email, "*" * len(password))

            # Generate MD5 hash
            password_hash = hashlib.md5(password.encode("utf-8")).hexdigest()
            _LOGGER.info("DIAGNOSTIC: Generated MD5 hash length: %d, first 6 chars: %s", len(password_hash), password_hash[:6])
            _LOGGER.info("DIAGNOSTIC: Original password length: %d", len(password))
            
            # Get region from user input, or use detected region if not specified
            region = user_input.get(CONF_REGION, detected_region)
            
            _LOGGER.info(f"Using region: {region} (detected: {detected_region}, user selected: {user_input.get(CONF_REGION)})")$

            return self.async_create_entry(
                title="MSpa Hot Tub",
                data={
                    "account_email": email,
                    "password": password_hash,
                    "region": region,
                    # "device_id": user_input[CONF_DEVICE_ID],
                    # "product_id": user_input[CONF_PRODUCT_ID],
                }
            )

        # Pre-populate form with detected region
        data_schema=vol.Schema({
            vol.Required(CONF_EMAIL): str,
            vol.Required(CONF_PASSWORD): str,
            vol.Optional(CONF_REGION, default=detected_region, description={"suggested_value": detected_region}): vol.In(REGIONS),
            # vol.Required(CONF_DEVICE_ID): str,
            # vol.Required(CONF_PRODUCT_ID): str,
        })
        return self.async_show_form(
            step_id="user", 
            data_schema=data_schema, 
            errors=errors,
            description_placeholders=description_placeholders
        )

    # Hook the options flow for per-device settings
    @staticmethod
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow for per-device power consumption settings."""

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            # Save options and return
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema({
            vol.Optional(
                "pump_power",
                default=self.config_entry.options.get("pump_power", DEFAULT_PUMP_POWER),
            ): vol.All(int, vol.Range(min=0)),
            vol.Optional(
                "bubble_power",
                default=self.config_entry.options.get("bubble_power", DEFAULT_BUBBLE_POWER),
            ): vol.All(int, vol.Range(min=0)),
            vol.Optional(
                "heater_power_preheat",
                default=self.config_entry.options.get("heater_power_preheat", DEFAULT_HEATER_POWER_PREHEAT),
            ): vol.All(int, vol.Range(min=0)),
            vol.Optional(
                "heater_power_heat",
                default=self.config_entry.options.get("heater_power_heat", DEFAULT_HEATER_POWER_HEAT),
            ): vol.All(int, vol.Range(min=0)),
        })

        return self.async_show_form(step_id="init", data_schema=data_schema)