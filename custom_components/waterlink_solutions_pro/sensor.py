from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        WaterLinkSensor(coordinator, factor)
        for factor in coordinator.data
    ])

class WaterLinkSensor(SensorEntity):
    def __init__(self, coordinator, factor):
        self.coordinator = coordinator
        self._attr_name = f"WaterLink: {factor}"
        self._factor = factor

    @property
    def native_value(self):
        return self.coordinator.data[self._factor]["value"]

    @property
    def native_unit_of_measurement(self):
        return self.coordinator.data[self._factor].get("unitOfMeasure")
