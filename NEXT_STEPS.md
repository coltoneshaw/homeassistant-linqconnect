# Next Steps for LinqConnect Integration

## What We've Built

A complete Home Assistant custom integration for LinqConnect school menus with:

- ✅ Sensor entities for breakfast and lunch
- ✅ Calendar integration for viewing menus
- ✅ UI-based configuration flow
- ✅ Smart timing (switches to next day after configurable cutoff)
- ✅ Full menu data organized by category
- ✅ Theme day support
- ✅ HACS compatibility

## Testing Locally

### 1. Set Up Home Assistant Development Environment

The easiest way is to use the Home Assistant Dev Container:

```bash
# Install VS Code and Docker
# Clone Home Assistant core repository
git clone https://github.com/home-assistant/core.git
cd core

# Open in VS Code and reopen in container
code .
# Click "Reopen in Container" when prompted
```

### 2. Copy Integration to Dev Environment

Copy the `custom_components/linqconnect` directory to your Home Assistant config:

```bash
# If using dev container:
cp -r /path/to/linqconnect/custom_components/linqconnect config/custom_components/

# If testing on existing HA instance:
cp -r custom_components/linqconnect /path/to/homeassistant/config/custom_components/
```

### 3. Restart Home Assistant

```bash
# In dev container or your HA instance
# Restart Home Assistant
```

### 4. Add the Integration

1. Go to Settings → Devices & Services
2. Click "+ Add Integration"
3. Search for "LinqConnect"
4. Enter your District ID and Building ID
5. Test that sensors and calendar appear

## Publishing to HACS

### 1. Create GitHub Repository

```bash
cd /Users/coltonshaw/development/linqconnect

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial release of LinqConnect Home Assistant integration"

# Create GitHub repo (via GitHub web UI or CLI)
gh repo create linqconnect-homeassistant --public --source=. --remote=origin

# Push to GitHub
git push -u origin main
```

### 2. Create a Release

```bash
# Tag the release
git tag -a v1.0.0 -m "Initial release"
git push origin v1.0.0

# Or create via GitHub web interface
```

### 3. Submit to HACS Default Repository

Option A: **Default HACS Repository** (Recommended for wider distribution)

1. Go to https://github.com/hacs/default
2. Fork the repository
3. Edit `integration` file
4. Add your repository following the format
5. Submit a pull request

Option B: **Custom Repository** (Easier, but users must manually add)

Users add your repo manually:
1. HACS → Integrations → ⋮ → Custom repositories
2. Add your repo URL
3. Select "Integration" as category

## Before You Publish

### Update manifest.json

Edit `custom_components/linqconnect/manifest.json`:

```json
{
  "codeowners": ["@yourgithubusername"],
  "documentation": "https://github.com/yourgithubusername/linqconnect-homeassistant",
  "issue_tracker": "https://github.com/yourgithubusername/linqconnect-homeassistant/issues"
}
```

### Update README.md

Replace placeholder URLs:
- `https://github.com/yourusername/linqconnect-homeassistant`
- With your actual GitHub username

## Notification Setup (For Users)

Users can set up notifications using Home Assistant automations. Example:

```yaml
automation:
  - alias: "Morning Lunch Notification"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: notify.mobile_app_phone
        data:
          title: "{{ state_attr('sensor.linqconnect_lunch', 'theme_day') or 'Today\\'s Lunch' }}"
          message: >
            Main: {{ state_attr('sensor.linqconnect_lunch', 'main_entree_formatted') }}
```

## Troubleshooting Common Issues

### Import Errors

If you see import errors, ensure Home Assistant version is 2024.1.0+. The integration uses modern HA features.

### API Rate Limiting

Default update interval is 3 hours. If you experience issues, increase this in the config options.

### Date Format Issues

The API uses `M/D/YYYY` format. If you see date parsing errors, check your timezone settings.

## Enhancements for Future Versions

Consider adding:

1. **Allergen Filtering**: Allow users to specify allergens and highlight items
2. **Multiple Buildings**: Support tracking menus for multiple children/schools
3. **Nutritional Display**: Show detailed nutritional information
4. **Menu Images**: If API provides images, display them
5. **Integration Services**: Custom service for sending formatted notifications
6. **Weekend/Holiday Detection**: Better handling of non-school days

## Resources

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [HACS Documentation](https://hacs.xyz/)
- [Home Assistant Community](https://community.home-assistant.io/)
- [LinqConnect API](https://api.linqconnect.com/) (unofficial documentation needed)

## Questions?

Feel free to reach out or check the Home Assistant developer community for help!
