"""Tests for the CashPilot integration __init__.py."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.cashpilot import (
    PLATFORMS,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.cashpilot.const import CONF_PASSWORD, CONF_URL, CONF_USERNAME, DOMAIN


# ---------------------------------------------------------------------------
# PLATFORMS
# ---------------------------------------------------------------------------


def test_platforms_list():
    """All four platforms are registered."""
    assert "binary_sensor" in PLATFORMS
    assert "button" in PLATFORMS
    assert "sensor" in PLATFORMS
    assert "switch" in PLATFORMS
    assert len(PLATFORMS) == 4


# ---------------------------------------------------------------------------
# async_setup_entry
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_setup_entry_success():
    """Successful setup authenticates, refreshes, and forwards platforms."""
    hass = MagicMock()
    hass.data = {}
    hass.config_entries = MagicMock()
    hass.config_entries.async_forward_entry_setups = AsyncMock()

    entry = MagicMock()
    entry.entry_id = "test_id"
    entry.data = {
        CONF_URL: "http://cashpilot:8080",
        CONF_USERNAME: "admin",
        CONF_PASSWORD: "secret",
    }

    mock_client = AsyncMock()
    mock_coordinator = MagicMock()
    mock_coordinator.async_config_entry_first_refresh = AsyncMock()

    with patch(
        "custom_components.cashpilot.async_get_clientsession",
        return_value=MagicMock(),
    ), patch(
        "custom_components.cashpilot.CashPilotClient",
        return_value=mock_client,
    ) as client_cls, patch(
        "custom_components.cashpilot.CashPilotCoordinator",
        return_value=mock_coordinator,
    ):
        result = await async_setup_entry(hass, entry)

    assert result is True
    mock_client.async_login.assert_awaited_once()
    mock_coordinator.async_config_entry_first_refresh.assert_awaited_once()
    assert DOMAIN in hass.data
    assert hass.data[DOMAIN]["test_id"] is mock_coordinator
    hass.config_entries.async_forward_entry_setups.assert_awaited_once_with(
        entry, PLATFORMS
    )


@pytest.mark.asyncio
async def test_setup_entry_stores_coordinator():
    """Coordinator is stored under hass.data[DOMAIN][entry_id]."""
    hass = MagicMock()
    hass.data = {}
    hass.config_entries = MagicMock()
    hass.config_entries.async_forward_entry_setups = AsyncMock()

    entry = MagicMock()
    entry.entry_id = "entry_abc"
    entry.data = {
        CONF_URL: "http://cashpilot:8080",
        CONF_USERNAME: "admin",
        CONF_PASSWORD: "secret",
    }

    mock_coordinator = MagicMock()
    mock_coordinator.async_config_entry_first_refresh = AsyncMock()

    with patch(
        "custom_components.cashpilot.async_get_clientsession",
        return_value=MagicMock(),
    ), patch(
        "custom_components.cashpilot.CashPilotClient",
        return_value=AsyncMock(),
    ), patch(
        "custom_components.cashpilot.CashPilotCoordinator",
        return_value=mock_coordinator,
    ):
        await async_setup_entry(hass, entry)

    assert hass.data[DOMAIN]["entry_abc"] is mock_coordinator


# ---------------------------------------------------------------------------
# async_unload_entry
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_unload_entry_success():
    """Successful unload removes coordinator from hass.data."""
    hass = MagicMock()
    hass.data = {DOMAIN: {"test_id": MagicMock()}}
    hass.config_entries = MagicMock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

    entry = MagicMock()
    entry.entry_id = "test_id"

    result = await async_unload_entry(hass, entry)

    assert result is True
    assert "test_id" not in hass.data[DOMAIN]
    hass.config_entries.async_unload_platforms.assert_awaited_once_with(
        entry, PLATFORMS
    )


@pytest.mark.asyncio
async def test_unload_entry_failure():
    """Failed unload keeps coordinator in hass.data."""
    coordinator = MagicMock()
    hass = MagicMock()
    hass.data = {DOMAIN: {"test_id": coordinator}}
    hass.config_entries = MagicMock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=False)

    entry = MagicMock()
    entry.entry_id = "test_id"

    result = await async_unload_entry(hass, entry)

    assert result is False
    assert hass.data[DOMAIN]["test_id"] is coordinator
