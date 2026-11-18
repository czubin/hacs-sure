"""Config flow for Sure integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_SCAN_INTERVAL, CONF_URL
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .client import SureAuthError, SureClient, SureConnectionError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass, data: dict[str, Any]) -> dict[str, Any]:
    """Validate user credentials using SureClient."""
    session = async_get_clientsession(hass)
    client = SureClient(session, data[CONF_URL], data[CONF_API_KEY])

    try:
        await client.get_accounts()
    except SureAuthError:
        return {"error": "invalid_auth"}
    except SureConnectionError:
        return {"error": "cannot_connect"}
    except Exception as exc:
        _LOGGER.exception("Unexpected error connecting to Sure: %s", exc)
        return {"error": "unknown"}

    return {"title": "Sure"}


class SureConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sure."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            user_input[CONF_URL] = user_input[CONF_URL].rstrip("/")
            await self.async_set_unique_id(user_input[CONF_URL])
            self._abort_if_unique_id_configured()

            validation = await validate_input(self.hass, user_input)
            if "error" in validation:
                errors["base"] = validation["error"]
            else:
                return self.async_create_entry(
                    title=validation["title"],
                    data=user_input,
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_URL): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.URL)
                ),
                vol.Required(CONF_API_KEY): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return SureOptionsFlowHandler(config_entry)


class SureOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for Sure."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self._config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self._config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=current_interval,
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1,
                        max=1440,
                        step=1,
                        unit_of_measurement="min",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
