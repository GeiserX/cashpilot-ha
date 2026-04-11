"""Common fixtures and HA mocks for CashPilot tests."""

from __future__ import annotations

import sys
from types import ModuleType
from unittest.mock import MagicMock


def _make_ha_mocks():
    """Create minimal mocks for homeassistant modules so imports work."""
    mods = {}

    mods["homeassistant"] = MagicMock()
    mods["homeassistant.core"] = MagicMock()

    const = ModuleType("homeassistant.const")
    const.Platform = MagicMock()
    const.Platform.BINARY_SENSOR = "binary_sensor"
    const.Platform.BUTTON = "button"
    const.Platform.SENSOR = "sensor"
    const.Platform.SWITCH = "switch"
    const.EntityCategory = MagicMock()
    const.EntityCategory.DIAGNOSTIC = "diagnostic"
    const.PERCENTAGE = "%"
    const.UnitOfInformation = MagicMock()
    const.UnitOfInformation.MEGABYTES = "MB"
    mods["homeassistant.const"] = const

    mods["homeassistant.config_entries"] = MagicMock()

    for mod_name in [
        "homeassistant.helpers",
        "homeassistant.helpers.aiohttp_client",
        "homeassistant.helpers.device_registry",
        "homeassistant.helpers.entity_platform",
        "homeassistant.helpers.update_coordinator",
    ]:
        mods[mod_name] = MagicMock()

    sensor_mod = MagicMock()
    sensor_mod.SensorDeviceClass = MagicMock()
    sensor_mod.SensorDeviceClass.DATA_SIZE = "data_size"
    sensor_mod.SensorStateClass = MagicMock()
    sensor_mod.SensorStateClass.MEASUREMENT = "measurement"
    sensor_mod.SensorStateClass.TOTAL = "total"
    mods["homeassistant.components"] = MagicMock()
    mods["homeassistant.components.sensor"] = sensor_mod
    mods["homeassistant.components.binary_sensor"] = MagicMock()
    mods["homeassistant.components.button"] = MagicMock()
    mods["homeassistant.components.switch"] = MagicMock()
    mods["homeassistant.data_entry_flow"] = MagicMock()

    return mods


_ha_mocks = _make_ha_mocks()
for name, mod in _ha_mocks.items():
    sys.modules[name] = mod


MOCK_SUMMARY = {
    "total": 42.50,
    "today": 1.25,
    "today_change": 0.15,
    "month": 12.50,
    "month_change": 2.30,
    "active_services": 3,
}

MOCK_BREAKDOWN = [
    {"platform": "honeygain", "balance": 15.0},
    {"platform": "earnapp", "balance": 27.5},
]

MOCK_SERVICES = [
    {
        "slug": "honeygain",
        "name": "Honeygain",
        "balance": 15.0,
        "health_score": 95.0,
        "uptime_pct": 99.5,
        "cpu": 2.5,
        "memory": "150.5 MB",
        "container_status": "running",
    },
    {
        "slug": "earnapp",
        "name": "EarnApp",
        "balance": 27.5,
        "health_score": 80.0,
        "uptime_pct": 98.0,
        "cpu": 1.0,
        "memory": 50,
        "container_status": "stopped",
    },
]

MOCK_HEALTH = [
    {"slug": "honeygain", "score": 95},
    {"slug": "earnapp", "score": 80},
]

MOCK_FLEET = {
    "online_workers": 2,
    "total_workers": 3,
    "running_containers": 10,
    "total_containers": 12,
}
