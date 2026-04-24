"""Tests for CashPilot sensor platform."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.cashpilot.const import (
    DATA_FLEET,
    DATA_SERVICES,
    DATA_SUMMARY,
    DOMAIN,
)
from custom_components.cashpilot.sensor import (
    CashPilotActiveServicesSensor,
    CashPilotFleetContainersSensor,
    CashPilotFleetWorkersSensor,
    CashPilotMonthEarningsSensor,
    CashPilotServiceBalanceSensor,
    CashPilotServiceCpuSensor,
    CashPilotServiceHealthSensor,
    CashPilotServiceMemorySensor,
    CashPilotServiceUptimeSensor,
    CashPilotTodayEarningsSensor,
    CashPilotTotalEarningsSensor,
    async_setup_entry,
)

from .conftest import (
    ENTRY_ID,
    MOCK_FLEET,
    MOCK_SERVICES,
    MOCK_SUMMARY,
    make_coordinator_data,
    make_mock_coordinator,
)


# ---------------------------------------------------------------------------
# async_setup_entry
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_setup_entry_with_fleet_and_services():
    """Setup creates dashboard + fleet + per-service sensors."""
    coord = make_mock_coordinator()
    hass = MagicMock()
    hass.data = {DOMAIN: {ENTRY_ID: coord}}
    entry = MagicMock()
    entry.entry_id = ENTRY_ID

    added = []
    async_add_entities = MagicMock(side_effect=lambda entities: added.extend(entities))

    await async_setup_entry(hass, entry, async_add_entities)

    # 4 dashboard + 2 fleet + 5*2 per-service = 16
    assert len(added) == 16


@pytest.mark.asyncio
async def test_setup_entry_without_fleet():
    """No fleet sensors when fleet data is None."""
    data = make_coordinator_data(
        summary=MOCK_SUMMARY,
        services=MOCK_SERVICES,
        fleet=None,
    )
    coord = make_mock_coordinator(data=data)
    hass = MagicMock()
    hass.data = {DOMAIN: {ENTRY_ID: coord}}
    entry = MagicMock()
    entry.entry_id = ENTRY_ID

    added = []
    async_add_entities = MagicMock(side_effect=lambda entities: added.extend(entities))

    await async_setup_entry(hass, entry, async_add_entities)

    # 4 dashboard + 0 fleet + 5*2 per-service = 14
    assert len(added) == 14


@pytest.mark.asyncio
async def test_setup_entry_no_services():
    """Only dashboard sensors when no services."""
    data = make_coordinator_data(summary=MOCK_SUMMARY, fleet=MOCK_FLEET)
    coord = make_mock_coordinator(data=data)
    hass = MagicMock()
    hass.data = {DOMAIN: {ENTRY_ID: coord}}
    entry = MagicMock()
    entry.entry_id = ENTRY_ID

    added = []
    async_add_entities = MagicMock(side_effect=lambda entities: added.extend(entities))

    await async_setup_entry(hass, entry, async_add_entities)

    # 4 dashboard + 2 fleet = 6
    assert len(added) == 6


@pytest.mark.asyncio
async def test_setup_entry_skips_empty_slug():
    """Services with empty slug are skipped."""
    data = make_coordinator_data(
        summary=MOCK_SUMMARY,
        services=[{"slug": "", "name": "NoSlug"}, {"slug": "ok", "name": "OK"}],
    )
    coord = make_mock_coordinator(data=data)
    hass = MagicMock()
    hass.data = {DOMAIN: {ENTRY_ID: coord}}
    entry = MagicMock()
    entry.entry_id = ENTRY_ID

    added = []
    async_add_entities = MagicMock(side_effect=lambda entities: added.extend(entities))

    await async_setup_entry(hass, entry, async_add_entities)

    # 4 dashboard + 5*1 per-service = 9
    assert len(added) == 9


# ---------------------------------------------------------------------------
# Dashboard sensors: TotalEarnings
# ---------------------------------------------------------------------------


def test_total_earnings_unique_id():
    coord = make_mock_coordinator()
    s = CashPilotTotalEarningsSensor(coord, ENTRY_ID)
    assert s._attr_unique_id == f"{ENTRY_ID}_total_earnings"


def test_total_earnings_value():
    coord = make_mock_coordinator()
    s = CashPilotTotalEarningsSensor(coord, ENTRY_ID)
    assert s.native_value == 42.50


def test_total_earnings_none():
    data = make_coordinator_data()
    coord = make_mock_coordinator(data=data)
    s = CashPilotTotalEarningsSensor(coord, ENTRY_ID)
    assert s.native_value is None


def test_total_earnings_icon():
    coord = make_mock_coordinator()
    s = CashPilotTotalEarningsSensor(coord, ENTRY_ID)
    assert s._attr_icon == "mdi:currency-usd"


# ---------------------------------------------------------------------------
# Dashboard sensors: TodayEarnings
# ---------------------------------------------------------------------------


def test_today_earnings_value():
    coord = make_mock_coordinator()
    s = CashPilotTodayEarningsSensor(coord, ENTRY_ID)
    assert s.native_value == 1.25


def test_today_earnings_unique_id():
    coord = make_mock_coordinator()
    s = CashPilotTodayEarningsSensor(coord, ENTRY_ID)
    assert s._attr_unique_id == f"{ENTRY_ID}_today_earnings"


def test_today_earnings_extra_attrs_with_change():
    coord = make_mock_coordinator()
    s = CashPilotTodayEarningsSensor(coord, ENTRY_ID)
    attrs = s.extra_state_attributes
    assert attrs == {"change": 0.15}


def test_today_earnings_extra_attrs_no_change():
    data = make_coordinator_data(summary={"today": 1.0})
    coord = make_mock_coordinator(data=data)
    s = CashPilotTodayEarningsSensor(coord, ENTRY_ID)
    assert s.extra_state_attributes == {}


# ---------------------------------------------------------------------------
# Dashboard sensors: MonthEarnings
# ---------------------------------------------------------------------------


def test_month_earnings_value():
    coord = make_mock_coordinator()
    s = CashPilotMonthEarningsSensor(coord, ENTRY_ID)
    assert s.native_value == 12.50


def test_month_earnings_unique_id():
    coord = make_mock_coordinator()
    s = CashPilotMonthEarningsSensor(coord, ENTRY_ID)
    assert s._attr_unique_id == f"{ENTRY_ID}_month_earnings"


def test_month_earnings_extra_attrs_with_change():
    coord = make_mock_coordinator()
    s = CashPilotMonthEarningsSensor(coord, ENTRY_ID)
    attrs = s.extra_state_attributes
    assert attrs == {"change": 2.30}


def test_month_earnings_extra_attrs_no_change():
    data = make_coordinator_data(summary={"month": 5.0})
    coord = make_mock_coordinator(data=data)
    s = CashPilotMonthEarningsSensor(coord, ENTRY_ID)
    assert s.extra_state_attributes == {}


# ---------------------------------------------------------------------------
# Dashboard sensors: ActiveServices
# ---------------------------------------------------------------------------


def test_active_services_value():
    coord = make_mock_coordinator()
    s = CashPilotActiveServicesSensor(coord, ENTRY_ID)
    assert s.native_value == 3


def test_active_services_unique_id():
    coord = make_mock_coordinator()
    s = CashPilotActiveServicesSensor(coord, ENTRY_ID)
    assert s._attr_unique_id == f"{ENTRY_ID}_active_services"


def test_active_services_none():
    data = make_coordinator_data()
    coord = make_mock_coordinator(data=data)
    s = CashPilotActiveServicesSensor(coord, ENTRY_ID)
    assert s.native_value is None


# ---------------------------------------------------------------------------
# Fleet sensors: Workers
# ---------------------------------------------------------------------------


def test_fleet_workers_value():
    coord = make_mock_coordinator()
    s = CashPilotFleetWorkersSensor(coord, ENTRY_ID)
    assert s.native_value == 2


def test_fleet_workers_unique_id():
    coord = make_mock_coordinator()
    s = CashPilotFleetWorkersSensor(coord, ENTRY_ID)
    assert s._attr_unique_id == f"{ENTRY_ID}_fleet_workers_online"


def test_fleet_workers_none_when_no_fleet():
    data = make_coordinator_data(fleet=None)
    coord = make_mock_coordinator(data=data)
    s = CashPilotFleetWorkersSensor(coord, ENTRY_ID)
    assert s.native_value is None


def test_fleet_workers_extra_attrs():
    coord = make_mock_coordinator()
    s = CashPilotFleetWorkersSensor(coord, ENTRY_ID)
    assert s.extra_state_attributes == {"total_workers": 3}


def test_fleet_workers_extra_attrs_no_fleet():
    data = make_coordinator_data(fleet=None)
    coord = make_mock_coordinator(data=data)
    s = CashPilotFleetWorkersSensor(coord, ENTRY_ID)
    assert s.extra_state_attributes == {}


def test_fleet_workers_extra_attrs_no_total():
    data = make_coordinator_data(fleet={"online_workers": 1})
    coord = make_mock_coordinator(data=data)
    s = CashPilotFleetWorkersSensor(coord, ENTRY_ID)
    assert s.extra_state_attributes == {}


# ---------------------------------------------------------------------------
# Fleet sensors: Containers
# ---------------------------------------------------------------------------


def test_fleet_containers_value():
    coord = make_mock_coordinator()
    s = CashPilotFleetContainersSensor(coord, ENTRY_ID)
    assert s.native_value == 10


def test_fleet_containers_unique_id():
    coord = make_mock_coordinator()
    s = CashPilotFleetContainersSensor(coord, ENTRY_ID)
    assert s._attr_unique_id == f"{ENTRY_ID}_fleet_containers_running"


def test_fleet_containers_none_when_no_fleet():
    data = make_coordinator_data(fleet=None)
    coord = make_mock_coordinator(data=data)
    s = CashPilotFleetContainersSensor(coord, ENTRY_ID)
    assert s.native_value is None


def test_fleet_containers_extra_attrs():
    coord = make_mock_coordinator()
    s = CashPilotFleetContainersSensor(coord, ENTRY_ID)
    assert s.extra_state_attributes == {"total_containers": 12}


def test_fleet_containers_extra_attrs_no_fleet():
    data = make_coordinator_data(fleet=None)
    coord = make_mock_coordinator(data=data)
    s = CashPilotFleetContainersSensor(coord, ENTRY_ID)
    assert s.extra_state_attributes == {}


def test_fleet_containers_extra_attrs_no_total():
    data = make_coordinator_data(fleet={"running_containers": 5})
    coord = make_mock_coordinator(data=data)
    s = CashPilotFleetContainersSensor(coord, ENTRY_ID)
    assert s.extra_state_attributes == {}


# ---------------------------------------------------------------------------
# Per-service: Balance
# ---------------------------------------------------------------------------


def test_service_balance_value():
    coord = make_mock_coordinator()
    s = CashPilotServiceBalanceSensor(coord, ENTRY_ID, "honeygain", "Honeygain")
    assert s.native_value == 15.0


def test_service_balance_unique_id():
    coord = make_mock_coordinator()
    s = CashPilotServiceBalanceSensor(coord, ENTRY_ID, "honeygain", "Honeygain")
    assert s._attr_unique_id == f"{ENTRY_ID}_honeygain_balance"


def test_service_balance_missing_slug():
    coord = make_mock_coordinator()
    s = CashPilotServiceBalanceSensor(coord, ENTRY_ID, "missing", "Missing")
    assert s.native_value is None


# ---------------------------------------------------------------------------
# Per-service: HealthScore
# ---------------------------------------------------------------------------


def test_service_health_value():
    coord = make_mock_coordinator()
    s = CashPilotServiceHealthSensor(coord, ENTRY_ID, "honeygain", "Honeygain")
    assert s.native_value == 95.0


def test_service_health_unique_id():
    coord = make_mock_coordinator()
    s = CashPilotServiceHealthSensor(coord, ENTRY_ID, "honeygain", "Honeygain")
    assert s._attr_unique_id == f"{ENTRY_ID}_honeygain_health_score"


def test_service_health_missing_slug():
    coord = make_mock_coordinator()
    s = CashPilotServiceHealthSensor(coord, ENTRY_ID, "missing", "Missing")
    assert s.native_value is None


# ---------------------------------------------------------------------------
# Per-service: Uptime
# ---------------------------------------------------------------------------


def test_service_uptime_value():
    coord = make_mock_coordinator()
    s = CashPilotServiceUptimeSensor(coord, ENTRY_ID, "honeygain", "Honeygain")
    assert s.native_value == 99.5


def test_service_uptime_unique_id():
    coord = make_mock_coordinator()
    s = CashPilotServiceUptimeSensor(coord, ENTRY_ID, "honeygain", "Honeygain")
    assert s._attr_unique_id == f"{ENTRY_ID}_honeygain_uptime"


def test_service_uptime_missing_slug():
    coord = make_mock_coordinator()
    s = CashPilotServiceUptimeSensor(coord, ENTRY_ID, "missing", "Missing")
    assert s.native_value is None


# ---------------------------------------------------------------------------
# Per-service: CPU
# ---------------------------------------------------------------------------


def test_service_cpu_value():
    coord = make_mock_coordinator()
    s = CashPilotServiceCpuSensor(coord, ENTRY_ID, "honeygain", "Honeygain")
    assert s.native_value == 2.5


def test_service_cpu_unique_id():
    coord = make_mock_coordinator()
    s = CashPilotServiceCpuSensor(coord, ENTRY_ID, "honeygain", "Honeygain")
    assert s._attr_unique_id == f"{ENTRY_ID}_honeygain_cpu"


def test_service_cpu_missing_slug():
    coord = make_mock_coordinator()
    s = CashPilotServiceCpuSensor(coord, ENTRY_ID, "missing", "Missing")
    assert s.native_value is None


def test_service_cpu_invalid_value():
    """CPU with non-numeric value returns None."""
    data = make_coordinator_data(
        services=[{"slug": "test", "name": "Test", "cpu": "bad"}]
    )
    coord = make_mock_coordinator(data=data)
    s = CashPilotServiceCpuSensor(coord, ENTRY_ID, "test", "Test")
    assert s.native_value is None


def test_service_cpu_none_value():
    """CPU with None value returns None."""
    data = make_coordinator_data(
        services=[{"slug": "test", "name": "Test", "cpu": None}]
    )
    coord = make_mock_coordinator(data=data)
    s = CashPilotServiceCpuSensor(coord, ENTRY_ID, "test", "Test")
    assert s.native_value is None


def test_service_cpu_no_key():
    """CPU absent from data returns None."""
    data = make_coordinator_data(
        services=[{"slug": "test", "name": "Test"}]
    )
    coord = make_mock_coordinator(data=data)
    s = CashPilotServiceCpuSensor(coord, ENTRY_ID, "test", "Test")
    assert s.native_value is None


# ---------------------------------------------------------------------------
# Per-service: Memory
# ---------------------------------------------------------------------------


def test_service_memory_string():
    """Memory parsed from '150.5 MB' string."""
    coord = make_mock_coordinator()
    s = CashPilotServiceMemorySensor(coord, ENTRY_ID, "honeygain", "Honeygain")
    assert s.native_value == 150.5


def test_service_memory_numeric():
    """Memory from numeric value."""
    coord = make_mock_coordinator()
    s = CashPilotServiceMemorySensor(coord, ENTRY_ID, "earnapp", "EarnApp")
    assert s.native_value == 50.0


def test_service_memory_unique_id():
    coord = make_mock_coordinator()
    s = CashPilotServiceMemorySensor(coord, ENTRY_ID, "honeygain", "Honeygain")
    assert s._attr_unique_id == f"{ENTRY_ID}_honeygain_memory"


def test_service_memory_missing_slug():
    coord = make_mock_coordinator()
    s = CashPilotServiceMemorySensor(coord, ENTRY_ID, "missing", "Missing")
    assert s.native_value is None


def test_service_memory_invalid_string():
    """Memory with non-numeric string returns None."""
    data = make_coordinator_data(
        services=[{"slug": "test", "name": "Test", "memory": "unknown"}]
    )
    coord = make_mock_coordinator(data=data)
    s = CashPilotServiceMemorySensor(coord, ENTRY_ID, "test", "Test")
    assert s.native_value is None


def test_service_memory_lowercase_mb():
    """Memory parsed from '100 mb' (lowercase)."""
    data = make_coordinator_data(
        services=[{"slug": "test", "name": "Test", "memory": "100 mb"}]
    )
    coord = make_mock_coordinator(data=data)
    s = CashPilotServiceMemorySensor(coord, ENTRY_ID, "test", "Test")
    assert s.native_value == 100.0


def test_service_memory_float_value():
    """Memory from float value."""
    data = make_coordinator_data(
        services=[{"slug": "test", "name": "Test", "memory": 75.5}]
    )
    coord = make_mock_coordinator(data=data)
    s = CashPilotServiceMemorySensor(coord, ENTRY_ID, "test", "Test")
    assert s.native_value == 75.5


def test_service_memory_empty_string():
    """Memory from empty string returns default (empty string after strip)."""
    data = make_coordinator_data(
        services=[{"slug": "test", "name": "Test", "memory": ""}]
    )
    coord = make_mock_coordinator(data=data)
    s = CashPilotServiceMemorySensor(coord, ENTRY_ID, "test", "Test")
    assert s.native_value is None
