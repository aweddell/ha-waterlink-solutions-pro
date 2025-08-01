import aiohttp
from datetime import datetime, timedelta

AUTH_URL = "https://wls-auth.waterlinkconnect.com/authentication"
API_BASE = "https://wls-api.waterlinkconnect.com"

class WaterLinkAPI:
    def __init__(self, username, password, site_id):
        self._username = username
        self._password = password
        self._site_id = site_id
        self._token = None

    async def authenticate(self):
        payload = {"username": self._username, "password": self._password, "appId": "HomeAssistant"}
        async with aiohttp.ClientSession() as session:
            async with session.post(AUTH_URL, json=payload) as resp:
                data = await resp.json()
                self._token = data["jwt"]

    async def _get_headers(self):
        if not self._token:
            await self.authenticate()
        return {"Authorization": f"Bearer {self._token}"}

    async def get_test_factors(self):
        headers = await self._get_headers()
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(f"{API_BASE}/sites/{self._site_id}/test-factors") as resp:
                return await resp.json()

    async def get_test_results(self):
        headers = await self._get_headers()
        now = datetime.utcnow()
        start = (now - timedelta(days=14)).isoformat() + "Z"
        end = now.isoformat() + "Z"
        payload = {"startDate": start, "endDate": end, "siteId": self._site_id}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(f"{API_BASE}/treatment-reports/grid-view/search", json=payload) as resp:
                return await resp.json()
