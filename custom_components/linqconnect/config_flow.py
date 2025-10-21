"""Config flow for LinqConnect integration."""
from __future__ import annotations

from datetime import time
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .api import ApiClientError, LinqConnectApiClient
from .const import (
    CONF_BUILDING_ID,
    CONF_CALENDAR_DAYS,
    CONF_CUTOFF_TIME,
    CONF_DISTRICT_ID,
    CONF_UPDATE_INTERVAL,
    DEFAULT_CALENDAR_DAYS,
    DEFAULT_CUTOFF_TIME,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DISTRICT_ID): str,
        vol.Required(CONF_BUILDING_ID): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    session = async_get_clientsession(hass)
    client = LinqConnectApiClient(
        district_id=data[CONF_DISTRICT_ID],
        building_id=data[CONF_BUILDING_ID],
        session=session,
    )

    if not await client.async_validate_credentials():
        raise InvalidAuth

    return {"title": "LinqConnect School Menus"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for LinqConnect."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for the integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Get current options with defaults
        current_cutoff = self.config_entry.options.get(
            CONF_CUTOFF_TIME, DEFAULT_CUTOFF_TIME
        )
        if isinstance(current_cutoff, str):
            try:
                hour, minute = current_cutoff.split(":")
                current_cutoff = time(int(hour), int(minute))
            except (ValueError, AttributeError):
                current_cutoff = DEFAULT_CUTOFF_TIME

        options_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_CUTOFF_TIME,
                    default=current_cutoff.strftime("%H:%M")
                    if isinstance(current_cutoff, time)
                    else str(current_cutoff),
                ): str,
                vol.Optional(
                    CONF_UPDATE_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                    ),
                ): cv.positive_int,
                vol.Optional(
                    CONF_CALENDAR_DAYS,
                    default=self.config_entry.options.get(
                        CONF_CALENDAR_DAYS, DEFAULT_CALENDAR_DAYS
                    ),
                ): cv.positive_int,
            }
        )

        return self.async_show_form(step_id="init", data_schema=options_schema)


class InvalidAuth(Exception):
    """Error to indicate there is invalid auth."""
