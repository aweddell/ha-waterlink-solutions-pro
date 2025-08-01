from .const import DOMAIN
from .api import WaterLinkAPI
from .coordinator import WaterLinkDataCoordinator
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry):
    _LOGGER.debug("Setting up WaterLink Solutions Pro integration")
    api = WaterLinkAPI(
        entry.data["username"],
        entry.data["password"],
        entry.data["site_id"]
    )
    coordinator = WaterLinkDataCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()
    _LOGGER.debug("Coordinator initial data: %s", coordinator.data)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass, entry):
    await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    hass.data[DOMAIN].pop(entry.entry_id)
    return True

