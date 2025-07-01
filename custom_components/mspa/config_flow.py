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
            _LOGGER.debug("User input: %s", user_input)
            return self.async_create_entry(
                title="MSpa Hot Tub",
                data={
                    "account_email": user_input[CONF_EMAIL],
                    "password": hashlib.md5(user_input[CONF_PASSWORD].encode("utf-8")).hexdigest(),
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

