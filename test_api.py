#!/usr/bin/env python3
"""
Standalone test script for LinqConnect API.
Run this to test the API and data parsing without Home Assistant.
"""
import asyncio
import aiohttp
from datetime import datetime, timedelta
import json
import sys

# Your credentials
DISTRICT_ID = "8571dba1-79cf-eb11-a2c4-f81ec5475527"
BUILDING_ID = "b812a68d-5ed4-eb11-a2c4-87353d5bc03e"
API_URL = "https://api.linqconnect.com/api/FamilyMenu"


async def test_api():
    """Test the API and data parsing."""
    print("=" * 80)
    print("LinqConnect API Test")
    print("=" * 80)

    # Calculate date range
    start_date = datetime.now()
    end_date = start_date + timedelta(days=30)

    params = {
        "districtId": DISTRICT_ID,
        "buildingId": BUILDING_ID,
        "startDate": start_date.strftime("%-m-%-d-%Y"),
        "endDate": end_date.strftime("%-m-%-d-%Y"),
    }

    print(f"\n📅 Date Range: {params['startDate']} to {params['endDate']}")
    print(f"🔗 API URL: {API_URL}")
    print(f"🏫 Building ID: {BUILDING_ID}")
    print(f"🏛️  District ID: {DISTRICT_ID}")

    async with aiohttp.ClientSession() as session:
        try:
            print("\n🌐 Fetching data from API...")
            async with session.get(API_URL, params=params) as response:
                print(f"✅ Status Code: {response.status}")

                if response.status != 200:
                    print(f"❌ Error: HTTP {response.status}")
                    return

                data = await response.json()

                # Save raw response for inspection
                with open("/Users/coltonshaw/development/linqconnect/test_response.json", "w") as f:
                    json.dump(data, f, indent=2)
                print("💾 Raw response saved to test_response.json")

                # Process the data like the coordinator does
                print("\n" + "=" * 80)
                print("Processing Menu Data")
                print("=" * 80)

                processed = process_menu_data(data)

                # Display results
                print(f"\n📊 Breakfast days found: {len(processed['breakfast'])}")
                print(f"📊 Lunch days found: {len(processed['lunch'])}")

                # Show some sample data
                if processed['breakfast']:
                    print("\n🍳 Sample Breakfast Data:")
                    show_sample_menu(processed['breakfast'], "breakfast")

                if processed['lunch']:
                    print("\n🍕 Sample Lunch Data:")
                    show_sample_menu(processed['lunch'], "lunch")

                # Test specific date lookup (today/tomorrow)
                print("\n" + "=" * 80)
                print("Testing Date Lookup")
                print("=" * 80)

                today = datetime.now().date()
                tomorrow = today + timedelta(days=1)

                print(f"\n📅 Today ({today}):")
                test_date_lookup(processed, today)

                print(f"\n📅 Tomorrow ({tomorrow}):")
                test_date_lookup(processed, tomorrow)

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()


def process_menu_data(raw_data):
    """Process raw API data - same logic as coordinator."""
    processed = {
        "breakfast": {},
        "lunch": {},
    }

    if not raw_data or "FamilyMenuSessions" not in raw_data:
        print("⚠️  No FamilyMenuSessions found in response")
        return processed

    print(f"\n📦 Found {len(raw_data['FamilyMenuSessions'])} menu sessions")

    for session in raw_data["FamilyMenuSessions"]:
        session_name = session.get("ServingSession", "").lower()
        print(f"\n🔍 Processing session: {session.get('ServingSession')}")

        # Determine meal type
        if "breakfast" in session_name:
            meal_type = "breakfast"
        elif "lunch" in session_name:
            meal_type = "lunch"
        else:
            print(f"   ⚠️  Skipping unknown session type: {session_name}")
            continue

        # Process menu plans
        menu_plans = session.get("MenuPlans", [])
        print(f"   📋 Found {len(menu_plans)} menu plans")

        for menu_plan in menu_plans:
            menu_plan_name = menu_plan.get("MenuPlanName", "Unknown")
            days = menu_plan.get("Days", [])
            print(f"   📅 Menu Plan: {menu_plan_name} ({len(days)} days)")

            # Process each day
            for day in days:
                date_str = day.get("Date")
                if not date_str:
                    continue

                # Parse the date (format: M/D/YYYY)
                try:
                    date_obj = datetime.strptime(date_str, "%m/%d/%Y").date()
                except ValueError as e:
                    print(f"   ❌ Could not parse date: {date_str} - {e}")
                    continue

                # Process menu meals
                menu_items = []
                theme_day = None

                for menu_meal in day.get("MenuMeals", []):
                    meal_name = menu_meal.get("MenuMealName")
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
                            }
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


def show_sample_menu(meal_data, meal_type):
    """Show a sample menu entry."""
    # Get first date
    dates = sorted(meal_data.keys())
    if not dates:
        print("   ❌ No dates found")
        return

    sample_date = dates[0]
    menu = meal_data[sample_date]

    print(f"   📅 Date: {sample_date}")
    print(f"   🎯 Theme: {menu.get('theme', 'None')}")
    print(f"   📋 Menu Plan: {menu.get('menu_plan', 'Unknown')}")

    items = menu.get("items", [])
    if items:
        print(f"   🍽️  Menu Items:")
        for item in items[:1]:  # Just show first item
            for category_name, recipes in item.items():
                recipe_names = [r["name"] for r in recipes if r.get("name")]
                print(f"      • {category_name}: {', '.join(recipe_names[:3])}")
                if len(recipe_names) > 3:
                    print(f"        ... and {len(recipe_names) - 3} more")


def test_date_lookup(processed, target_date):
    """Test looking up a specific date."""
    breakfast = processed["breakfast"].get(target_date)
    lunch = processed["lunch"].get(target_date)

    if breakfast:
        print(f"   🍳 Breakfast: {breakfast.get('theme', 'Menu Available')}")
        items = breakfast.get("items", [])
        if items:
            for item in items[:1]:
                if "Main Entrée" in item:
                    entrees = [r["name"] for r in item["Main Entrée"]]
                    print(f"      Main: {', '.join(entrees)}")
    else:
        print("   🍳 Breakfast: No menu available")

    if lunch:
        print(f"   🍕 Lunch: {lunch.get('theme', 'Menu Available')}")
        items = lunch.get("items", [])
        if items:
            for item in items[:1]:
                if "Main Entrée" in item:
                    entrees = [r["name"] for r in item["Main Entrée"]]
                    print(f"      Main: {', '.join(entrees)}")
    else:
        print("   🍕 Lunch: No menu available")


if __name__ == "__main__":
    asyncio.run(test_api())
