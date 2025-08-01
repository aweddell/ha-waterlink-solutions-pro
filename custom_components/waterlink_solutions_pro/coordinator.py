from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta
import logging
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

class WaterLinkDataCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self):
        try:
            results = await self.api.get_test_results()
            factors = await self.api.get_test_factors()
            factor_map = {f["id"]: f for f in factors.get("requiredTestFactors", []) + factors.get("computedTestFactors", [])}

            data = {}
            for entry in results.get("members", []):
                site_name = entry.get("testedSiteName", "WaterLink Site")
                test_time = entry.get("waterTestDate")
                for m in entry.get("measurements", []):
                    fid = m["testFactorId"]
                    name = factor_map.get(fid, {}).get("name", f"Factor {fid}")
                    m["_site_name"] = site_name
                    m["_test_time"] = test_time
                    data[name] = m
            return data
        except Exception as err:
            raise UpdateFailed(err)
