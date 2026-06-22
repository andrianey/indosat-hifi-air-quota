"""Sensor platform for Indosat HiFi Air."""

from __future__ import annotations

from datetime import date

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfInformation
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import IndosatHifiAirCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from a config entry."""
    coordinator: IndosatHifiAirCoordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        IndosatQuotaSensor(coordinator, "remaining_quota", "Remaining Quota", UnitOfInformation.GIGABYTES, SensorStateClass.MEASUREMENT),
        IndosatQuotaSensor(coordinator, "total_quota", "Total Quota", UnitOfInformation.GIGABYTES),
        IndosatQuotaSensor(coordinator, "used_quota", "Used Quota", UnitOfInformation.GIGABYTES, SensorStateClass.MEASUREMENT),
        IndosatQuotaSensor(coordinator, "remaining_days", "Remaining Days", "d", SensorStateClass.MEASUREMENT),
        IndosatQuotaSensor(coordinator, "expiry_date", "Expiry Date", None),
        IndosatQuotaSensor(coordinator, "account_status", "Account Status", None),
        IndosatQuotaSensor(coordinator, "package_name", "Package Name", None),
    ]
    async_add_entities(sensors)


class IndosatQuotaSensor(CoordinatorEntity, SensorEntity):
    """Indosat HiFi Air quota sensor."""

    def __init__(
        self,
        coordinator: IndosatHifiAirCoordinator,
        key: str,
        name: str,
        unit: str | None,
        state_class: SensorStateClass | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key = key
        self._attr_name = f"{coordinator.name} {name}"
        self._attr_unique_id = f"{coordinator.phone}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = state_class

    @property
    def native_value(self) -> str | float | None:
        """Return the sensor value."""
        data = self.coordinator.data
        if not data:
            return None

        if self._key == "remaining_quota":
            account = data.get("accountInfo", {})
            val = account.get("totalDataBalance")
            try:
                return float(val)
            except (TypeError, ValueError):
                return val
        if self._key == "total_quota":
            pkgs = data.get("packages", [])
            if pkgs:
                val = pkgs[0].get("packageInitialQuota")
                try:
                    return float(val)
                except (TypeError, ValueError):
                    return val
            return None
        if self._key == "used_quota":
            pkgs = data.get("packages", [])
            if pkgs:
                initial = pkgs[0].get("packageInitialQuota")
                remaining = pkgs[0].get("packageRemainingQuota")
                try:
                    return round(float(initial) - float(remaining), 2)
                except (TypeError, ValueError):
                    return None
            return None
        if self._key == "remaining_days":
            account = data.get("accountInfo", {})
            raw = account.get("expiryDate")
            if raw and len(raw) == 8:
                try:
                    expiry = date(int(raw[:4]), int(raw[4:6]), int(raw[6:]))
                    delta = (expiry - date.today()).days
                    return delta if delta >= 0 else 0
                except (TypeError, ValueError):
                    return None
            return None
        if self._key == "expiry_date":
            account = data.get("accountInfo", {})
            raw = account.get("expiryDate")
            if raw and len(raw) == 8:
                return f"{raw[:4]}-{raw[4:6]}-{raw[6:]}"
            return raw
        if self._key == "account_status":
            account = data.get("accountInfo", {})
            return account.get("accountStatus")
        if self._key == "package_name":
            pkgs = data.get("packages", [])
            if pkgs:
                return pkgs[0].get("packageName")
            return None
        return None

    @property
    def device_info(self) -> dict:
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.phone)},
            "name": self.coordinator.name,
            "manufacturer": "Indosat",
            "model": "HiFi Air",
        }

