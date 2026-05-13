"""DataUpdateCoordinator for the CashPilot integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import (
    CashPilotAuthError,
    CashPilotClient,
    CashPilotError,
    CashPilotPermissionError,
)
from .const import (
    DATA_BREAKDOWN,
    DATA_FLEET,
    DATA_HEALTH,
    DATA_SERVICES,
    DATA_SUMMARY,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

type CashPilotConfigEntry = ConfigEntry[CashPilotCoordinator]


class CashPilotCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that polls CashPilot for earnings and service data."""

    config_entry: CashPilotConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: CashPilotClient,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch all data from CashPilot."""
        try:
            summary = await self.client.async_get_earnings_summary()
            breakdown = await self.client.async_get_earnings_breakdown()
            services = await self.client.async_get_deployed_services()
            health = await self.client.async_get_health_scores()
            fleet = await self.client.async_get_fleet_summary()
        except CashPilotAuthError as err:
            if getattr(self, "config_entry", None):
                self.config_entry.async_start_reauth(self.hass)
            raise UpdateFailed(f"Authentication failed: {err}") from err
        except CashPilotPermissionError as err:
            if getattr(self, "config_entry", None):
                self.config_entry.async_start_reauth(self.hass)
            raise UpdateFailed(
                f"Insufficient permissions: {err}"
            ) from err
        except CashPilotError as err:
            raise UpdateFailed(f"Error fetching CashPilot data: {err}") from err

        # Build a health lookup by slug for easy access
        health_by_slug: dict[str, dict[str, Any]] = {}
        if health:
            for entry in health:
                health_by_slug[entry.get("slug", "")] = entry

        return {
            DATA_SUMMARY: summary or {},
            DATA_BREAKDOWN: breakdown or [],
            DATA_SERVICES: services or [],
            DATA_HEALTH: health_by_slug,
            DATA_FLEET: fleet,
        }
