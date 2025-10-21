"""Tests for the LinqConnect coordinator."""
import pytest
from datetime import datetime, date
from custom_components.linqconnect.coordinator import LinqConnectDataUpdateCoordinator


def test_process_menu_data_with_valid_data():
    """Test processing valid menu data."""
    coordinator = LinqConnectDataUpdateCoordinator(None, None, None)

    raw_data = {
        "FamilyMenuSessions": [
            {
                "ServingSession": "Breakfast",
                "MenuPlans": [
                    {
                        "MenuPlanName": "K-12 Breakfast",
                        "Days": [
                            {
                                "Date": "2025-10-21",
                                "MenuMeals": [
                                    {
                                        "MenuMealName": "Test Tuesday",
                                        "RecipeCategories": [
                                            {
                                                "CategoryName": "Main Entrée",
                                                "Recipes": [
                                                    {
                                                        "RecipeName": "Pancakes",
                                                        "ServingSize": "3 each",
                                                    }
                                                ],
                                            }
                                        ],
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        ]
    }

    processed = coordinator._process_menu_data(raw_data)

    assert "breakfast" in processed
    assert date(2025, 10, 21) in processed["breakfast"]
    menu = processed["breakfast"][date(2025, 10, 21)]
    assert menu["theme"] == "Test Tuesday"
    assert menu["menu_plan"] == "K-12 Breakfast"


def test_process_menu_data_with_empty_response():
    """Test processing empty API response."""
    coordinator = LinqConnectDataUpdateCoordinator(None, None, None)

    processed = coordinator._process_menu_data({})

    assert processed["breakfast"] == {}
    assert processed["lunch"] == {}


def test_date_parsing_format():
    """Test that YYYY-MM-DD format is parsed correctly."""
    coordinator = LinqConnectDataUpdateCoordinator(None, None, None)

    raw_data = {
        "FamilyMenuSessions": [
            {
                "ServingSession": "Lunch",
                "MenuPlans": [
                    {
                        "MenuPlanName": "K-8 Lunch",
                        "Days": [
                            {
                                "Date": "2025-10-21",
                                "MenuMeals": [
                                    {
                                        "RecipeCategories": [
                                            {
                                                "CategoryName": "Main Entrée",
                                                "Recipes": [{"RecipeName": "Pizza"}],
                                            }
                                        ]
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        ]
    }

    processed = coordinator._process_menu_data(raw_data)

    # Should parse the date correctly
    assert date(2025, 10, 21) in processed["lunch"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
