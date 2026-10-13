"""Regression tests for the names Home Assistant shows for CashPilot entities.

v1.1.2 shipped per-service names like "{service_name} balance" with no
translation placeholders set, so HA showed "Wipter {service_name} balance"
and made the id sensor.wipter_service_name_balance.

The suite stubs Home Assistant, so this module composes names the way
homeassistant/helpers/entity.py (2026.10.1) does with has_entity_name=True:
an explicit _attr_name wins (None means "use the device name alone"),
otherwise the translated name is formatted with translation_placeholders and,
on a missing placeholder, returned unformatted. entity_registry.py then joins
the device name and the entity name with a space for both the friendly name
and the entity id.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from custom_components.cashpilot.binary_sensor import CashPilotServiceRunningSensor
from custom_components.cashpilot.button import CashPilotServiceRestartButton
from custom_components.cashpilot.sensor import (
    CashPilotServiceBalanceSensor,
    CashPilotServiceCpuSensor,
    CashPilotServiceHealthSensor,
    CashPilotServiceMemorySensor,
    CashPilotServiceUptimeSensor,
)
from custom_components.cashpilot.switch import CashPilotServiceSwitch

from .conftest import ENTRY_ID, make_mock_coordinator

COMPONENT = Path(__file__).parent.parent / "custom_components" / "cashpilot"
TRANSLATION_FILES = [COMPONENT / "strings.json", *sorted((COMPONENT / "translations").glob("*.json"))]

PER_SERVICE = [
    ("sensor", CashPilotServiceBalanceSensor),
    ("sensor", CashPilotServiceHealthSensor),
    ("sensor", CashPilotServiceUptimeSensor),
    ("sensor", CashPilotServiceCpuSensor),
    ("sensor", CashPilotServiceMemorySensor),
    ("binary_sensor", CashPilotServiceRunningSensor),
    ("button", CashPilotServiceRestartButton),
    ("switch", CashPilotServiceSwitch),
]


def _entity_name(entity, platform: str, translations: dict) -> str | None:
    """Entity name as HA's Entity._name_internal resolves it."""
    if hasattr(entity, "_attr_name"):
        return entity._attr_name
    name = translations["entity"][platform][entity._attr_translation_key]["name"]
    placeholders = getattr(entity, "_attr_translation_placeholders", {})
    try:
        return name.format(**placeholders)
    except KeyError:
        return name


def _compose(entity, platform: str, translations: dict) -> tuple[str, str]:
    """Friendly name and entity id: device name + entity name, as HA joins them."""
    device_name = entity.device_info["name"]
    name = _entity_name(entity, platform, translations)
    full = " ".join(part for part in (device_name, name) if part)
    object_id = re.sub(r"[^a-z0-9]+", "_", full.lower()).strip("_")
    return full, f"{platform}.{object_id}"


def _make(cls):
    return cls(make_mock_coordinator(), ENTRY_ID, "wipter", "Wipter")


@pytest.fixture(params=TRANSLATION_FILES, ids=lambda p: p.name)
def translations(request) -> dict:
    return json.loads(request.param.read_text())


def test_service_sensor_name_and_entity_id(translations):
    name, entity_id = _compose(_make(CashPilotServiceBalanceSensor), "sensor", translations)
    assert name == "Wipter Balance"
    assert entity_id == "sensor.wipter_balance"


def test_service_button_name_and_entity_id(translations):
    name, entity_id = _compose(_make(CashPilotServiceRestartButton), "button", translations)
    assert name == "Wipter Restart"
    assert entity_id == "button.wipter_restart"


def test_service_switch_takes_the_device_name(translations):
    name, entity_id = _compose(_make(CashPilotServiceSwitch), "switch", translations)
    assert name == "Wipter"
    assert entity_id == "switch.wipter"


@pytest.mark.parametrize(("platform", "cls"), PER_SERVICE, ids=lambda v: getattr(v, "__name__", v))
def test_no_per_service_name_keeps_a_placeholder(translations, platform, cls):
    name, entity_id = _compose(_make(cls), platform, translations)
    assert "{" not in name and "}" not in name
    assert "service_name" not in entity_id


def test_no_entity_translation_has_a_placeholder(translations):
    for platform, keys in translations["entity"].items():
        for key, value in keys.items():
            assert "{" not in value["name"], f"{platform}.{key}: {value['name']}"
