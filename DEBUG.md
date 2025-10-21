# Debugging LinqConnect Integration

## Quick Diagnostics

### 1. Check the Logs

**Settings** → **System** → **Logs**

Look for errors containing:
- `linqconnect`
- `LinqConnect`
- API errors
- Connection errors

### 2. Enable Debug Logging

Add to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.linqconnect: debug
    homeassistant.helpers.update_coordinator: debug
```

Restart Home Assistant and check logs again.

### 3. Check Entity Attributes

**Developer Tools** → **States** → Search for `sensor.linqconnect_breakfast`

Look at the attributes. Even if state is "No menu available", attributes might show:
- Error messages
- Last update time
- Raw data

### 4. Common Issues

#### Issue: "No menu available"

**Possible Causes:**

1. **Wrong Date Range**
   - The API might not have data for today/tomorrow
   - Weekend or holiday
   - Check the calendar entities to see what dates have data

2. **API Call Failing**
   - Check logs for HTTP errors
   - Verify District ID and Building ID are correct
   - Test API manually (see below)

3. **Date Parsing Issue**
   - Check logs for date parsing errors
   - Timezone mismatch

4. **Cutoff Time Logic**
   - Sensor might be looking for tomorrow's menu but it's not available yet
   - Try changing cutoff time in config options

#### Issue: Integration Won't Load

**Check:**
1. Home Assistant version (needs 2024.1.0+)
2. Syntax errors in Python files
3. Missing dependencies

#### Issue: API Errors

**Check:**
1. Internet connectivity
2. LinqConnect API is up
3. Rate limiting (should be rare with 3-hour polling)

### 5. Manual API Testing

Test the API directly using Developer Tools → Template:

```yaml
{% set url = "https://api.linqconnect.com/api/FamilyMenu" %}
{% set params = {
  "districtId": "YOUR_DISTRICT_ID",
  "buildingId": "YOUR_BUILDING_ID",
  "startDate": "10-21-2025",
  "endDate": "10-28-2025"
} %}

Test URL: {{ url }}?districtId={{ params.districtId }}&buildingId={{ params.buildingId }}&startDate={{ params.startDate }}&endDate={{ params.endDate }}
```

Copy that URL and test it in your browser to see if the API returns data.

### 6. Check Coordinator Data

Add this automation to see what data the coordinator has:

```yaml
automation:
  - alias: "Debug LinqConnect Data"
    trigger:
      - platform: time_pattern
        minutes: "/5"
    action:
      - service: system_log.write
        data:
          message: "LinqConnect coordinator data check"
          level: info
```

Then check if the coordinator is updating.

### 7. Configuration Issues

Verify your configuration:

1. Go to **Settings** → **Devices & Services**
2. Find **LinqConnect School Menus**
3. Click on it and verify:
   - District ID is correct (GUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
   - Building ID is correct (same format)
4. Click **Configure** to check options:
   - Cutoff time (default: 10:00)
   - Update interval (default: 180 minutes)

### 8. Force Update

Try forcing an update:

1. Go to **Developer Tools** → **Services**
2. Call service: `homeassistant.update_entity`
3. Entity: `sensor.linqconnect_breakfast`
4. Check logs for any errors

### 9. Calendar Entities

The calendar entities might have data even if sensors don't. Check:
- `calendar.linqconnect_breakfast_calendar`
- `calendar.linqconnect_lunch_calendar`

Look at upcoming events to see if any menu data exists.

## Getting Help

When reporting issues, please provide:

1. **Home Assistant logs** (with debug logging enabled)
2. **Entity attributes** (from Developer Tools → States)
3. **Configuration** (District ID and Building ID - you can redact parts)
4. **Manual API test results** (test the URL in browser)
5. **Home Assistant version**
6. **Integration version**

## Quick Fix Checklist

- [ ] Check logs for errors
- [ ] Verify API credentials (District ID, Building ID)
- [ ] Test API manually in browser
- [ ] Check calendar entities for data
- [ ] Try changing cutoff time
- [ ] Force entity update
- [ ] Restart Home Assistant
- [ ] Check for weekends/holidays (no menu data)
- [ ] Enable debug logging
- [ ] Check timezone settings
