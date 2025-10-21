"""The LinqConnect School Menus integration."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import LinqConnectApiClient
from .const import (
    CONF_BUILDING_ID,
    CONF_DISTRICT_ID,
    CONF_MENU_PLANS,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)
from .coordinator import LinqConnectDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.CALENDAR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up LinqConnect from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    district_id = entry.data[CONF_DISTRICT_ID]
    building_id = entry.data[CONF_BUILDING_ID]
    selected_menu_plans = entry.data.get(CONF_MENU_PLANS, [])
    update_interval = entry.options.get(
        CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
    )

    session = async_get_clientsession(hass)
    client = LinqConnectApiClient(
        district_id=district_id,
        building_id=building_id,
        session=session,
    )

    coordinator = LinqConnectDataUpdateCoordinator(
        hass,
        client=client,
        update_interval=timedelta(minutes=update_interval),
        selected_menu_plans=selected_menu_plans,
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener for options changes
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    # Register force update service
    async def async_force_update(call):
        """Handle force update service call."""
        _LOGGER.info("Force update requested")
        await coordinator.async_request_refresh()

    hass.services.async_register(DOMAIN, "force_update", async_force_update)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
