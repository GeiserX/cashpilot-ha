"""Common fixtures and HA mocks for CashPilot tests."""

from __future__ import annotations

import sys
from types import ModuleType
from typing import Any
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch


# ---------------------------------------------------------------------------
# Stub out homeassistant modules BEFORE any custom_components import
# ---------------------------------------------------------------------------

class _FakeCoordinatorEntity:
    """Minimal stand-in for CoordinatorEntity."""

    def __init__(self, coordinator, *args, **kwargs):
        self.coordinator = coordinator

    def __class_getitem__(cls, item):
        return cls


class _FakeDataUpdateCoordinator:
    """Minimal stand-in for DataUpdateCoordinator."""

    def __init__(self, hass, logger, *, name, update_interval):
        self.hass = hass
        self.logger = logger
        self.name = name
        self.update_interval = update_interval
        self.data: dict[str, Any] = {}

    async def async_config_entry_first_refresh(self):
        pass

    async def async_request_refresh(self):
        pass

    def __class_getitem__(cls, item):
        return cls


class _FakeConfigFlow:
    """Minimal stand-in for ConfigFlow."""

    def __init__(self, *args, **kwargs):
        pass

    def __init_subclass__(cls, *, domain=None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._domain = domain

    async def async_set_unique_id(self, uid):
        self._unique_id = uid

    def _abort_if_unique_id_configured(self):
        pass

    def async_create_entry(self, *, title, data):
        return {"type": "create_entry", "title": title, "data": data}

    def async_show_form(self, *, step_id, data_schema, errors=None):
        return {"type": "form", "step_id": step_id, "errors": errors or {}}


class _FakeDeviceInfo(dict):
    """Minimal stand-in for DeviceInfo."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for k, v in kwargs.items():
            setattr(self, k, v)


class _FakeBinarySensorEntity:
    pass


class _FakeSensorEntity:
    pass


class _FakeButtonEntity:
    pass


class _FakeSwitchEntity:
    pass


class _FakeConfigEntry:
    """Minimal stand-in for ConfigEntry."""

    def __init__(self, entry_id="test_entry_id", data=None):
        self.entry_id = entry_id
        self.data = data or {}

    def __class_getitem__(cls, item):
        return cls


def _make_ha_mocks():
    """Create minimal mocks for homeassistant modules so imports work."""
    mods = {}

    # homeassistant core
    ha_mod = MagicMock()
    mods["homeassistant"] = ha_mod
    mods["homeassistant.core"] = MagicMock()

    # homeassistant.const
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

    # homeassistant.config_entries
    config_entries_mod = ModuleType("homeassistant.config_entries")
    config_entries_mod.ConfigEntry = _FakeConfigEntry
    config_entries_mod.ConfigFlow = _FakeConfigFlow
    config_entries_mod.ConfigFlowResult = dict
    mods["homeassistant.config_entries"] = config_entries_mod

    # homeassistant.helpers
    mods["homeassistant.helpers"] = MagicMock()
    mods["homeassistant.helpers.aiohttp_client"] = MagicMock()
    mods["homeassistant.helpers.entity_platform"] = MagicMock()

    # device_registry with real DeviceInfo
    device_registry_mod = ModuleType("homeassistant.helpers.device_registry")
    device_registry_mod.DeviceInfo = _FakeDeviceInfo
    mods["homeassistant.helpers.device_registry"] = device_registry_mod

    # update_coordinator with real base classes
    update_coord_mod = ModuleType("homeassistant.helpers.update_coordinator")
    update_coord_mod.CoordinatorEntity = _FakeCoordinatorEntity
    update_coord_mod.DataUpdateCoordinator = _FakeDataUpdateCoordinator
    update_coord_mod.UpdateFailed = type("UpdateFailed", (Exception,), {})
    mods["homeassistant.helpers.update_coordinator"] = update_coord_mod

    # homeassistant.data_entry_flow
    mods["homeassistant.data_entry_flow"] = MagicMock()

    # Component modules with real base classes
    binary_sensor_mod = ModuleType("homeassistant.components.binary_sensor")
    binary_sensor_mod.BinarySensorEntity = _FakeBinarySensorEntity
    binary_sensor_mod.BinarySensorDeviceClass = MagicMock()
    binary_sensor_mod.BinarySensorDeviceClass.RUNNING = "running"
    mods["homeassistant.components.binary_sensor"] = binary_sensor_mod

    sensor_mod = ModuleType("homeassistant.components.sensor")
    sensor_mod.SensorEntity = _FakeSensorEntity
    sensor_mod.SensorDeviceClass = MagicMock()
    sensor_mod.SensorDeviceClass.DATA_SIZE = "data_size"
    sensor_mod.SensorStateClass = MagicMock()
    sensor_mod.SensorStateClass.MEASUREMENT = "measurement"
    sensor_mod.SensorStateClass.TOTAL = "total"
    mods["homeassistant.components.sensor"] = sensor_mod

    button_mod = ModuleType("homeassistant.components.button")
    button_mod.ButtonEntity = _FakeButtonEntity
    mods["homeassistant.components.button"] = button_mod

    switch_mod = ModuleType("homeassistant.components.switch")
    switch_mod.SwitchEntity = _FakeSwitchEntity
    mods["homeassistant.components.switch"] = switch_mod

    mods["homeassistant.components"] = MagicMock()

    return mods


_ha_mocks = _make_ha_mocks()
for name, mod in _ha_mocks.items():
    sys.modules[name] = mod


# ---------------------------------------------------------------------------
# Mock data
# ---------------------------------------------------------------------------

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

ENTRY_ID = "test_entry_id"


def make_coordinator_data(
    summary=None,
    breakdown=None,
    services=None,
    health=None,
    fleet=None,
):
    """Build a coordinator.data dict from mock data."""
    from custom_components.cashpilot.const import (
        DATA_BREAKDOWN,
        DATA_FLEET,
        DATA_HEALTH,
        DATA_SERVICES,
        DATA_SUMMARY,
    )

    health_by_slug = {}
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


def make_mock_coordinator(data=None):
    """Create a mock coordinator with data populated."""
    from custom_components.cashpilot.coordinator import CashPilotCoordinator

    hass = MagicMock()
    client = AsyncMock()
    coord = CashPilotCoordinator(hass, client)
    coord.data = data or make_coordinator_data(
        summary=MOCK_SUMMARY,
        breakdown=MOCK_BREAKDOWN,
        services=MOCK_SERVICES,
        health=MOCK_HEALTH,
        fleet=MOCK_FLEET,
    )
    return coord
