"""Async HTTP client for the CashPilot API."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)


class CashPilotError(Exception):
    """Base exception for CashPilot API errors."""


class CashPilotConnectionError(CashPilotError):
    """Raised when the API is unreachable."""


class CashPilotAuthError(CashPilotError):
    """Raised when authentication fails."""


class CashPilotPermissionError(CashPilotError):
    """Raised when the user lacks sufficient permissions."""


class CashPilotClient:
    """Async client for communicating with a CashPilot instance."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        base_url: str,
        username: str,
        password: str,
    ) -> None:
        """Initialize the client."""
        self._session = session
        self._base_url = base_url.rstrip("/")
        self._username = username
        self._password = password
        self._cookies: dict[str, str] = {}

    async def async_login(self) -> None:
        """Authenticate with CashPilot and store the session cookie."""
        url = f"{self._base_url}/login"
        payload = aiohttp.FormData()
        payload.add_field("username", self._username)
        payload.add_field("password", self._password)

        try:
            async with self._session.post(
                url,
                data=payload,
                allow_redirects=False,
            ) as resp:
                if resp.status in (401, 403):
                    raise CashPilotAuthError("Invalid username or password")
                if resp.status >= 400:
                    raise CashPilotError(
                        f"Login failed with status {resp.status}"
                    )
                # Store cookies from the response for subsequent requests
                self._cookies = {
                    cookie.key: cookie.value
                    for cookie in resp.cookies.values()
                }
                if not self._cookies:
                    # Some setups may redirect on success; check for session
                    # cookie in the client session jar instead.
                    for cookie in self._session.cookie_jar:
                        self._cookies[cookie.key] = cookie.value
        except aiohttp.ClientError as err:
            raise CashPilotConnectionError(
                f"Unable to connect to CashPilot at {self._base_url}"
            ) from err

    async def _request(
        self,
        method: str,
        path: str,
        *,
        retry_auth: bool = True,
    ) -> Any:
        """Make an authenticated request, re-logging in on session expiry."""
        url = f"{self._base_url}{path}"
        try:
            async with self._session.request(
                method,
                url,
                cookies=self._cookies,
            ) as resp:
                if resp.status in (401, 403) and retry_auth:
                    _LOGGER.debug("Session expired, re-authenticating")
                    await self.async_login()
                    return await self._request(
                        method, path, retry_auth=False
                    )
                if resp.status == 403:
                    raise CashPilotPermissionError(
                        "Insufficient permissions"
                    )
                if resp.status == 401:
                    raise CashPilotAuthError("Authentication failed")
                resp.raise_for_status()
                return await resp.json()
        except aiohttp.ClientError as err:
            raise CashPilotConnectionError(
                f"Error communicating with CashPilot: {err}"
            ) from err

    # ---- Read endpoints ----

    async def async_get_earnings_summary(self) -> dict[str, Any]:
        """Fetch the earnings summary."""
        return await self._request("GET", "/api/earnings/summary")

    async def async_get_earnings_breakdown(self) -> list[dict[str, Any]]:
        """Fetch per-platform earnings breakdown."""
        return await self._request("GET", "/api/earnings/breakdown")

    async def async_get_deployed_services(self) -> list[dict[str, Any]]:
        """Fetch deployed services with status and resource usage."""
        return await self._request("GET", "/api/services/deployed")

    async def async_get_health_scores(self) -> list[dict[str, Any]]:
        """Fetch health scores for all services."""
        return await self._request("GET", "/api/health/scores")

    async def async_get_fleet_summary(self) -> dict[str, Any] | None:
        """Fetch fleet summary. Returns None if fleet is not configured."""
        try:
            return await self._request("GET", "/api/fleet/summary")
        except (CashPilotError, aiohttp.ClientResponseError):
            _LOGGER.debug("Fleet summary unavailable, skipping")
            return None

    # ---- Action endpoints ----

    async def async_restart_service(self, slug: str) -> None:
        """Restart a deployed service."""
        await self._request("POST", f"/api/services/{slug}/restart")

    async def async_start_service(self, slug: str) -> None:
        """Start a deployed service."""
        await self._request("POST", f"/api/services/{slug}/start")

    async def async_stop_service(self, slug: str) -> None:
        """Stop a deployed service."""
        await self._request("POST", f"/api/services/{slug}/stop")

    async def async_collect_earnings(self) -> None:
        """Trigger a manual earnings collection."""
        await self._request("POST", "/api/collect")
