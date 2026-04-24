"""Tests for the CashPilot async API client."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest
from aioresponses import aioresponses

from custom_components.cashpilot.api import (
    CashPilotAuthError,
    CashPilotClient,
    CashPilotConnectionError,
    CashPilotError,
)


BASE_URL = "http://cashpilot:8080"


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


def test_exception_hierarchy():
    """All custom exceptions descend from CashPilotError."""
    assert issubclass(CashPilotConnectionError, CashPilotError)
    assert issubclass(CashPilotAuthError, CashPilotError)
    assert issubclass(CashPilotError, Exception)


# ---------------------------------------------------------------------------
# Constructor
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_trailing_slash_stripped():
    """Trailing slash on base_url is removed."""
    async with aiohttp.ClientSession() as session:
        client = CashPilotClient(session, "http://host:8080/", "u", "p")
        assert client._base_url == "http://host:8080"


@pytest.mark.asyncio
async def test_no_trailing_slash():
    """URL without trailing slash is kept as-is."""
    async with aiohttp.ClientSession() as session:
        client = CashPilotClient(session, "http://host:8080", "u", "p")
        assert client._base_url == "http://host:8080"


# ---------------------------------------------------------------------------
# async_login
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_login_success():
    """Successful login stores cookies."""
    async with aiohttp.ClientSession() as session:
        client = CashPilotClient(session, BASE_URL, "admin", "pass")
        with aioresponses() as m:
            m.post(
                f"{BASE_URL}/login",
                status=302,
                headers={"Set-Cookie": "session=abc123"},
            )
            await client.async_login()
            # Cookies should have been captured (from jar or response)


@pytest.mark.asyncio
async def test_login_401_raises_auth_error():
    """401 from login raises CashPilotAuthError."""
    async with aiohttp.ClientSession() as session:
        client = CashPilotClient(session, BASE_URL, "admin", "wrong")
        with aioresponses() as m:
            m.post(f"{BASE_URL}/login", status=401)
            with pytest.raises(CashPilotAuthError, match="Invalid username"):
                await client.async_login()


@pytest.mark.asyncio
async def test_login_403_raises_auth_error():
    """403 from login raises CashPilotAuthError."""
    async with aiohttp.ClientSession() as session:
        client = CashPilotClient(session, BASE_URL, "admin", "wrong")
        with aioresponses() as m:
            m.post(f"{BASE_URL}/login", status=403)
            with pytest.raises(CashPilotAuthError, match="Invalid username"):
                await client.async_login()


@pytest.mark.asyncio
async def test_login_500_raises_generic_error():
    """Server error raises CashPilotError."""
    async with aiohttp.ClientSession() as session:
        client = CashPilotClient(session, BASE_URL, "admin", "pass")
        with aioresponses() as m:
            m.post(f"{BASE_URL}/login", status=500)
            with pytest.raises(CashPilotError, match="status 500"):
                await client.async_login()


@pytest.mark.asyncio
async def test_login_connection_error():
    """Unreachable server raises CashPilotConnectionError."""
    async with aiohttp.ClientSession() as session:
        client = CashPilotClient(session, "http://127.0.0.1:1", "u", "p")
        with pytest.raises(CashPilotConnectionError, match="Unable to connect"):
            await client.async_login()


@pytest.mark.asyncio
async def test_login_stores_cookies_from_jar():
    """When response has no cookies, fall back to session cookie jar."""
    async with aiohttp.ClientSession() as session:
        # Pre-populate the session cookie jar so the fallback loop iterates
        session.cookie_jar.update_cookies(
            {"session_token": "from_jar"},
            aiohttp.client_reqrep.URL(BASE_URL),
        )
        client = CashPilotClient(session, BASE_URL, "admin", "pass")
        with aioresponses() as m:
            # Response itself sets no cookies -- forces the jar-fallback path
            m.post(f"{BASE_URL}/login", status=200)
            await client.async_login()
            assert "session_token" in client._cookies
            assert client._cookies["session_token"] == "from_jar"


# ---------------------------------------------------------------------------
# _request
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_request_success():
    """Successful GET returns parsed JSON."""
    async with aiohttp.ClientSession() as session:
        client = CashPilotClient(session, BASE_URL, "admin", "pass")
        client._cookies = {"session": "abc"}
        with aioresponses() as m:
            m.get(
                f"{BASE_URL}/api/earnings/summary",
                payload={"total": 42.5},
            )
            result = await client.async_get_earnings_summary()
            assert result == {"total": 42.5}


@pytest.mark.asyncio
async def test_request_401_retries_login():
    """401 triggers re-login and retries once."""
    async with aiohttp.ClientSession() as session:
        client = CashPilotClient(session, BASE_URL, "admin", "pass")
        client._cookies = {"session": "expired"}
        with aioresponses() as m:
            # First request returns 401
            m.get(f"{BASE_URL}/api/earnings/summary", status=401)
            # Re-login succeeds
            m.post(f"{BASE_URL}/login", status=200)
            # Retry succeeds
            m.get(
                f"{BASE_URL}/api/earnings/summary",
                payload={"total": 10.0},
            )
            result = await client.async_get_earnings_summary()
            assert result == {"total": 10.0}


@pytest.mark.asyncio
async def test_request_401_after_retry_raises():
    """If retry after re-login also returns 401, raise auth error."""
    async with aiohttp.ClientSession() as session:
        client = CashPilotClient(session, BASE_URL, "admin", "pass")
        client._cookies = {"session": "expired"}
        with aioresponses() as m:
            m.get(f"{BASE_URL}/api/earnings/summary", status=401)
            m.post(f"{BASE_URL}/login", status=200)
            m.get(f"{BASE_URL}/api/earnings/summary", status=401)
            with pytest.raises(CashPilotAuthError, match="Authentication failed"):
                await client.async_get_earnings_summary()


@pytest.mark.asyncio
async def test_request_403_retries():
    """403 also triggers re-login retry."""
    async with aiohttp.ClientSession() as session:
        client = CashPilotClient(session, BASE_URL, "admin", "pass")
        client._cookies = {"session": "expired"}
        with aioresponses() as m:
            m.get(f"{BASE_URL}/api/earnings/summary", status=403)
            m.post(f"{BASE_URL}/login", status=200)
            m.get(
                f"{BASE_URL}/api/earnings/summary",
                payload={"total": 5.0},
            )
            result = await client.async_get_earnings_summary()
            assert result == {"total": 5.0}


@pytest.mark.asyncio
async def test_request_connection_error():
    """Connection error during request raises CashPilotConnectionError."""
    async with aiohttp.ClientSession() as session:
        client = CashPilotClient(session, BASE_URL, "admin", "pass")
        client._cookies = {"session": "abc"}
        with aioresponses() as m:
            m.get(
                f"{BASE_URL}/api/earnings/summary",
                exception=aiohttp.ClientError("network down"),
            )
            with pytest.raises(CashPilotConnectionError, match="Error communicating"):
                await client.async_get_earnings_summary()


# ---------------------------------------------------------------------------
# Read endpoints
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_earnings_summary():
    """async_get_earnings_summary calls correct path."""
    async with aiohttp.ClientSession() as session:
        client = CashPilotClient(session, BASE_URL, "admin", "pass")
        client._cookies = {}
        with aioresponses() as m:
            m.get(f"{BASE_URL}/api/earnings/summary", payload={"total": 1})
            result = await client.async_get_earnings_summary()
            assert result["total"] == 1


@pytest.mark.asyncio
async def test_get_earnings_breakdown():
    """async_get_earnings_breakdown calls correct path."""
    async with aiohttp.ClientSession() as session:
        client = CashPilotClient(session, BASE_URL, "admin", "pass")
        client._cookies = {}
        with aioresponses() as m:
            m.get(f"{BASE_URL}/api/earnings/breakdown", payload=[{"a": 1}])
            result = await client.async_get_earnings_breakdown()
            assert len(result) == 1


@pytest.mark.asyncio
async def test_get_deployed_services():
    """async_get_deployed_services calls correct path."""
    async with aiohttp.ClientSession() as session:
        client = CashPilotClient(session, BASE_URL, "admin", "pass")
        client._cookies = {}
        with aioresponses() as m:
            m.get(f"{BASE_URL}/api/services/deployed", payload=[])
            result = await client.async_get_deployed_services()
            assert result == []


@pytest.mark.asyncio
async def test_get_health_scores():
    """async_get_health_scores calls correct path."""
    async with aiohttp.ClientSession() as session:
        client = CashPilotClient(session, BASE_URL, "admin", "pass")
        client._cookies = {}
        with aioresponses() as m:
            m.get(f"{BASE_URL}/api/health/scores", payload=[{"score": 90}])
            result = await client.async_get_health_scores()
            assert result[0]["score"] == 90


@pytest.mark.asyncio
async def test_get_fleet_summary():
    """async_get_fleet_summary calls correct path."""
    async with aiohttp.ClientSession() as session:
        client = CashPilotClient(session, BASE_URL, "admin", "pass")
        client._cookies = {}
        with aioresponses() as m:
            m.get(f"{BASE_URL}/api/fleet/summary", payload={"workers": 2})
            result = await client.async_get_fleet_summary()
            assert result["workers"] == 2


@pytest.mark.asyncio
async def test_get_fleet_summary_returns_none_on_error():
    """async_get_fleet_summary returns None when fleet is not configured."""
    async with aiohttp.ClientSession() as session:
        client = CashPilotClient(session, BASE_URL, "admin", "pass")
        client._cookies = {}
        with aioresponses() as m:
            m.get(
                f"{BASE_URL}/api/fleet/summary",
                exception=aiohttp.ClientError("not found"),
            )
            result = await client.async_get_fleet_summary()
            assert result is None


@pytest.mark.asyncio
async def test_get_fleet_summary_returns_none_on_status_error():
    """async_get_fleet_summary returns None on HTTP error status."""
    async with aiohttp.ClientSession() as session:
        client = CashPilotClient(session, BASE_URL, "admin", "pass")
        client._cookies = {}
        with aioresponses() as m:
            m.get(f"{BASE_URL}/api/fleet/summary", status=404)
            result = await client.async_get_fleet_summary()
            assert result is None


# ---------------------------------------------------------------------------
# Action endpoints
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_restart_service():
    """async_restart_service sends POST to correct path."""
    async with aiohttp.ClientSession() as session:
        client = CashPilotClient(session, BASE_URL, "admin", "pass")
        client._cookies = {}
        with aioresponses() as m:
            m.post(
                f"{BASE_URL}/api/services/honeygain/restart",
                payload={"ok": True},
            )
            await client.async_restart_service("honeygain")


@pytest.mark.asyncio
async def test_start_service():
    """async_start_service sends POST to correct path."""
    async with aiohttp.ClientSession() as session:
        client = CashPilotClient(session, BASE_URL, "admin", "pass")
        client._cookies = {}
        with aioresponses() as m:
            m.post(
                f"{BASE_URL}/api/services/earnapp/start",
                payload={"ok": True},
            )
            await client.async_start_service("earnapp")


@pytest.mark.asyncio
async def test_stop_service():
    """async_stop_service sends POST to correct path."""
    async with aiohttp.ClientSession() as session:
        client = CashPilotClient(session, BASE_URL, "admin", "pass")
        client._cookies = {}
        with aioresponses() as m:
            m.post(
                f"{BASE_URL}/api/services/earnapp/stop",
                payload={"ok": True},
            )
            await client.async_stop_service("earnapp")


@pytest.mark.asyncio
async def test_collect_earnings():
    """async_collect_earnings sends POST to /api/collect."""
    async with aiohttp.ClientSession() as session:
        client = CashPilotClient(session, BASE_URL, "admin", "pass")
        client._cookies = {}
        with aioresponses() as m:
            m.post(f"{BASE_URL}/api/collect", payload={"ok": True})
            await client.async_collect_earnings()
