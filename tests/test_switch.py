"""Tests for CashPilot switch platform."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.cashpilot.api import CashPilotError
from custom_components.cashpilot.const import DATA_SERVICES, DOMAIN
from custom_components.cashpilot.switch import (
    CashPilotServiceSwitch,
    async_setup_entry,
)

from .conftest import ENTRY_ID, MOCK_SERVICES, make_coordinator_data, make_mock_coordinator


# ---------------------------------------------------------------------------
# async_setup_entry
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_setup_entry_creates_switches():
    """Setup creates one switch per service."""
    coord = make_mock_coordinator()
    hass = MagicMock()
    hass.data = {DOMAIN: {ENTRY_ID: coord}}
    entry = MagicMock()
    entry.entry_id = ENTRY_ID

    added = []
    async_add_entities = MagicMock(side_effect=lambda entities: added.extend(entities))

    await async_setup_entry(hass, entry, async_add_entities)

    assert len(added) == 2
    slugs = {e._slug for e in added}
    assert slugs == {"honeygain", "earnapp"}


@pytest.mark.asyncio
async def test_setup_entry_skips_empty_slug():
    """Services without slug are skipped."""
    data = make_coordinator_data(
        services=[{"slug": "", "name": "NoSlug"}, {"slug": "ok", "name": "OK"}]
    )
    coord = make_mock_coordinator(data=data)
    hass = MagicMock()
    hass.data = {DOMAIN: {ENTRY_ID: coord}}
    entry = MagicMock()
    entry.entry_id = ENTRY_ID

    added = []
    async_add_entities = MagicMock(side_effect=lambda entities: added.extend(entities))

    await async_setup_entry(hass, entry, async_add_entities)
    assert len(added) == 1


@pytest.mark.asyncio
async def test_setup_entry_no_services():
    """No switches when no services."""
    data = make_coordinator_data(services=[])
    coord = make_mock_coordinator(data=data)
    hass = MagicMock()
    hass.data = {DOMAIN: {ENTRY_ID: coord}}
    entry = MagicMock()
    entry.entry_id = ENTRY_ID

    added = []
    async_add_entities = MagicMock(side_effect=lambda entities: added.extend(entities))

    await async_setup_entry(hass, entry, async_add_entities)
    assert len(added) == 0


# ---------------------------------------------------------------------------
# CashPilotServiceSwitch
# ---------------------------------------------------------------------------


def test_switch_unique_id():
    coord = make_mock_coordinator()
    sw = CashPilotServiceSwitch(coord, ENTRY_ID, "honeygain", "Honeygain")
    assert sw._attr_unique_id == f"{ENTRY_ID}_honeygain_switch"


def test_switch_icon():
    coord = make_mock_coordinator()
    sw = CashPilotServiceSwitch(coord, ENTRY_ID, "honeygain", "Honeygain")
    assert sw._attr_icon == "mdi:power"


def test_switch_is_on_running():
    """Switch is on when container is running."""
    coord = make_mock_coordinator()
    sw = CashPilotServiceSwitch(coord, ENTRY_ID, "honeygain", "Honeygain")
    assert sw.is_on is True


def test_switch_is_on_stopped():
    """Switch is off when container is stopped."""
    coord = make_mock_coordinator()
    sw = CashPilotServiceSwitch(coord, ENTRY_ID, "earnapp", "EarnApp")
    assert sw.is_on is False


def test_switch_is_on_missing():
    """Switch returns None for unknown slug."""
    coord = make_mock_coordinator()
    sw = CashPilotServiceSwitch(coord, ENTRY_ID, "missing", "Missing")
    assert sw.is_on is None


def test_switch_case_insensitive():
    """Status comparison is case-insensitive."""
    data = make_coordinator_data(
        services=[{"slug": "test", "container_status": "Running"}]
    )
    coord = make_mock_coordinator(data=data)
    sw = CashPilotServiceSwitch(coord, ENTRY_ID, "test", "Test")
    assert sw.is_on is True


def test_switch_empty_status():
    """Empty status means off."""
    data = make_coordinator_data(
        services=[{"slug": "test", "container_status": ""}]
    )
    coord = make_mock_coordinator(data=data)
    sw = CashPilotServiceSwitch(coord, ENTRY_ID, "test", "Test")
    assert sw.is_on is False


# ---------------------------------------------------------------------------
# async_turn_on / async_turn_off
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_turn_on_success():
    """Turn on calls start_service and refreshes."""
    coord = make_mock_coordinator()
    coord.client.async_start_service = AsyncMock()
    coord.async_request_refresh = AsyncMock()

    sw = CashPilotServiceSwitch(coord, ENTRY_ID, "earnapp", "EarnApp")
    await sw.async_turn_on()

    coord.client.async_start_service.assert_awaited_once_with("earnapp")
    coord.async_request_refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_turn_on_error():
    """Turn on failure logs and does not refresh."""
    coord = make_mock_coordinator()
    coord.client.async_start_service = AsyncMock(
        side_effect=CashPilotError("fail")
    )
    coord.async_request_refresh = AsyncMock()

    sw = CashPilotServiceSwitch(coord, ENTRY_ID, "earnapp", "EarnApp")
    await sw.async_turn_on()

    coord.async_request_refresh.assert_not_awaited()


@pytest.mark.asyncio
async def test_turn_off_success():
    """Turn off calls stop_service and refreshes."""
    coord = make_mock_coordinator()
    coord.client.async_stop_service = AsyncMock()
    coord.async_request_refresh = AsyncMock()

    sw = CashPilotServiceSwitch(coord, ENTRY_ID, "honeygain", "Honeygain")
    await sw.async_turn_off()

    coord.client.async_stop_service.assert_awaited_once_with("honeygain")
    coord.async_request_refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_turn_off_error():
    """Turn off failure logs and does not refresh."""
    coord = make_mock_coordinator()
    coord.client.async_stop_service = AsyncMock(
        side_effect=CashPilotError("fail")
    )
    coord.async_request_refresh = AsyncMock()

    sw = CashPilotServiceSwitch(coord, ENTRY_ID, "honeygain", "Honeygain")
    await sw.async_turn_off()

    coord.async_request_refresh.assert_not_awaited()
