"""Tests for CashPilot button platform."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.cashpilot.api import CashPilotError
from custom_components.cashpilot.button import (
    CashPilotCollectButton,
    CashPilotServiceRestartButton,
    async_setup_entry,
)
from custom_components.cashpilot.const import DATA_SERVICES, DOMAIN

from .conftest import ENTRY_ID, MOCK_SERVICES, make_coordinator_data, make_mock_coordinator


# ---------------------------------------------------------------------------
# async_setup_entry
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_setup_entry_creates_entities():
    """Setup creates 1 collect button + 1 restart per service."""
    coord = make_mock_coordinator()
    hass = MagicMock()
    hass.data = {DOMAIN: {ENTRY_ID: coord}}
    entry = MagicMock()
    entry.entry_id = ENTRY_ID

    added = []
    async_add_entities = MagicMock(side_effect=lambda entities: added.extend(entities))

    await async_setup_entry(hass, entry, async_add_entities)

    # 1 collect + 2 restarts (honeygain, earnapp)
    assert len(added) == 3
    assert isinstance(added[0], CashPilotCollectButton)
    assert isinstance(added[1], CashPilotServiceRestartButton)
    assert isinstance(added[2], CashPilotServiceRestartButton)


@pytest.mark.asyncio
async def test_setup_entry_skips_empty_slug():
    """Services without slug get no restart button."""
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
    # 1 collect + 1 restart for "ok"
    assert len(added) == 2


@pytest.mark.asyncio
async def test_setup_entry_no_services():
    """Only the collect button when no services exist."""
    data = make_coordinator_data(services=[])
    coord = make_mock_coordinator(data=data)
    hass = MagicMock()
    hass.data = {DOMAIN: {ENTRY_ID: coord}}
    entry = MagicMock()
    entry.entry_id = ENTRY_ID

    added = []
    async_add_entities = MagicMock(side_effect=lambda entities: added.extend(entities))

    await async_setup_entry(hass, entry, async_add_entities)
    assert len(added) == 1
    assert isinstance(added[0], CashPilotCollectButton)


# ---------------------------------------------------------------------------
# CashPilotCollectButton
# ---------------------------------------------------------------------------


def test_collect_button_unique_id():
    """Collect button unique_id is correct."""
    coord = make_mock_coordinator()
    btn = CashPilotCollectButton(coord, ENTRY_ID)
    assert btn._attr_unique_id == f"{ENTRY_ID}_collect_earnings"


def test_collect_button_icon():
    """Collect button has refresh icon."""
    coord = make_mock_coordinator()
    btn = CashPilotCollectButton(coord, ENTRY_ID)
    assert btn._attr_icon == "mdi:refresh"


@pytest.mark.asyncio
async def test_collect_button_press_success():
    """Pressing collect triggers collection and refresh."""
    coord = make_mock_coordinator()
    coord.client.async_collect_earnings = AsyncMock()
    coord.async_request_refresh = AsyncMock()

    btn = CashPilotCollectButton(coord, ENTRY_ID)
    await btn.async_press()

    coord.client.async_collect_earnings.assert_awaited_once()
    coord.async_request_refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_collect_button_press_error():
    """Pressing collect when API fails logs but does not crash."""
    coord = make_mock_coordinator()
    coord.client.async_collect_earnings = AsyncMock(
        side_effect=CashPilotError("fail")
    )
    coord.async_request_refresh = AsyncMock()

    btn = CashPilotCollectButton(coord, ENTRY_ID)
    await btn.async_press()

    # Refresh should NOT be called on error (early return)
    coord.async_request_refresh.assert_not_awaited()


# ---------------------------------------------------------------------------
# CashPilotServiceRestartButton
# ---------------------------------------------------------------------------


def test_restart_button_unique_id():
    """Restart button unique_id includes slug."""
    coord = make_mock_coordinator()
    btn = CashPilotServiceRestartButton(coord, ENTRY_ID, "honeygain", "Honeygain")
    assert btn._attr_unique_id == f"{ENTRY_ID}_honeygain_restart"


def test_restart_button_icon():
    """Restart button has restart icon."""
    coord = make_mock_coordinator()
    btn = CashPilotServiceRestartButton(coord, ENTRY_ID, "honeygain", "Honeygain")
    assert btn._attr_icon == "mdi:restart"


@pytest.mark.asyncio
async def test_restart_button_press_success():
    """Pressing restart triggers restart and refresh."""
    coord = make_mock_coordinator()
    coord.client.async_restart_service = AsyncMock()
    coord.async_request_refresh = AsyncMock()

    btn = CashPilotServiceRestartButton(coord, ENTRY_ID, "honeygain", "Honeygain")
    await btn.async_press()

    coord.client.async_restart_service.assert_awaited_once_with("honeygain")
    coord.async_request_refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_restart_button_press_error():
    """Pressing restart when API fails logs but does not crash."""
    coord = make_mock_coordinator()
    coord.client.async_restart_service = AsyncMock(
        side_effect=CashPilotError("fail")
    )
    coord.async_request_refresh = AsyncMock()

    btn = CashPilotServiceRestartButton(coord, ENTRY_ID, "honeygain", "Honeygain")
    await btn.async_press()

    coord.async_request_refresh.assert_not_awaited()
