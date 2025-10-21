"""Sensor platform for LinqConnect."""
from __future__ import annotations

from datetime import datetime, time, timedelta
import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    CATEGORY_MAIN_ENTREE,
    CONF_CUTOFF_TIME,
    DEFAULT_CUTOFF_TIME,
    DOMAIN,
    SENSOR_BREAKFAST,
    SENSOR_LUNCH,
)
from .coordinator import LinqConnectDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up LinqConnect sensors based on a config entry."""
    coordinator: LinqConnectDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        LinqConnectMenuSensor(coordinator, entry, SENSOR_BREAKFAST),
        LinqConnectMenuSensor(coordinator, entry, SENSOR_LUNCH),
    ]

    async_add_entities(entities)


class LinqConnectMenuSensor(CoordinatorEntity, SensorEntity):
    """Sensor for displaying school menu information."""

    def __init__(
        self,
        coordinator: LinqConnectDataUpdateCoordinator,
        entry: ConfigEntry,
        meal_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._meal_type = meal_type
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{meal_type}"
        self._attr_name = f"LinqConnect {meal_type.title()}"
        self._attr_attribution = ATTRIBUTION

    @property
    def icon(self) -> str:
        """Return the icon for the sensor."""
        if self._meal_type == SENSOR_BREAKFAST:
            return "mdi:food-croissant"
        return "mdi:food"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        menu_data = self._get_relevant_menu()
        if not menu_data:
            return "No menu available"

        theme = menu_data.get("theme")
        if theme:
            return theme

        return "Menu available"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        menu_data = self._get_relevant_menu()
        if not menu_data:
            return {}

        attributes = {
            "menu_plan": menu_data.get("menu_plan"),
            "theme_day": menu_data.get("theme"),
        }

        # Organize items by category
        items = menu_data.get("items", [])
        if items:
            # Combine all categories from all menu items
            all_categories = {}
            for item in items:
                for category_name, recipes in item.items():
                    if category_name not in all_categories:
                        all_categories[category_name] = []
                    all_categories[category_name].extend(recipes)

            # Add each category as an attribute
            for category_name, recipes in all_categories.items():
                # Create a list of recipe names
                recipe_names = [recipe["name"] for recipe in recipes if recipe.get("name")]
                if recipe_names:
                    # Use a sanitized key for the attribute
                    attr_key = category_name.lower().replace(" ", "_").replace("é", "e")
                    attributes[attr_key] = recipe_names

                    # For main entrees, also create a formatted string
                    if category_name == CATEGORY_MAIN_ENTREE:
                        attributes["main_entree_formatted"] = ", ".join(recipe_names)

        return attributes

    def _get_relevant_menu(self) -> dict[str, Any] | None:
        """Get the menu for today or tomorrow based on cutoff time."""
        target_date = self._get_target_date()
        return self.coordinator.get_menu_for_date(self._meal_type, target_date)

    def _get_target_date(self) -> datetime.date:
        """Determine which date's menu to show based on cutoff time."""
        now = datetime.now()
        cutoff_time = self._entry.options.get(CONF_CUTOFF_TIME, DEFAULT_CUTOFF_TIME)

        # Parse cutoff time if it's a string
        if isinstance(cutoff_time, str):
            try:
                hour, minute = cutoff_time.split(":")
                cutoff_time = time(int(hour), int(minute))
            except (ValueError, AttributeError):
                cutoff_time = DEFAULT_CUTOFF_TIME

        # Create a datetime for today's cutoff
        cutoff_datetime = datetime.combine(now.date(), cutoff_time)

        # If we're past the cutoff time, show tomorrow's menu
        if now >= cutoff_datetime:
            target_date = now.date() + timedelta(days=1)
        else:
            target_date = now.date()

        return target_date
