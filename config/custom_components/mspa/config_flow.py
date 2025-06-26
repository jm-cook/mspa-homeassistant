"""Config flow for MSpa Hot Tub integration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, CONF_DEVICE_ID
from .const import DOMAIN, CONF_PRODUCT_ID

class MSpaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MSpa Hot Tub."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate the credentials here
            # For now, we'll just accept them
            return self.async_create_entry(
                title=user_input[CONF_EMAIL],
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_EMAIL): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Required(CONF_DEVICE_ID): str,
                vol.Required(CONF_PRODUCT_ID): str,
            }),
            errors=errors,
        )