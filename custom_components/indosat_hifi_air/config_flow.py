"""Config flow for Indosat HiFi Air."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import IndosatAPIError, IndosatHifiAirAPI, _normalize_msisdn
from .const import (
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    SCAN_INTERVAL_OPTIONS,
)

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required("msisdn"): str,
        vol.Required("name"): str,
        vol.Required(
            "scan_interval",
            default=DEFAULT_SCAN_INTERVAL,
        ): vol.In({k: f"{v} minutes" for k, v in SCAN_INTERVAL_OPTIONS.items()}),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, str]:
    """Validate the user input by hitting the API."""
    api = IndosatHifiAirAPI(session=async_get_clientsession(hass))
    try:
        await api.get_quota_data(data["msisdn"])
    except IndosatAPIError as err:
        _LOGGER.error("Validation failed: %s", err)
        raise
    finally:
        await api.close()
    return {"title": data["name"]}


class IndosatHifiAirConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Indosat HiFi Air."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            phone = "".join(c for c in user_input["msisdn"] if c.isdigit())
            name = user_input.get("name", "").strip()
            if not phone:
                errors["base"] = "invalid_msisdn"
            elif not name:
                errors["base"] = "invalid_name"
            else:
                normalized = _normalize_msisdn(phone)
                await self.async_set_unique_id(normalized)
                self._abort_if_unique_id_configured()
                try:
                    info = await validate_input(self.hass, user_input)
                except IndosatAPIError:
                    errors["base"] = "cannot_connect"
                except Exception:  # pylint: disable=broad-except
                    _LOGGER.exception("Unexpected exception")
                    errors["base"] = "unexpected"
                else:
                    data = {
                        "msisdn": normalized,
                        "name": name,
                        "scan_interval": user_input.get(
                            "scan_interval", DEFAULT_SCAN_INTERVAL
                        ),
                    }
                    return self.async_create_entry(
                        title=info["title"], data=data
                    )

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return IndosatHifiAirOptionsFlow(config_entry)


class IndosatHifiAirOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Indosat HiFi Air."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema(
            {
                vol.Required(
                    "scan_interval",
                    default=self.config_entry.options.get(
                        "scan_interval",
                        self.config_entry.data.get(
                            "scan_interval", DEFAULT_SCAN_INTERVAL
                        ),
                    ),
                ): vol.In({k: f"{v} minutes" for k, v in SCAN_INTERVAL_OPTIONS.items()}),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
        )

