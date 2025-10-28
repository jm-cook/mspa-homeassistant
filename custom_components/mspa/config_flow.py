"""Config flow for MSpa Hot Tub integration."""
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, CONF_DEVICE_ID
from .const import DOMAIN, CONF_PRODUCT_ID
import hashlib

_LOGGER = logging.getLogger(__name__)

from typing import Any, Dict

class MSpaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MSpa Hot Tub."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None ) :
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate the credentials here
            # For now, we'll just accept them
            # When creating the config entry

            # Obfuscate for logging
            email_parts = user_input[CONF_EMAIL].split("@")
            obfuscated_email = f"{email_parts[0][:3]}***@{email_parts[1]}" if len(email_parts) == 2 else "***"
            _LOGGER.debug("User input: {'email': '%s', 'password': '%s'}", obfuscated_email, "*" * len(user_input[CONF_PASSWORD]))

            # Generate MD5 hash
            password_hash = hashlib.md5(user_input[CONF_PASSWORD].encode("utf-8")).hexdigest()
            _LOGGER.info("DIAGNOSTIC: Generated MD5 hash length: %d, first 6 chars: %s", len(password_hash), password_hash[:6])
            _LOGGER.info("DIAGNOSTIC: Original password length: %d", len(user_input[CONF_PASSWORD]))

            return self.async_create_entry(
                title="MSpa Hot Tub",
                data={
                    "account_email": user_input[CONF_EMAIL],
                    "password": password_hash,
                    # "device_id": user_input[CONF_DEVICE_ID],
                    # "product_id": user_input[CONF_PRODUCT_ID],
                }
            )

        data_schema=vol.Schema({
            vol.Required(CONF_EMAIL): str,
            vol.Required(CONF_PASSWORD): str,
            # vol.Required(CONF_DEVICE_ID): str,
            # vol.Required(CONF_PRODUCT_ID): str,
        })
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

