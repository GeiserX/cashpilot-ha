"""Tests for CashPilot binary sensor logic."""

from __future__ import annotations

import pytest

from .conftest import MOCK_SERVICES


def _is_service_running(services: list[dict], slug: str) -> bool | None:
    """Replicate the binary sensor is_on logic."""
    for svc in services:
        if svc.get("slug") == slug:
            status = svc.get("container_status", "")
            return status.lower() == "running"
    return None


def test_service_running() -> None:
    """Test is True when container is running."""
    assert _is_service_running(MOCK_SERVICES, "honeygain") is True


def test_service_stopped() -> None:
    """Test is False when container is stopped."""
    assert _is_service_running(MOCK_SERVICES, "earnapp") is False


def test_service_missing() -> None:
    """Test None when slug is not found."""
    assert _is_service_running(MOCK_SERVICES, "missing") is None


def test_empty_services() -> None:
    """Test None with empty service list."""
    assert _is_service_running([], "honeygain") is None
