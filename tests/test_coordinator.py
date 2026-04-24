"""Tests for the CashPilot coordinator."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.cashpilot.api import CashPilotAuthError, CashPilotError
from custom_components.cashpilot.const import (
    DATA_BREAKDOWN,
    DATA_FLEET,
    DATA_HEALTH,
    DATA_SERVICES,
    DATA_SUMMARY,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from custom_components.cashpilot.coordinator import CashPilotCoordinator

from .conftest import (
    MOCK_BREAKDOWN,
    MOCK_FLEET,
    MOCK_HEALTH,
    MOCK_SERVICES,
    MOCK_SUMMARY,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_default_scan_interval():
    """Default scan interval is 300 seconds."""
    assert DEFAULT_SCAN_INTERVAL == 300


def test_data_keys():
    """Data key constants have expected values."""
    assert DATA_SUMMARY == "summary"
    assert DATA_BREAKDOWN == "breakdown"
    assert DATA_SERVICES == "services"
    assert DATA_HEALTH == "health"
    assert DATA_FLEET == "fleet"


# ---------------------------------------------------------------------------
# Coordinator init
# ---------------------------------------------------------------------------


def test_coordinator_init():
    """Coordinator stores client and has correct name/interval."""
    hass = MagicMock()
    client = AsyncMock()
    coord = CashPilotCoordinator(hass, client)
    assert coord.client is client
    assert coord.name == DOMAIN
    assert coord.update_interval == timedelta(seconds=DEFAULT_SCAN_INTERVAL)


# ---------------------------------------------------------------------------
# _async_update_data
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_data_assembles_all_endpoints():
    """_async_update_data calls all API endpoints and assembles data."""
    hass = MagicMock()
    client = AsyncMock()
    client.async_get_earnings_summary = AsyncMock(return_value=MOCK_SUMMARY)
    client.async_get_earnings_breakdown = AsyncMock(return_value=MOCK_BREAKDOWN)
    client.async_get_deployed_services = AsyncMock(return_value=MOCK_SERVICES)
    client.async_get_health_scores = AsyncMock(return_value=MOCK_HEALTH)
    client.async_get_fleet_summary = AsyncMock(return_value=MOCK_FLEET)

    coord = CashPilotCoordinator(hass, client)
    data = await coord._async_update_data()

    assert data[DATA_SUMMARY] == MOCK_SUMMARY
    assert data[DATA_BREAKDOWN] == MOCK_BREAKDOWN
    assert data[DATA_SERVICES] == MOCK_SERVICES
    assert data[DATA_FLEET] == MOCK_FLEET
    # Health is indexed by slug
    assert "honeygain" in data[DATA_HEALTH]
    assert "earnapp" in data[DATA_HEALTH]


@pytest.mark.asyncio
async def test_update_data_health_by_slug():
    """Health data is transformed into a slug-keyed dict."""
    hass = MagicMock()
    client = AsyncMock()
    client.async_get_earnings_summary = AsyncMock(return_value={})
    client.async_get_earnings_breakdown = AsyncMock(return_value=[])
    client.async_get_deployed_services = AsyncMock(return_value=[])
    client.async_get_health_scores = AsyncMock(return_value=MOCK_HEALTH)
    client.async_get_fleet_summary = AsyncMock(return_value=None)

    coord = CashPilotCoordinator(hass, client)
    data = await coord._async_update_data()

    assert data[DATA_HEALTH]["honeygain"]["score"] == 95
    assert data[DATA_HEALTH]["earnapp"]["score"] == 80


@pytest.mark.asyncio
async def test_update_data_none_responses():
    """None responses from endpoints are handled gracefully."""
    hass = MagicMock()
    client = AsyncMock()
    client.async_get_earnings_summary = AsyncMock(return_value=None)
    client.async_get_earnings_breakdown = AsyncMock(return_value=None)
    client.async_get_deployed_services = AsyncMock(return_value=None)
    client.async_get_health_scores = AsyncMock(return_value=None)
    client.async_get_fleet_summary = AsyncMock(return_value=None)

    coord = CashPilotCoordinator(hass, client)
    data = await coord._async_update_data()

    assert data[DATA_SUMMARY] == {}
    assert data[DATA_BREAKDOWN] == []
    assert data[DATA_SERVICES] == []
    assert data[DATA_HEALTH] == {}
    assert data[DATA_FLEET] is None


@pytest.mark.asyncio
async def test_update_data_empty_health():
    """Empty health list produces empty dict."""
    hass = MagicMock()
    client = AsyncMock()
    client.async_get_earnings_summary = AsyncMock(return_value={})
    client.async_get_earnings_breakdown = AsyncMock(return_value=[])
    client.async_get_deployed_services = AsyncMock(return_value=[])
    client.async_get_health_scores = AsyncMock(return_value=[])
    client.async_get_fleet_summary = AsyncMock(return_value=None)

    coord = CashPilotCoordinator(hass, client)
    data = await coord._async_update_data()
    assert data[DATA_HEALTH] == {}


@pytest.mark.asyncio
async def test_update_data_auth_error_raises_update_failed():
    """CashPilotAuthError is wrapped in UpdateFailed."""
    from homeassistant.helpers.update_coordinator import UpdateFailed

    hass = MagicMock()
    client = AsyncMock()
    client.async_get_earnings_summary = AsyncMock(
        side_effect=CashPilotAuthError("expired")
    )

    coord = CashPilotCoordinator(hass, client)
    with pytest.raises(UpdateFailed, match="Authentication failed"):
        await coord._async_update_data()


@pytest.mark.asyncio
async def test_update_data_generic_error_raises_update_failed():
    """CashPilotError is wrapped in UpdateFailed."""
    from homeassistant.helpers.update_coordinator import UpdateFailed

    hass = MagicMock()
    client = AsyncMock()
    client.async_get_earnings_summary = AsyncMock(return_value={})
    client.async_get_earnings_breakdown = AsyncMock(
        side_effect=CashPilotError("fail")
    )

    coord = CashPilotCoordinator(hass, client)
    with pytest.raises(UpdateFailed, match="Error fetching"):
        await coord._async_update_data()
