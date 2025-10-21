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
    CONF_MENU_PLANS,
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

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._district_id: str | None = None
        self._building_id: str | None = None
        self._available_plans: list[str] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - get credentials."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)

                # Store credentials and fetch available menu plans
                self._district_id = user_input[CONF_DISTRICT_ID]
                self._building_id = user_input[CONF_BUILDING_ID]

                # Fetch available menu plans
                self._available_plans = await self._async_get_available_plans()

                if not self._available_plans:
                    errors["base"] = "no_menu_plans"
                else:
                    # Move to plan selection step
                    return await self.async_step_select_plans()

            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_select_plans(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Let user select which menu plans to track."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Create the config entry with selected plans
            data = {
                CONF_DISTRICT_ID: self._district_id,
                CONF_BUILDING_ID: self._building_id,
                CONF_MENU_PLANS: user_input.get(CONF_MENU_PLANS, []),
            }
            return self.async_create_entry(
                title="LinqConnect School Menus",
                data=data,
            )

        # Build schema with available plans as checkboxes
        # Default to selecting all non-Pre-K plans
        default_plans = [
            plan for plan in self._available_plans
            if "pre-k" not in plan.lower()
        ]

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_MENU_PLANS,
                    default=default_plans,
                ): cv.multi_select(
                    {plan: plan for plan in self._available_plans}
                ),
            }
        )

        return self.async_show_form(
            step_id="select_plans",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "available_plans": ", ".join(self._available_plans)
            },
        )

    async def _async_get_available_plans(self) -> list[str]:
        """Fetch available menu plans from API."""
        try:
            session = async_get_clientsession(self.hass)
            client = LinqConnectApiClient(
                district_id=self._district_id,
                building_id=self._building_id,
                session=session,
            )

            # Fetch menu data
            data = await client.async_get_menu()

            # Extract unique menu plan names
            plans = set()
            for session in data.get("FamilyMenuSessions", []):
                for menu_plan in session.get("MenuPlans", []):
                    plan_name = menu_plan.get("MenuPlanName")
                    if plan_name:
                        plans.add(plan_name)

            return sorted(list(plans))

        except Exception as err:
            _LOGGER.error("Failed to fetch menu plans: %s", err)
            return []

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
        self._available_plans: list[str] = []

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # If menu plans changed, update config entry data (not options)
            if CONF_MENU_PLANS in user_input:
                new_data = {**self.config_entry.data, CONF_MENU_PLANS: user_input.pop(CONF_MENU_PLANS)}
                self.hass.config_entries.async_update_entry(
                    self.config_entry, data=new_data
                )

            return self.async_create_entry(title="", data=user_input)

        # Fetch available menu plans
        self._available_plans = await self._async_get_available_plans()

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

        # Get current selected menu plans
        current_plans = self.config_entry.data.get(CONF_MENU_PLANS, [])

        # Build options schema
        schema_dict = {}

        # Add menu plan selector if plans are available
        if self._available_plans:
            schema_dict[vol.Optional(
                CONF_MENU_PLANS,
                default=current_plans,
            )] = cv.multi_select({plan: plan for plan in self._available_plans})

        schema_dict.update({
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
        })

        options_schema = vol.Schema(schema_dict)

        return self.async_show_form(step_id="init", data_schema=options_schema)

    async def _async_get_available_plans(self) -> list[str]:
        """Fetch available menu plans from API."""
        try:
            session = async_get_clientsession(self.hass)
            client = LinqConnectApiClient(
                district_id=self.config_entry.data[CONF_DISTRICT_ID],
                building_id=self.config_entry.data[CONF_BUILDING_ID],
                session=session,
            )

            data = await client.async_get_menu()

            plans = set()
            for session_data in data.get("FamilyMenuSessions", []):
                for menu_plan in session_data.get("MenuPlans", []):
                    plan_name = menu_plan.get("MenuPlanName")
                    if plan_name:
                        plans.add(plan_name)

            return sorted(list(plans))

        except Exception as err:
            _LOGGER.error("Failed to fetch menu plans in options: %s", err)
            return []


class InvalidAuth(Exception):
    """Error to indicate there is invalid auth."""
