"""Calendar platform for LinqConnect."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
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
    """Set up LinqConnect calendar based on a config entry."""
    coordinator: LinqConnectDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        LinqConnectCalendar(coordinator, entry, SENSOR_BREAKFAST),
        LinqConnectCalendar(coordinator, entry, SENSOR_LUNCH),
    ]

    async_add_entities(entities)


class LinqConnectCalendar(CoordinatorEntity, CalendarEntity):
    """Calendar entity for school menus."""

    def __init__(
        self,
        coordinator: LinqConnectDataUpdateCoordinator,
        entry: ConfigEntry,
        meal_type: str,
    ) -> None:
        """Initialize the calendar."""
        super().__init__(coordinator)
        self._meal_type = meal_type
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{meal_type}_calendar"
        self._attr_name = f"LinqConnect {meal_type.title()} Calendar"
        self._attr_attribution = ATTRIBUTION

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        events = self._get_events(datetime.now(), datetime.now() + timedelta(days=1))
        if events:
            return events[0]
        return None

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        return self._get_events(start_date, end_date)

    def _get_events(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Get calendar events for the date range."""
        if not self.coordinator.data:
            return []

        events = []
        meal_data = self.coordinator.data.get(self._meal_type, {})

        current_date = start_date.date()
        end_date_only = end_date.date()

        while current_date <= end_date_only:
            menu = meal_data.get(current_date)
            if menu:
                event = self._create_event_from_menu(current_date, menu)
                if event:
                    events.append(event)

            current_date += timedelta(days=1)

        return events

    def _create_event_from_menu(
        self,
        date: datetime.date,
        menu: dict[str, Any],
    ) -> CalendarEvent | None:
        """Create a calendar event from menu data."""
        theme = menu.get("theme", "")
        items = menu.get("items", [])

        if not items:
            return None

        # Build event summary with emoji
        emoji = "🥐" if self._meal_type == SENSOR_BREAKFAST else "🍔"
        if theme:
            summary = f"{emoji} {theme}"
        else:
            summary = f"{emoji} {self._meal_type.title()}"

        # Build clean event description
        description_parts = []

        # Combine all categories from all menu items
        all_categories = {}
        for item in items:
            for category_name, recipes in item.items():
                if category_name not in all_categories:
                    all_categories[category_name] = []
                all_categories[category_name].extend(recipes)

        # Format each category with item limits
        MAX_ITEMS_PER_CATEGORY = 4
        for category_name, recipes in all_categories.items():
            recipe_names = [recipe["name"] for recipe in recipes if recipe.get("name")]
            if recipe_names:
                # Add category header
                description_parts.append(f"{category_name}:")

                # Limit items shown
                if len(recipe_names) > MAX_ITEMS_PER_CATEGORY:
                    shown_items = recipe_names[:MAX_ITEMS_PER_CATEGORY]
                    remaining = len(recipe_names) - MAX_ITEMS_PER_CATEGORY
                    for item in shown_items:
                        description_parts.append(f"  • {item}")
                    description_parts.append(f"  ... and {remaining} more")
                else:
                    for item in recipe_names:
                        description_parts.append(f"  • {item}")

                # Add blank line between categories
                description_parts.append("")

        description = "\n".join(description_parts)

        # Make it an all-day event
        from homeassistant.util import dt as dt_util

        # All-day events need start and end dates (not datetimes)
        start_datetime = dt_util.start_of_local_day(datetime.combine(date, datetime.min.time()))
        end_datetime = dt_util.start_of_local_day(datetime.combine(date + timedelta(days=1), datetime.min.time()))

        return CalendarEvent(
            start=start_datetime.date(),
            end=end_datetime.date(),
            summary=summary,
            description=description,
        )
