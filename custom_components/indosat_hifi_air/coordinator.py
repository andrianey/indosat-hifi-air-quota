"""DataUpdateCoordinator for Indosat HiFi Air."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import IndosatAPIError, IndosatHifiAirAPI
from .const import DEFAULT_NAME, DOMAIN, SCAN_INTERVAL_OPTIONS

_LOGGER = logging.getLogger(__name__)


class IndosatHifiAirCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch Indosat HiFi Air quota data."""

    def __init__(
        self,
        hass: HomeAssistant,
        phone: str,
        name: str,
        scan_interval_key: str,
    ) -> None:
        """Initialize the coordinator."""
        self.phone = phone
        self.name = name
        interval_minutes = SCAN_INTERVAL_OPTIONS.get(scan_interval_key, 60)
        self.api = IndosatHifiAirAPI(session=async_get_clientsession(hass))
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DEFAULT_NAME} {name}",
            update_interval=timedelta(minutes=interval_minutes),
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from API."""
        try:
            data = await self.api.get_quota_data(self.phone)
        except IndosatAPIError as err:
            raise UpdateFailed(err) from err
        return data

