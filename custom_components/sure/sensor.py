"""Sensor platform for the Sure integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SureDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sure sensors from a config entry."""
    coordinator: SureDataUpdateCoordinator = (
        getattr(entry, "runtime_data", None) or hass.data[DOMAIN][entry.entry_id]
    )

    known_ids: set[str] = set()

    @callback
    def _sync_entities() -> None:
        new_ids = set(coordinator.data) - known_ids
        if new_ids:
            known_ids.update(new_ids)
            async_add_entities([SureSensor(coordinator, entry, acc_id) for acc_id in new_ids])

    _sync_entities()
    entry.async_on_unload(coordinator.async_add_listener(_sync_entities))


class SureSensor(CoordinatorEntity[SureDataUpdateCoordinator], SensorEntity):
    """Sensor representing a Sure account balance."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL
    _attr_suggested_display_precision = 2

    def __init__(
        self,
        coordinator: SureDataUpdateCoordinator,
        entry: ConfigEntry,
        account_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.account_id = account_id
        self._attr_unique_id = f"sure_{account_id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Sure Finances Display",
            configuration_url=coordinator.client.url,
        )

    @property
    def _account(self) -> dict[str, Any]:
        """Return the account dictionary."""
        return self.coordinator.data.get(self.account_id, {})

    @property
    def name(self) -> str:
        """Return the account name."""
        return self._account.get("name", "Account")

    @property
    def native_value(self) -> float | None:
        """Return account balance from balance_cents."""
        cents = self._account.get("balance_cents")
        return round(cents / 100.0, 2) if cents is not None else None

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the currency."""
        return self._account.get("currency")

    @property
    def available(self) -> bool:
        """Return True if account is available in coordinator data."""
        return super().available and self.account_id in self.coordinator.data
