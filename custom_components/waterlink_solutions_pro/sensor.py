from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    latest_test = max((d.get("_test_time") for d in coordinator.data.values() if d.get("_test_time")), default=None)

    entities = [
        WaterLinkSensor(coordinator, factor, data)
        for factor, data in coordinator.data.items()
    ]

    if latest_test:
        entities.append(LastTestTimeSensor(
            coordinator.api._site_id,
            latest_test,
            next(iter(coordinator.data.values()), {})
        ))

    async_add_entities(entities)

class WaterLinkSensor(SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, factor, measurement):
        self.coordinator = coordinator
        self._attr_name = factor
        self._attr_unique_id = f"waterlink_{factor.lower().replace(' ', '_')}"
        self._factor = factor
        self._measurement = measurement
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.api._site_id)},
            name=measurement.get("_site_name", coordinator.api._site_id),
            manufacturer="LaMotte",
            model="SpinTouch",
            configuration_url="https://solutions.waterlinkconnect.com/"
        )

    @property
    def native_value(self):
        return self._measurement["value"]

    @property
    def native_unit_of_measurement(self):
        return self._measurement.get("unitOfMeasure")

    @property
    def extra_state_attributes(self):
        site_name = self._measurement.get("_site_name", self.coordinator.api._site_id)
        attrs = {
            "last_test_time": self._measurement.get("_test_time") or "unknown",
            "input_source": self._measurement.get("inputSource"),
            "input_meter_id": self._measurement.get("inputMeterId"),
            "tags": self._measurement.get("tags", []),
            "site_name": site_name,
            "site_id": self.coordinator.api._site_id
        }
        ideal = self._measurement.get("idealRange")
        if ideal:
            attrs["ideal_min"] = ideal.get("minimum")
            attrs["ideal_target"] = ideal.get("target")
            attrs["ideal_max"] = ideal.get("maximum")
        return attrs

class LastTestTimeSensor(SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, site_id, test_time, any_measurement):
        self._attr_name = "Last Water Test"
        self._attr_unique_id = f"waterlink_{site_id}_last_test"
        self._test_time = test_time
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, site_id)},
            name=any_measurement.get("_site_name", site_id),
            manufacturer="LaMotte",
            model="SpinTouch",
            configuration_url="https://solutions.waterlinkconnect.com/"
        )

    @property
    def native_value(self):
        return self._test_time

    @property
    def extra_state_attributes(self):
        return {"site_id": self._attr_unique_id}
