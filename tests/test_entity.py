"""Tests for the CashPilot base entity classes."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.cashpilot.const import DOMAIN, MANUFACTURER
from custom_components.cashpilot.entity import CashPilotEntity, CashPilotServiceEntity

from .conftest import ENTRY_ID, make_mock_coordinator


# ---------------------------------------------------------------------------
# CashPilotEntity
# ---------------------------------------------------------------------------


def test_cashpilot_entity_has_entity_name():
    """has_entity_name is True."""
    assert CashPilotEntity._attr_has_entity_name is True


def test_cashpilot_entity_init():
    """Base entity stores coordinator and entry_id."""
    coord = make_mock_coordinator()
    entity = CashPilotEntity(coord, ENTRY_ID)
    assert entity.coordinator is coord
    assert entity._entry_id == ENTRY_ID


def test_cashpilot_entity_device_info():
    """Device info has correct identifiers and name."""
    coord = make_mock_coordinator()
    entity = CashPilotEntity(coord, ENTRY_ID)
    info = entity.device_info
    assert (DOMAIN, ENTRY_ID) in info["identifiers"]
    assert info["name"] == "CashPilot"
    assert info["manufacturer"] == MANUFACTURER


# ---------------------------------------------------------------------------
# CashPilotServiceEntity
# ---------------------------------------------------------------------------


def test_service_entity_has_entity_name():
    """has_entity_name is True for service entity."""
    assert CashPilotServiceEntity._attr_has_entity_name is True


def test_service_entity_init():
    """Service entity stores slug and service_name."""
    coord = make_mock_coordinator()
    entity = CashPilotServiceEntity(coord, ENTRY_ID, "honeygain", "Honeygain")
    assert entity._slug == "honeygain"
    assert entity._service_name == "Honeygain"
    assert entity._entry_id == ENTRY_ID


def test_service_entity_device_info():
    """Service device info references parent via via_device."""
    coord = make_mock_coordinator()
    entity = CashPilotServiceEntity(coord, ENTRY_ID, "honeygain", "Honeygain")
    info = entity.device_info
    assert (DOMAIN, "honeygain") in info["identifiers"]
    assert info["name"] == "Honeygain"
    assert info["manufacturer"] == MANUFACTURER
    assert info["model"] == "Passive Income Service"
    assert info["via_device"] == (DOMAIN, ENTRY_ID)
