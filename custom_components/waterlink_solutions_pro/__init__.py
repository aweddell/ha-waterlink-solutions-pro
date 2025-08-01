import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from .const import DOMAIN
from .api import WaterLinkAPI
from .coordinator import WaterLinkDataCoordinator

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the integration (empty for config entry-based)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up WaterLink Solutions Pro from a config entry."""
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

    # Register manual refresh service
    async def handle_manual_refresh(call):
        await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN, "refresh", handle_manual_refresh
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded