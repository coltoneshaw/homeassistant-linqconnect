"""DataUpdateCoordinator for LinqConnect."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import LinqConnectApiClient, ApiClientError
from .const import DOMAIN, SESSION_BREAKFAST, SESSION_LUNCH

_LOGGER = logging.getLogger(__name__)


class LinqConnectDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching LinqConnect data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: LinqConnectApiClient,
        update_interval: timedelta,
    ) -> None:
        """Initialize the coordinator."""
        self.client = client
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        try:
            # Fetch menu data for the configured time range
            raw_data = await self.client.async_get_menu()

            # Process and organize the data
            processed_data = self._process_menu_data(raw_data)

            return processed_data
        except ApiClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    def _process_menu_data(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """Process raw API data into a more usable format."""
        processed = {
            "breakfast": {},
            "lunch": {},
            "raw": raw_data,
        }

        if not raw_data or "FamilyMenuSessions" not in raw_data:
            _LOGGER.warning("No menu data found in API response")
            return processed

        for session in raw_data["FamilyMenuSessions"]:
            session_name = session.get("ServingSessionKey", "").lower()

            # Determine if this is breakfast or lunch
            if SESSION_BREAKFAST.lower() in session_name:
                meal_type = "breakfast"
            elif SESSION_LUNCH.lower() in session_name:
                meal_type = "lunch"
            else:
                continue

            # Process menu plans
            for menu_plan in session.get("MenuPlans", []):
                menu_plan_name = menu_plan.get("MenuPlanName", "Unknown")

                # Process each day
                for day in menu_plan.get("Days", []):
                    date_str = day.get("Date")
                    if not date_str:
                        continue

                    # Parse the date (format: YYYY-MM-DD)
                    try:
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                    except ValueError:
                        _LOGGER.warning("Could not parse date: %s", date_str)
                        continue

                    # Process menu meals for this day
                    menu_items = []
                    theme_day = None

                    for menu_meal in day.get("MenuMeals", []):
                        meal_name = menu_meal.get("Name")
                        if meal_name:
                            theme_day = meal_name

                        # Process recipe categories
                        categories = {}
                        for category in menu_meal.get("RecipeCategories", []):
                            category_name = category.get("CategoryName")
                            if not category_name:
                                continue

                            recipes = []
                            for recipe in category.get("Recipes", []):
                                recipe_info = {
                                    "name": recipe.get("RecipeName"),
                                    "serving_size": recipe.get("ServingSize"),
                                    "identifier": recipe.get("RecipeIdentifier"),
                                }

                                # Add nutritional info if available
                                nutrients = recipe.get("Nutrients", [])
                                if nutrients:
                                    recipe_info["nutrients"] = {
                                        nutrient.get("Name"): nutrient.get("Value")
                                        for nutrient in nutrients
                                    }

                                # Add allergens if available
                                allergens = recipe.get("Allergens", [])
                                if allergens:
                                    recipe_info["allergens"] = allergens

                                recipes.append(recipe_info)

                            if recipes:
                                categories[category_name] = recipes

                        if categories:
                            menu_items.append(categories)

                    # Store processed day data
                    if date_obj not in processed[meal_type]:
                        processed[meal_type][date_obj] = {
                            "theme": theme_day,
                            "menu_plan": menu_plan_name,
                            "items": [],
                        }

                    processed[meal_type][date_obj]["items"].extend(menu_items)

        return processed

    def get_menu_for_date(
        self, meal_type: str, target_date: datetime.date
    ) -> dict[str, Any] | None:
        """Get menu data for a specific date and meal type."""
        if not self.data:
            return None

        meal_data = self.data.get(meal_type, {})
        return meal_data.get(target_date)
