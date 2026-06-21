"""Config flow for Indosat HiFi Air."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .api import IndosatAPIError, IndosatHifiAirAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({vol.Required("msisdn"): str})


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, str]:
    """Validate the user input by hitting the API."""
    api = IndosatHifiAirAPI()
    try:
        # Full flow: checkaltno + validatecallplan + quota
        await api.get_quota_data(data["msisdn"])
    except IndosatAPIError as err:
        _LOGGER.error("Validation failed: %s", err)
        raise
    finally:
        await api.close()
    return {"title": data["msisdn"]}


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
            if not phone:
                errors["base"] = "invalid_msisdn"
            else:
                await self.async_set_unique_id(phone)
                self._abort_if_unique_id_configured()
                try:
                    info = await validate_input(self.hass, user_input)
                except IndosatAPIError:
                    errors["base"] = "cannot_connect"
                except Exception:  # pylint: disable=broad-except
                    _LOGGER.exception("Unexpected exception")
                    errors["base"] = "unexpected"
                else:
                    return self.async_create_entry(
                        title=info["title"], data=user_input
                    )

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

