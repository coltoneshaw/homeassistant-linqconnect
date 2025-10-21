# LinqConnect School Menus

A Home Assistant integration that displays your school's breakfast and lunch menus from LinqConnect.

## Features

- View menus in your Home Assistant calendar
- Get daily notifications of tomorrow's menu
- Display menus on dashboards
- Support for multiple grade levels (K-8, K-12, Pre-K)
- Automatically shows next school day's menu after 10 AM

## Installation

### HACS

1. Add custom repository: `https://github.com/coltoneshaw/homeassistant-linqconnect`
2. Select category: Integration
3. Install and restart Home Assistant

### Manual

Copy `custom_components/linqconnect` to your `config/custom_components` directory and restart.

## Setup

### Find Your IDs

Your school's LinqConnect URL contains the IDs you need:
```
https://linqconnect.com/public/menu/XXXXX?buildingId=abc...&districtId=def...
```

Copy the `buildingId` and `districtId` values.

### Add Integration

Go to Settings → Devices & Services → Add Integration → Search "LinqConnect"

Enter your District ID and Building ID, then select which menu plans to track (K-8, K-12, etc.).

## Notifications

The easiest way to get daily menu notifications is using the included blueprint.

### Import Blueprint

Settings → Automations → Blueprints → Import Blueprint

Paste this URL:
```
https://github.com/coltoneshaw/homeassistant-linqconnect/blob/main/blueprints/automation/linqconnect/daily_menu_notification.yaml
```

### Create Automation

Settings → Automations → Create Automation → Select "Daily School Menu Notification"

Configure your notification time and device, then save. You'll get notifications Monday-Friday.

## What Gets Created

**Sensors:**
- `sensor.linqconnect_breakfast`
- `sensor.linqconnect_lunch`

**Calendars:**
- `calendar.linqconnect_breakfast_calendar`
- `calendar.linqconnect_lunch_calendar`

**Sensor attributes:**
- `main_entree_formatted` - Comma-separated list of main dishes
- `theme_day` - Special theme like "Taco Tuesday"
- Individual categories: `grain`, `vegetable`, `fruit`, `milk`, `condiment`, `side_item`

## Examples

### Simple Dashboard Card

```yaml
type: markdown
content: |
  ## {{ states('sensor.linqconnect_lunch') or 'Tomorrow\'s Lunch' }}
  {{ state_attr('sensor.linqconnect_lunch', 'main_entree_formatted') }}
title: School Lunch
```

### Alert on Pizza Day

```yaml
automation:
  - alias: "Pizza Day"
    trigger:
      platform: state
      entity_id: sensor.linqconnect_lunch
    condition:
      condition: template
      value_template: "{{ 'pizza' in (state_attr('sensor.linqconnect_lunch', 'main_entree_formatted') | lower) }}"
    action:
      service: notify.family
      data:
        message: "Pizza day tomorrow!"
```

## Configuration

Settings → Devices & Services → LinqConnect → Configure

Available options:
- Menu plans to track
- Cutoff time for switching to next day
- Update interval
- Calendar days ahead

## Troubleshooting

**No menu data?** Check if it's a weekend or holiday. Menu data is only available on school days.

**Wrong day showing?** Adjust the cutoff time in the configuration options.

**Integration won't load?** Verify your District ID and Building ID are correct.

## Services

Force a manual update: Developer Tools → Actions → `linqconnect.force_update`

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for local development setup.

## License

MIT

## Disclaimer

Not affiliated with LinqConnect. This is an unofficial integration.
