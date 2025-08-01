from .const import DOMAIN
from .api import WaterLinkAPI
from .coordinator import WaterLinkDataCoordinator

async def async_setup_entry(hass, entry):
    api = WaterLinkAPI(
        entry.data["username"],
        entry.data["password"],
        entry.data["site_id"]
    )
    coordinator = WaterLinkDataCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    hass.config_entries.async_setup_platforms(entry, ["sensor"])
    return True

async def async_unload_entry(hass, entry):
    await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
