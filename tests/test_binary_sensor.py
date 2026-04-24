"""Tests for CashPilot binary sensor platform."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.cashpilot.binary_sensor import (
    CashPilotServiceRunningSensor,
    async_setup_entry,
)
from custom_components.cashpilot.const import DATA_SERVICES, DOMAIN

from .conftest import ENTRY_ID, MOCK_SERVICES, make_coordinator_data, make_mock_coordinator


# ---------------------------------------------------------------------------
# async_setup_entry
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_setup_entry_creates_entities():
    """Setup creates one binary sensor per service."""
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
    """Services without a slug are skipped."""
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
    assert added[0]._slug == "ok"


@pytest.mark.asyncio
async def test_setup_entry_no_services():
    """No entities when services list is empty."""
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
# CashPilotServiceRunningSensor
# ---------------------------------------------------------------------------


def test_sensor_unique_id():
    """Unique ID uses entry_id and slug."""
    coord = make_mock_coordinator()
    sensor = CashPilotServiceRunningSensor(coord, ENTRY_ID, "honeygain", "Honeygain")
    assert sensor._attr_unique_id == f"{ENTRY_ID}_honeygain_running"


def test_sensor_is_on_running():
    """is_on is True when container_status is running."""
    coord = make_mock_coordinator()
    sensor = CashPilotServiceRunningSensor(coord, ENTRY_ID, "honeygain", "Honeygain")
    assert sensor.is_on is True


def test_sensor_is_on_stopped():
    """is_on is False when container_status is stopped."""
    coord = make_mock_coordinator()
    sensor = CashPilotServiceRunningSensor(coord, ENTRY_ID, "earnapp", "EarnApp")
    assert sensor.is_on is False


def test_sensor_is_on_missing_slug():
    """is_on is None when slug not found."""
    coord = make_mock_coordinator()
    sensor = CashPilotServiceRunningSensor(coord, ENTRY_ID, "missing", "Missing")
    assert sensor.is_on is None


def test_sensor_is_on_empty_services():
    """is_on is None with empty service list."""
    data = make_coordinator_data(services=[])
    coord = make_mock_coordinator(data=data)
    sensor = CashPilotServiceRunningSensor(coord, ENTRY_ID, "honeygain", "Honeygain")
    assert sensor.is_on is None


def test_sensor_case_insensitive_status():
    """Status comparison is case-insensitive."""
    data = make_coordinator_data(
        services=[{"slug": "test", "container_status": "Running"}]
    )
    coord = make_mock_coordinator(data=data)
    sensor = CashPilotServiceRunningSensor(coord, ENTRY_ID, "test", "Test")
    assert sensor.is_on is True


def test_sensor_translation_key():
    """Translation key is set correctly."""
    coord = make_mock_coordinator()
    sensor = CashPilotServiceRunningSensor(coord, ENTRY_ID, "test", "Test")
    assert sensor._attr_translation_key == "service_running"
