# Testing Guide for LinqConnect Integration

## Quick Start - Test API Without Home Assistant

The fastest way to test if the integration is working:

```bash
cd /Users/coltonshaw/development/linqconnect

# Install dependencies (if needed)
pip3 install aiohttp

# Run the test script
python3 test_api.py
```

This will:
- ✅ Test the API connection
- ✅ Fetch and parse menu data
- ✅ Show you exactly what data is being processed
- ✅ Save the raw API response to `test_response.json`
- ✅ Test date lookups for today and tomorrow

### Expected Output

You should see something like:

```
================================================================================
LinqConnect API Test
================================================================================

📅 Date Range: 10-21-2025 to 11-20-2025
🔗 API URL: https://api.linqconnect.com/api/FamilyMenu
🏫 Building ID: b812a68d-5ed4-eb11-a2c4-87353d5bc03e
🏛️  District ID: 8571dba1-79cf-eb11-a2c4-f81ec5475527

🌐 Fetching data from API...
✅ Status Code: 200
💾 Raw response saved to test_response.json

================================================================================
Processing Menu Data
================================================================================

📦 Found 2 menu sessions

🔍 Processing session: Breakfast
   📋 Found 2 menu plans
   📅 Menu Plan: K-12 Breakfast SY 25-26 (30 days)

📊 Breakfast days found: 20
📊 Lunch days found: 20

🍳 Sample Breakfast Data:
   📅 Date: 2025-10-21
   🎯 Theme: Week 3 Tuesday
   📋 Menu Plan: K-12 Breakfast SY 25-26
   🍽️  Menu Items:
      • Main Entrée: Yogurt Cup with Granola, Pumpkin Bread
      • Fruit: Apple Slices
      ... and more
```

## Full Test Suite with Pytest

### Setup

```bash
cd /Users/coltonshaw/development/linqconnect

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dev dependencies
pip install -r requirements-dev.txt
```

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=custom_components.linqconnect --cov-report=html

# Run specific test file
pytest tests/test_coordinator.py -v
```

## Testing in Home Assistant Dev Container

For full Home Assistant integration testing:

### 1. Setup Dev Container

```bash
# Clone Home Assistant core
git clone https://github.com/home-assistant/core.git
cd core

# Open in VS Code
code .

# Reopen in Container (VS Code will prompt)
```

### 2. Copy Integration

```bash
# Inside the dev container
cp -r /path/to/linqconnect/custom_components/linqconnect config/custom_components/
```

### 3. Add to Configuration

Edit `config/configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.linqconnect: debug

# The integration will be set up via UI
```

### 4. Start Home Assistant

```bash
# Inside dev container
hass -c config
```

### 5. Configure Integration

1. Open Home Assistant at http://localhost:8123
2. Go to Settings → Devices & Services
3. Add Integration → Search "LinqConnect"
4. Enter your District ID and Building ID

## Manual Testing Checklist

### API Tests
- [ ] Test script runs without errors
- [ ] API returns 200 status code
- [ ] Data is parsed correctly (dates, menus, categories)
- [ ] Both breakfast and lunch data present
- [ ] Today's/tomorrow's menu can be looked up

### Home Assistant Tests
- [ ] Integration loads without errors
- [ ] Config flow completes successfully
- [ ] Sensors created (breakfast and lunch)
- [ ] Calendar entities created
- [ ] Sensors show menu data (not "No menu available")
- [ ] Sensor attributes populated (main_entree, theme_day, etc.)
- [ ] Calendar shows events
- [ ] Smart timing works (cutoff time switches to next day)
- [ ] Options flow works (change cutoff time, update interval)

### Edge Cases
- [ ] Weekend/holiday handling (no menu data)
- [ ] Invalid credentials (district/building ID)
- [ ] API timeout/error handling
- [ ] Empty API response
- [ ] Malformed date strings
- [ ] Missing recipe categories

## Debugging Tips

### Enable Verbose Logging

Add to `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.linqconnect: debug
    custom_components.linqconnect.coordinator: debug
    custom_components.linqconnect.api: debug
    homeassistant.helpers.update_coordinator: debug
```

### Check Raw API Response

```bash
# Test API directly
curl "https://api.linqconnect.com/api/FamilyMenu?buildingId=YOUR_BUILDING_ID&districtId=YOUR_DISTRICT_ID&startDate=10-21-2025&endDate=11-1-2025"
```

### Inspect Coordinator Data

In Home Assistant Developer Tools → Template:

```jinja
{# Check sensor attributes #}
{{ states.sensor.linqconnect_lunch.attributes }}

{# Check specific attribute #}
{{ state_attr('sensor.linqconnect_lunch', 'main_entree') }}

{# Check all linqconnect entities #}
{% for state in states.sensor %}
  {% if 'linqconnect' in state.entity_id %}
    {{ state.entity_id }}: {{ state.state }}
  {% endif %}
{% endfor %}
```

## Common Issues

### Issue: test_api.py fails with import error

**Solution:** Make sure you're in the right directory and have aiohttp installed:
```bash
pip3 install aiohttp
```

### Issue: Dates not parsing

**Check:** The date format in coordinator.py should be `%Y-%m-%d` (YYYY-MM-DD)

### Issue: No menu data in Home Assistant

**Debug:**
1. Run `test_api.py` first to verify API is working
2. Check Home Assistant logs for errors
3. Verify District ID and Building ID are correct
4. Check if it's a weekend (no school menu)

### Issue: pytest can't find modules

**Solution:**
```bash
# Make sure you're in the venv
source venv/bin/activate

# Install in development mode
pip install -e .
```

## Performance Testing

Test API response time:

```bash
time python3 test_api.py
```

Should complete in < 5 seconds typically.

## Continuous Integration

For GitHub Actions, add `.github/workflows/test.yml`:

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements-dev.txt
      - run: pytest tests/ -v --cov
```
