"""Tests for the CashPilot config flow logic."""

from __future__ import annotations

import pytest

from custom_components.cashpilot.api import (
    CashPilotAuthError,
    CashPilotConnectionError,
    CashPilotError,
)
from custom_components.cashpilot.const import (
    CONF_PASSWORD,
    CONF_URL,
    CONF_USERNAME,
    DEFAULT_URL,
    DOMAIN,
)


def test_domain_constant() -> None:
    """Test the domain is correctly defined."""
    assert DOMAIN == "cashpilot"


def test_default_url() -> None:
    """Test the default URL."""
    assert DEFAULT_URL == "http://localhost:8080"


def test_conf_keys() -> None:
    """Test configuration keys."""
    assert CONF_URL == "url"
    assert CONF_USERNAME == "username"
    assert CONF_PASSWORD == "password"


def test_exception_hierarchy() -> None:
    """Test exception class hierarchy."""
    assert issubclass(CashPilotConnectionError, CashPilotError)
    assert issubclass(CashPilotAuthError, CashPilotError)


@pytest.mark.asyncio
async def test_connection_error_detection() -> None:
    """Test that unreachable servers are detected."""
    from custom_components.cashpilot.api import CashPilotClient
    import aiohttp

    async with aiohttp.ClientSession() as session:
        client = CashPilotClient(session, "http://127.0.0.1:1", "user", "pass")
        with pytest.raises(CashPilotConnectionError):
            await client.async_login()


@pytest.mark.asyncio
async def test_url_trailing_slash_stripped() -> None:
    """Test that trailing slashes are stripped."""
    from custom_components.cashpilot.api import CashPilotClient
    import aiohttp

    async with aiohttp.ClientSession() as session:
        client = CashPilotClient(session, "http://cashpilot:8080/", "user", "pass")
        assert client._base_url == "http://cashpilot:8080"
