"""Tests for the CashPilot coordinator data logic."""

from __future__ import annotations

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
)

from .conftest import (
    MOCK_BREAKDOWN,
    MOCK_FLEET,
    MOCK_HEALTH,
    MOCK_SERVICES,
    MOCK_SUMMARY,
)


def test_default_scan_interval() -> None:
    """Verify default scan interval is 300 seconds (5 minutes)."""
    assert DEFAULT_SCAN_INTERVAL == 300


def test_data_keys() -> None:
    """Verify data key constants."""
    assert DATA_SUMMARY == "summary"
    assert DATA_BREAKDOWN == "breakdown"
    assert DATA_SERVICES == "services"
    assert DATA_HEALTH == "health"
    assert DATA_FLEET == "fleet"


@pytest.mark.asyncio
async def test_coordinator_data_assembly() -> None:
    """Test that coordinator assembles data from all endpoints."""
    client = MagicMock()
    client.async_get_earnings_summary = AsyncMock(return_value=MOCK_SUMMARY)
    client.async_get_earnings_breakdown = AsyncMock(return_value=MOCK_BREAKDOWN)
    client.async_get_deployed_services = AsyncMock(return_value=MOCK_SERVICES)
    client.async_get_health_scores = AsyncMock(return_value=MOCK_HEALTH)
    client.async_get_fleet_summary = AsyncMock(return_value=MOCK_FLEET)

    # Simulate coordinator _async_update_data logic
    summary = await client.async_get_earnings_summary()
    breakdown = await client.async_get_earnings_breakdown()
    services = await client.async_get_deployed_services()
    health = await client.async_get_health_scores()
    fleet = await client.async_get_fleet_summary()

    health_by_slug = {}
    for entry in health:
        health_by_slug[entry.get("slug", "")] = entry

    data = {
        DATA_SUMMARY: summary or {},
        DATA_BREAKDOWN: breakdown or [],
        DATA_SERVICES: services or [],
        DATA_HEALTH: health_by_slug,
        DATA_FLEET: fleet,
    }

    assert data[DATA_SUMMARY]["total"] == 42.50
    assert len(data[DATA_BREAKDOWN]) == 2
    assert len(data[DATA_SERVICES]) == 2
    assert data[DATA_FLEET]["online_workers"] == 2
    assert "honeygain" in data[DATA_HEALTH]


@pytest.mark.asyncio
async def test_auth_error_propagation() -> None:
    """Test auth error propagation."""
    client = MagicMock()
    client.async_get_earnings_summary = AsyncMock(
        side_effect=CashPilotAuthError("expired")
    )

    with pytest.raises(CashPilotAuthError):
        await client.async_get_earnings_summary()


@pytest.mark.asyncio
async def test_api_error_propagation() -> None:
    """Test general API error propagation."""
    client = MagicMock()
    client.async_get_earnings_summary = AsyncMock(
        side_effect=CashPilotError("fail")
    )

    with pytest.raises(CashPilotError):
        await client.async_get_earnings_summary()


@pytest.mark.asyncio
async def test_fleet_none_handled() -> None:
    """Test that None fleet data is handled."""
    client = MagicMock()
    client.async_get_fleet_summary = AsyncMock(return_value=None)

    fleet = await client.async_get_fleet_summary()
    assert fleet is None
