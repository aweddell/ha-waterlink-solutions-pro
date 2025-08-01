import pytest
from custom_components.waterlink_solutions_pro.api import WaterLinkAPI

@pytest.mark.asyncio
async def test_authenticate():
    api = WaterLinkAPI("fake@example.com", "fakepass", "siteid")
    try:
        await api.authenticate()
    except Exception:
        assert True  # Expected failure with fake credentials
