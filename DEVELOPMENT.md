# Development Guide

## Quick Start

```bash
# Start test environment
make setup

# Make code changes, then:
make restart

# View logs
make logs

# Test API without HA
make test-api

# Clean everything
make clean
```

Access at: **http://localhost:8123**

## Requirements

- Docker Desktop
- Make

## Project Structure

```
custom_components/linqconnect/
├── __init__.py          # Main setup
├── api.py               # API client
├── calendar.py          # Calendar entities
├── config_flow.py       # UI config
├── coordinator.py       # Data management
├── sensor.py            # Sensors
└── manifest.json        # Metadata
```

## Testing

```bash
# Quick API test (no HA needed)
source venv/bin/activate
python3 test_api.py

# Unit tests
pytest tests/ -v
```

## Release

```bash
# Update version in manifest.json
# Update CHANGELOG.md

git add .
git commit -m "Release vX.X.X"
git tag -a vX.X.X -m "Release vX.X.X"
git push origin main --tags
```

Then create GitHub release from tag.
