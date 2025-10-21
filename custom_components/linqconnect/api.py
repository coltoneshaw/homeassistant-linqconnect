"""API client for LinqConnect."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
import logging
from typing import Any

import aiohttp
import async_timeout

from .const import API_FAMILY_MENU

_LOGGER = logging.getLogger(__name__)


class LinqConnectApiClient:
    """API client for LinqConnect school menus."""

    def __init__(
        self,
        district_id: str,
        building_id: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialize the API client."""
        self._district_id = district_id
        self._building_id = building_id
        self._session = session

    async def async_get_menu(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict[str, Any]:
        """Get menu data from the API."""
        if start_date is None:
            start_date = datetime.now()
        if end_date is None:
            end_date = start_date + timedelta(days=30)

        params = {
            "districtId": self._district_id,
            "buildingId": self._building_id,
            "startDate": start_date.strftime("%-m-%-d-%Y"),
            "endDate": end_date.strftime("%-m-%-d-%Y"),
        }

        try:
            async with async_timeout.timeout(10):
                response = await self._session.get(
                    API_FAMILY_MENU,
                    params=params,
                )
                response.raise_for_status()
                data = await response.json()
                _LOGGER.debug("Successfully fetched menu data")
                return data
        except asyncio.TimeoutError as exception:
            _LOGGER.error("Timeout error fetching menu data: %s", exception)
            raise ApiClientError("Timeout connecting to LinqConnect API") from exception
        except aiohttp.ClientError as exception:
            _LOGGER.error("Error fetching menu data: %s", exception)
            raise ApiClientError("Error connecting to LinqConnect API") from exception
        except Exception as exception:
            _LOGGER.error("Unexpected error fetching menu data: %s", exception)
            raise ApiClientError("Unexpected error") from exception

    async def async_validate_credentials(self) -> bool:
        """Validate that the district and building IDs are valid."""
        try:
            # Try to fetch a small date range to validate credentials
            end_date = datetime.now() + timedelta(days=1)
            await self.async_get_menu(end_date=end_date)
            return True
        except ApiClientError:
            return False


class ApiClientError(Exception):
    """Exception to indicate a general API error."""
