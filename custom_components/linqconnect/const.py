"""Constants for the LinqConnect integration."""
from datetime import time

DOMAIN = "linqconnect"

# API Configuration
API_BASE_URL = "https://api.linqconnect.com/api"
API_FAMILY_MENU = f"{API_BASE_URL}/FamilyMenu"
API_FAMILY_MENU_MEALS = f"{API_BASE_URL}/FamilyMenuMeals"

# Configuration Keys
CONF_DISTRICT_ID = "district_id"
CONF_BUILDING_ID = "building_id"
CONF_MENU_PLANS = "menu_plans"
CONF_CUTOFF_TIME = "cutoff_time"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_CALENDAR_DAYS = "calendar_days"

# Defaults
DEFAULT_CUTOFF_TIME = time(10, 0)  # 10:00 AM
DEFAULT_UPDATE_INTERVAL = 180  # 3 hours in minutes
DEFAULT_CALENDAR_DAYS = 30  # Days ahead to fetch

# Sensor Configuration
SENSOR_BREAKFAST = "breakfast"
SENSOR_LUNCH = "lunch"

# Meal Session Keys (from API)
SESSION_BREAKFAST = "Breakfast"
SESSION_LUNCH = "Lunch"

# Recipe Categories
CATEGORY_MAIN_ENTREE = "Main Entrée"
CATEGORY_GRAIN = "Grain"
CATEGORY_VEGETABLE = "Vegetable"
CATEGORY_FRUIT = "Fruit"
CATEGORY_FRUIT_JUICE = "Fruit Juice"
CATEGORY_MILK = "Milk"
CATEGORY_CONDIMENT = "Condiment"
CATEGORY_SIDE_ITEM = "Side Item"

# Attribution
ATTRIBUTION = "Data provided by LinqConnect"
