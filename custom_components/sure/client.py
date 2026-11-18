"""API client for Sure."""
from __future__ import annotations

from typing import Any

import aiohttp


class SureError(Exception):
    """Generic Sure API error."""


class SureAuthError(SureError):
    """Authentication failed (invalid API key)."""


class SureConnectionError(SureError):
    """Connection or network error."""


class SureClient:

    def __init__(self, session: aiohttp.ClientSession, url: str, api_key: str) -> None:
        self.session = session
        self.url = url.rstrip("/")
        self.api_key = api_key

    async def get_accounts(self) -> list[dict[str, Any]]:
        try:
            async with self.session.get(
                f"{self.url}/api/v1/accounts?per_page=50",
                headers={"X-Api-Key": self.api_key, "Accept": "application/json"},
                timeout=aiohttp.ClientTimeout(total=20),
            ) as resp:

                if resp.status in (401, 403):
                    raise SureAuthError("Invalid or unauthorized API key")

                if resp.status != 200:
                    raise SureError(f"HTTP {resp.status}: {await resp.text()}")

                return (await resp.json()).get("accounts", [])

        except (aiohttp.ClientError, TimeoutError) as err:
            raise SureConnectionError(err) from err
