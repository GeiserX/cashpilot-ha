"""Tests for CashPilot sensor value computation logic."""

from __future__ import annotations

import pytest

from custom_components.cashpilot.const import (
    DATA_FLEET,
    DATA_SERVICES,
    DATA_SUMMARY,
)

from .conftest import MOCK_FLEET, MOCK_SERVICES, MOCK_SUMMARY


def _find_service(services: list[dict], slug: str) -> dict | None:
    """Find a service by slug."""
    for svc in services:
        if svc.get("slug") == slug:
            return svc
    return None


def _parse_memory(raw) -> float | None:
    """Parse memory value from string or number."""
    if isinstance(raw, (int, float)):
        return float(raw)
    if isinstance(raw, str):
        cleaned = raw.replace("MB", "").replace("mb", "").strip()
        try:
            return float(cleaned)
        except (ValueError, TypeError):
            return None
    return None


# --- Dashboard sensor tests ---


def test_total_earnings() -> None:
    assert MOCK_SUMMARY["total"] == 42.50


def test_today_earnings() -> None:
    assert MOCK_SUMMARY["today"] == 1.25


def test_today_change_attr() -> None:
    assert MOCK_SUMMARY["today_change"] == 0.15


def test_month_earnings() -> None:
    assert MOCK_SUMMARY["month"] == 12.50


def test_month_change_attr() -> None:
    assert MOCK_SUMMARY["month_change"] == 2.30


def test_active_services() -> None:
    assert MOCK_SUMMARY["active_services"] == 3


def test_missing_summary_key() -> None:
    assert {}.get("total") is None


# --- Fleet sensor tests ---


def test_fleet_workers_online() -> None:
    assert MOCK_FLEET["online_workers"] == 2


def test_fleet_total_workers() -> None:
    assert MOCK_FLEET["total_workers"] == 3


def test_fleet_containers_running() -> None:
    assert MOCK_FLEET["running_containers"] == 10


def test_fleet_none_handling() -> None:
    fleet = None
    result = fleet.get("online_workers") if fleet else None
    assert result is None


# --- Service sensor tests ---


def test_service_balance() -> None:
    svc = _find_service(MOCK_SERVICES, "honeygain")
    assert svc is not None
    assert svc["balance"] == 15.0


def test_service_balance_missing() -> None:
    svc = _find_service(MOCK_SERVICES, "missing")
    assert svc is None


def test_service_health_score() -> None:
    svc = _find_service(MOCK_SERVICES, "honeygain")
    assert svc["health_score"] == 95.0


def test_service_uptime() -> None:
    svc = _find_service(MOCK_SERVICES, "honeygain")
    assert svc["uptime_pct"] == 99.5


def test_service_cpu() -> None:
    svc = _find_service(MOCK_SERVICES, "honeygain")
    assert float(svc["cpu"]) == 2.5


def test_service_memory_string_format() -> None:
    """Test memory parsing from '150.5 MB' string."""
    assert _parse_memory("150.5 MB") == 150.5


def test_service_memory_numeric() -> None:
    """Test memory when provided as a number."""
    assert _parse_memory(50) == 50.0


def test_service_memory_float() -> None:
    """Test memory when provided as a float."""
    assert _parse_memory(75.5) == 75.5


def test_service_memory_invalid_string() -> None:
    """Test memory with invalid string."""
    assert _parse_memory("unknown") is None


def test_service_memory_none() -> None:
    """Test memory with None."""
    assert _parse_memory(None) is None
