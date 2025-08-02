import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD, CONF_SITE_ID
from .api import WaterLinkAPI
from .coordinator import WaterLinkDataCoordinator

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up WaterLink Solutions Pro from a config entry."""
    _LOGGER.debug("Setting up WaterLink Solutions Pro integration")

    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    site_ids = entry.data[CONF_SITE_ID]
    if isinstance(site_ids, str):
        site_ids = [site_ids]  # backward compatibility

    coordinators = {}
    for site_id in site_ids:
        api = WaterLinkAPI(username, password, site_id)
        coordinator = WaterLinkDataCoordinator(hass, api, site_id)
        await coordinator.async_config_entry_first_refresh()
        coordinators[site_id] = coordinator

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinators

    async def handle_manual_refresh(call):
        for coordinator in coordinators.values():
            await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN, "refresh", handle_manual_refresh
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded

