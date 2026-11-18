"""DataUpdateCoordinator for Sure integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import SureAuthError, SureClient, SureConnectionError, SureError

_LOGGER = logging.getLogger(__name__)


class SureDataUpdateCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Coordinates polling for Sure accounts."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: SureClient,
        scan_interval_minutes: int = 15,
    ) -> None:
        """Initialize the coordinator."""
        self.client = client
        super().__init__(
            hass,
            _LOGGER,
            name="Sure Finances Display",
            update_interval=timedelta(minutes=scan_interval_minutes),
        )

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Fetch accounts from client."""
        try:
            accounts = await self.client.get_accounts()
        except SureAuthError as err:
            raise ConfigEntryAuthFailed(err) from err
        except (SureConnectionError, SureError) as err:
            raise UpdateFailed(err) from err

        accounts_by_id = {}

        for acc in accounts:
            if acc.get("id"):
                accounts_by_id[acc["id"]] = acc

        return accounts_by_id
