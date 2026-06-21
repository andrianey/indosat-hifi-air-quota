"""DataUpdateCoordinator for Indosat HiFi Air."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import IndosatAPIError, IndosatHifiAirAPI
from .const import DEFAULT_NAME, DOMAIN, UPDATE_INTERVAL_MINUTES

_LOGGER = logging.getLogger(__name__)


class IndosatHifiAirCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch Indosat HiFi Air quota data."""

    def __init__(self, hass: HomeAssistant, phone: str) -> None:
        """Initialize the coordinator."""
        self.phone = phone
        self.api = IndosatHifiAirAPI()
        super().__init__(
            hass,
            _LOGGER,
            name=DEFAULT_NAME,
            update_interval=timedelta(minutes=UPDATE_INTERVAL_MINUTES),
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from API."""
        try:
            data = await self.api.get_quota_data(self.phone)
        except IndosatAPIError as err:
            raise UpdateFailed(err) from err
        finally:
            await self.api.close()
        return data

