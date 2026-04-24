"""Tests for the CashPilot config flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from custom_components.cashpilot.api import (
    CashPilotAuthError,
    CashPilotClient,
    CashPilotConnectionError,
    CashPilotError,
)
from custom_components.cashpilot.config_flow import CashPilotConfigFlow
from custom_components.cashpilot.const import (
    CONF_PASSWORD,
    CONF_URL,
    CONF_USERNAME,
    DEFAULT_URL,
    DOMAIN,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_domain_constant():
    assert DOMAIN == "cashpilot"


def test_default_url():
    assert DEFAULT_URL == "http://localhost:8080"


def test_conf_keys():
    assert CONF_URL == "url"
    assert CONF_USERNAME == "username"
    assert CONF_PASSWORD == "password"


def test_exception_hierarchy():
    assert issubclass(CashPilotConnectionError, CashPilotError)
    assert issubclass(CashPilotAuthError, CashPilotError)


def test_flow_version():
    """Config flow version is 1."""
    assert CashPilotConfigFlow.VERSION == 1


# ---------------------------------------------------------------------------
# async_step_user
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_step_user_no_input_shows_form():
    """First call with no input shows the form."""
    flow = CashPilotConfigFlow()
    result = await flow.async_step_user(user_input=None)
    assert result["type"] == "form"
    assert result["step_id"] == "user"
    assert result["errors"] == {}


@pytest.mark.asyncio
async def test_step_user_success():
    """Successful validation creates an entry."""
    flow = CashPilotConfigFlow()

    user_input = {
        CONF_URL: "http://cashpilot:8080/",
        CONF_USERNAME: "admin",
        CONF_PASSWORD: "secret",
    }

    with patch("custom_components.cashpilot.config_flow.aiohttp.ClientSession") as mock_session_cls:
        mock_session = AsyncMock()
        mock_session_cls.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        with patch("custom_components.cashpilot.config_flow.CashPilotClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.async_login = AsyncMock()
            mock_client.async_get_earnings_summary = AsyncMock(return_value={"total": 1})
            mock_client_cls.return_value = mock_client

            result = await flow.async_step_user(user_input=user_input)

    assert result["type"] == "create_entry"
    assert result["title"] == "CashPilot (http://cashpilot:8080)"
    assert result["data"][CONF_URL] == "http://cashpilot:8080"
    assert result["data"][CONF_USERNAME] == "admin"
    assert result["data"][CONF_PASSWORD] == "secret"


@pytest.mark.asyncio
async def test_step_user_connection_error():
    """Connection error shows cannot_connect."""
    flow = CashPilotConfigFlow()

    user_input = {
        CONF_URL: "http://cashpilot:8080",
        CONF_USERNAME: "admin",
        CONF_PASSWORD: "secret",
    }

    with patch("custom_components.cashpilot.config_flow.aiohttp.ClientSession") as mock_session_cls:
        mock_session = AsyncMock()
        mock_session_cls.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        with patch("custom_components.cashpilot.config_flow.CashPilotClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.async_login = AsyncMock(
                side_effect=CashPilotConnectionError("unreachable")
            )
            mock_client_cls.return_value = mock_client

            result = await flow.async_step_user(user_input=user_input)

    assert result["type"] == "form"
    assert result["errors"]["base"] == "cannot_connect"


@pytest.mark.asyncio
async def test_step_user_auth_error():
    """Auth error shows invalid_auth."""
    flow = CashPilotConfigFlow()

    user_input = {
        CONF_URL: "http://cashpilot:8080",
        CONF_USERNAME: "admin",
        CONF_PASSWORD: "wrong",
    }

    with patch("custom_components.cashpilot.config_flow.aiohttp.ClientSession") as mock_session_cls:
        mock_session = AsyncMock()
        mock_session_cls.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        with patch("custom_components.cashpilot.config_flow.CashPilotClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.async_login = AsyncMock(
                side_effect=CashPilotAuthError("bad creds")
            )
            mock_client_cls.return_value = mock_client

            result = await flow.async_step_user(user_input=user_input)

    assert result["type"] == "form"
    assert result["errors"]["base"] == "invalid_auth"


@pytest.mark.asyncio
async def test_step_user_unknown_error():
    """Unexpected exception shows unknown error."""
    flow = CashPilotConfigFlow()

    user_input = {
        CONF_URL: "http://cashpilot:8080",
        CONF_USERNAME: "admin",
        CONF_PASSWORD: "secret",
    }

    with patch("custom_components.cashpilot.config_flow.aiohttp.ClientSession") as mock_session_cls:
        mock_session = AsyncMock()
        mock_session_cls.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        with patch("custom_components.cashpilot.config_flow.CashPilotClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.async_login = AsyncMock(side_effect=RuntimeError("boom"))
            mock_client_cls.return_value = mock_client

            result = await flow.async_step_user(user_input=user_input)

    assert result["type"] == "form"
    assert result["errors"]["base"] == "unknown"


@pytest.mark.asyncio
async def test_step_user_strips_trailing_slash():
    """URL trailing slash is stripped before creating entry."""
    flow = CashPilotConfigFlow()

    user_input = {
        CONF_URL: "http://cashpilot:8080///",
        CONF_USERNAME: "admin",
        CONF_PASSWORD: "secret",
    }

    with patch("custom_components.cashpilot.config_flow.aiohttp.ClientSession") as mock_session_cls:
        mock_session = AsyncMock()
        mock_session_cls.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        with patch("custom_components.cashpilot.config_flow.CashPilotClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.async_login = AsyncMock()
            mock_client.async_get_earnings_summary = AsyncMock(return_value={})
            mock_client_cls.return_value = mock_client

            result = await flow.async_step_user(user_input=user_input)

    assert result["type"] == "create_entry"
    # Only one trailing slash is stripped by rstrip("/")
    assert "/" not in result["data"][CONF_URL][-1:]


@pytest.mark.asyncio
async def test_step_user_auth_error_on_summary():
    """Auth error during summary fetch shows invalid_auth."""
    flow = CashPilotConfigFlow()

    user_input = {
        CONF_URL: "http://cashpilot:8080",
        CONF_USERNAME: "admin",
        CONF_PASSWORD: "secret",
    }

    with patch("custom_components.cashpilot.config_flow.aiohttp.ClientSession") as mock_session_cls:
        mock_session = AsyncMock()
        mock_session_cls.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        with patch("custom_components.cashpilot.config_flow.CashPilotClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.async_login = AsyncMock()
            mock_client.async_get_earnings_summary = AsyncMock(
                side_effect=CashPilotAuthError("expired")
            )
            mock_client_cls.return_value = mock_client

            result = await flow.async_step_user(user_input=user_input)

    assert result["type"] == "form"
    assert result["errors"]["base"] == "invalid_auth"
