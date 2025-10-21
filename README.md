# LinqConnect School Menus for Home Assistant

A Home Assistant integration for displaying school lunch and breakfast menus from LinqConnect.

## Features

- **Sensor Entities**: Display today's or tomorrow's breakfast and lunch menus
- **Calendar Integration**: View upcoming menus in a calendar format
- **Smart Timing**: Automatically switches to the next school day's menu after a configurable cutoff time (default: 10 AM)
- **Organized Menu Display**: All menu items organized by category (Main Entrée, Grains, Vegetables, Fruits, Milk, Condiments)
- **Theme Days**: Shows special theme days like "Taco Tuesday" or "Fun Friday"
- **Automation Support**: Use sensor data to create notifications and automations

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/coltoneshaw/linqconnect-homeassistant`
6. Select "Integration" as the category
7. Click "Add"
8. Search for "LinqConnect School Menus" and install it
9. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/linqconnect` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

### Finding Your IDs

You'll need two IDs from LinqConnect:

1. Go to your school's LinqConnect menu page (e.g., `https://linqconnect.com/public/menu/XXXXX?buildingId=...`)
2. Look at the URL parameters:
   - `districtId` - Your district's unique identifier (GUID format)
   - `buildingId` - Your school building's unique identifier (GUID format)

You can also find these in the browser's developer tools network tab when loading the menu page.

### Setup via UI

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **LinqConnect School Menus**
4. Enter your **District ID** and **Building ID**
5. Click **Submit**

### Configuration Options

After setup, you can configure additional options:

- **Cutoff Time**: Time after which sensors show the next school day's menu (format: HH:MM, default: 10:00)
- **Update Interval**: How often to fetch new data in minutes (default: 180 / 3 hours)
- **Calendar Days Ahead**: How many days of menu data to fetch for the calendar (default: 30)

To change options:
1. Go to **Settings** → **Devices & Services**
2. Find **LinqConnect School Menus**
3. Click **Configure**

## Entities Created

The integration creates the following entities:

### Sensors

- `sensor.linqconnect_breakfast` - Today's or tomorrow's breakfast menu
- `sensor.linqconnect_lunch` - Today's or tomorrow's lunch menu

#### Sensor Attributes

Each sensor includes the following attributes:

- `theme_day` - Special theme name (e.g., "Taco Tuesday")
- `menu_plan` - Menu plan name (e.g., "K-8 Lunch SY 25-26")
- `main_entree` - List of main entrée options
- `main_entree_formatted` - Comma-separated string of main entrées
- `grain` - List of grain options
- `vegetable` - List of vegetable options
- `fruit` - List of fruit options
- `milk` - List of milk options
- `condiment` - List of condiments
- `side_item` - List of side items

### Calendar

- `calendar.linqconnect_breakfast_calendar` - Breakfast menu calendar
- `calendar.linqconnect_lunch_calendar` - Lunch menu calendar

## Usage Examples

### Display in Dashboard

Add a markdown card to show today's lunch:

```yaml
type: markdown
content: |
  ## {{ states('sensor.linqconnect_lunch') }}

  **Main Entrées:**
  {% for item in state_attr('sensor.linqconnect_lunch', 'main_entree') %}
  - {{ item }}
  {% endfor %}

  **Sides:**
  {% for item in state_attr('sensor.linqconnect_lunch', 'vegetable') %}
  - {{ item }}
  {% endfor %}
title: Today's Lunch
```

### Create Notification Automation

Send a notification with tomorrow's lunch menu every evening:

```yaml
automation:
  - alias: "Notify Tomorrow's Lunch"
    trigger:
      - platform: time
        at: "19:00:00"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "{{ state_attr('sensor.linqconnect_lunch', 'theme_day') or 'Tomorrow\\'s Lunch' }}"
          message: "{{ state_attr('sensor.linqconnect_lunch', 'main_entree_formatted') }}"
```

### Notify on Specific Menu Items

Get notified when pizza is on the menu:

```yaml
automation:
  - alias: "Pizza Day Alert"
    trigger:
      - platform: state
        entity_id: sensor.linqconnect_lunch
    condition:
      - condition: template
        value_template: >
          {{ 'pizza' in (state_attr('sensor.linqconnect_lunch', 'main_entree_formatted') | lower) }}
    action:
      - service: notify.family
        data:
          title: "🍕 Pizza Day!"
          message: "It's pizza day at school tomorrow!"
```

### Calendar View

Add the calendar entities to your Home Assistant calendar view to see the full month's menu at a glance.

## Troubleshooting

### Integration won't load

- Verify your District ID and Building ID are correct
- Check Home Assistant logs for error messages
- Ensure you have an internet connection

### No menu data showing

- Check that menu data is available on the LinqConnect website for your school
- Verify the date range settings in options
- Try reducing the "Calendar Days Ahead" value if you're getting timeout errors

### Sensors showing "No menu available"

- This is normal for weekends and school holidays
- Check the calendar entities to see what dates have menu data
- Verify the cutoff time setting if the wrong day is showing

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or feature requests, please [open an issue on GitHub](https://github.com/coltoneshaw/linqconnect-homeassistant/issues).

## Disclaimer

This integration is not affiliated with, endorsed by, or connected to LinqConnect or its parent company. Use at your own risk.
