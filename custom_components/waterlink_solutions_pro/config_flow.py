import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD, CONF_SITE_ID
from .api import WaterLinkAPI

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    def __init__(self):
        self.username = None
        self.password = None
        self.api = None
        self.sites = []

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            self.username = user_input[CONF_USERNAME]
            self.password = user_input[CONF_PASSWORD]

            try:
                self.api = WaterLinkAPI(self.username, self.password)
                self.sites = await self.api.get_sites()
                if not self.sites:
                    errors["base"] = "no_sites_found"
                else:
                    return await self.async_step_site()
            except Exception as ex:
                if hasattr(ex, "status_code") and ex.status_code == 401:
                    errors["base"] = "invalid_auth"
                else:
                    errors["base"] = "auth_failed"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }),
            errors=errors,
        )

    async def async_step_site(self, user_input=None):
        errors = {}
        site_options = {
            site["id"]: site["name"] for site in self.sites
        }

        if user_input is not None:
            selected_sites = user_input[CONF_SITE_ID]
            return self.async_create_entry(
                title="WaterLink Sites",
                data={
                    CONF_USERNAME: self.username,
                    CONF_PASSWORD: self.password,
                    CONF_SITE_ID: selected_sites,
                },
            )

        return self.async_show_form(
            step_id="site",
            data_schema=vol.Schema({
                vol.Required(CONF_SITE_ID): vol.All(
                    vol.EnsureList,
                    [vol.In(list(site_options.keys()))]
                )
            }),
            description_placeholders=site_options,
            errors=errors,
        )

