# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-21

### Added
- Initial release of LinqConnect School Menus integration
- Sensor entities for breakfast and lunch menus
- Calendar entities showing menus as events with emoji titles
- UI-based configuration flow with district and building ID
- Menu plan selection during setup (K-8, K-12, Pre-K, etc.)
- Smart timing - automatically switches to next school day after configurable cutoff time (default 10:00 AM)
- Options flow for changing cutoff time, update interval, and menu plans
- Force update service (`linqconnect.force_update`)
- Automation blueprint for daily menu notifications
- All menu categories displayed: Main Entrée, Grain, Vegetable, Fruit, Milk, Condiment, Side Items
- Theme day support (e.g., "Taco Tuesday", "Fun Friday")
- HACS compatibility
- Debug logging support

### Features
- **Sensors**: Display today's or tomorrow's menu with all items organized by category
- **Calendar**: All-day events with formatted descriptions showing menu items
- **Notifications**: Automation blueprint for daily notifications (configurable time, device, meal type)
- **Menu Plan Filtering**: Select which grade levels to track (supports multiple students)
- **Smart Updates**: 3-hour polling interval (configurable)
- **Developer Tools**: Docker-based development environment with `make` commands

### Technical
- Python 3.11+ compatible
- Home Assistant 2024.1.0+ required
- Uses DataUpdateCoordinator for efficient API polling
- Config flow for easy setup
- No YAML configuration required (UI-based only)

[1.0.0]: https://github.com/coltoneshaw/homeassistant-linqconnect/releases/tag/v1.0.0
