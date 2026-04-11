"""Tests for CashPilot switch logic."""

from __future__ import annotations

import pytest

from .conftest import MOCK_SERVICES


def _is_switch_on(services: list[dict], slug: str) -> bool | None:
    """Replicate the switch is_on logic."""
    for svc in services:
        if svc.get("slug") == slug:
            return svc.get("container_status", "").lower() == "running"
    return None


def test_switch_on_running() -> None:
    """Test switch is on when container is running."""
    assert _is_switch_on(MOCK_SERVICES, "honeygain") is True


def test_switch_off_stopped() -> None:
    """Test switch is off when container is stopped."""
    assert _is_switch_on(MOCK_SERVICES, "earnapp") is False


def test_switch_missing() -> None:
    """Test None when slug is not found."""
    assert _is_switch_on(MOCK_SERVICES, "missing") is None


def test_case_insensitive_status() -> None:
    """Test that status comparison is case-insensitive."""
    services = [{"slug": "test", "container_status": "Running"}]
    assert _is_switch_on(services, "test") is True


def test_empty_status() -> None:
    """Test False with empty status string."""
    services = [{"slug": "test", "container_status": ""}]
    assert _is_switch_on(services, "test") is False
