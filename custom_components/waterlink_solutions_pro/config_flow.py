import voluptuous as vol
import logging
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD, CONF_SITE_ID
from .api import WaterLinkAPI

_LOGGER = logging.getLogger(__name__)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    def __init__(self):
        self.username = None
        self.password = None
        self.api = None
        self.sites = []

    async def async_step_user(self, user_input=None):
        errors = {}
        _LOGGER.debug("Starting async_step_user with input: %s", user_input)

        if user_input is not None:
            self.username = user_input[CONF_USERNAME]
            self.password = user_input[CONF_PASSWORD]
            _LOGGER.debug("Attempting login for user: %s", self.username)

            try:
                self.api = WaterLinkAPI(self.username, self.password, None)
                await self.api.authenticate()
                if not self.api._token:
                    _LOGGER.warning("Authentication succeeded but no token returned.")
                    errors["base"] = "invalid_auth"
                    return self.async_show_form(
                        step_id="user",
                        data_schema=vol.Schema({
                            vol.Required(CONF_USERNAME): str,
                            vol.Required(CONF_PASSWORD): str,
                        }),
                        errors=errors,
                    )
                _LOGGER.debug("Authentication successful for user: %s", self.username)
            except Exception as ex:
                _LOGGER.exception("Authentication failed: %s", ex)
                errors["base"] = "invalid_auth"
                return self.async_show_form(
                    step_id="user",
                    data_schema=vol.Schema({
                        vol.Required(CONF_USERNAME): str,
                        vol.Required(CONF_PASSWORD): str,
                    }),
                    errors=errors,
                )

            try:
                self.sites = await self.api.get_sites()
                if not self.sites:
                    _LOGGER.warning("Authentication succeeded but no sites returned.")
                    errors["base"] = "no_sites_found"
                else:
                    _LOGGER.debug("Retrieved %d sites", len(self.sites))
                    return self.async_create_entry(
                        title="WaterLink Sites",
                        data={
                            CONF_USERNAME: self.username,
                            CONF_PASSWORD: self.password,
                            CONF_SITE_ID: [site["id"] for site in self.sites],
                        },
                    )
            except Exception as ex:
                _LOGGER.exception("Failed to retrieve site list: %s", ex)
                errors["base"] = "site_fetch_error"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }),
            errors=errors,
        )
