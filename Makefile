.PHONY: start stop restart logs clean setup test-api

setup: start
	@echo "🔧 Auto-configuring LinqConnect integration..."
	@mkdir -p volumes/ha/.storage
	@echo '{"version": 1, "minor_version": 1, "key": "core.config_entries", "data": {"entries": [{"entry_id": "linqconnect_auto", "version": 1, "domain": "linqconnect", "title": "LinqConnect School Menus", "data": {"district_id": "8571dba1-79cf-eb11-a2c4-f81ec5475527", "building_id": "b812a68d-5ed4-eb11-a2c4-87353d5bc03e", "menu_plans": ["K-12 Breakfast SY 25-26", "K-8 Lunch SY 25-26"]}, "options": {"cutoff_time": "10:00", "update_interval": 180, "calendar_days": 30}, "pref_disable_new_entities": false, "pref_disable_polling": false, "source": "user", "unique_id": null, "disabled_by": null}]}}' > volumes/ha/.storage/core.config_entries
	@echo "✅ LinqConnect auto-configured with K-12 Breakfast and K-8 Lunch plans!"
	@echo "🔄 Restarting Home Assistant..."
	@docker-compose restart
	@echo "✅ Setup complete! Access at http://localhost:8123"

start: 
	docker-compose up -d

stop:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f | grep -i linqconnect

logs-all:
	docker-compose logs -f

clean: 
	docker-compose down -v
	rm -rf volumes/ha

test-api: 
	@echo "🧪 Testing LinqConnect API..."
	@source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate && pip install aiohttp > /dev/null
	@source venv/bin/activate && python3 test_api.py

dev: ## Start in development mode with logs
	@make start
	@make logs
