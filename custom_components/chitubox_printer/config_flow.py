"""Config flow for ChituBox Printer integration."""

import logging
import re
import socket
from typing import Any, Optional

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_ID, CONF_NAME
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from sdcpapi import SDCPWSClient
from sdcpapi.exceptions import SDCPDeviceError

from .const import (
    CONF_BRAND,
    CONF_MACHINE_BRAND_ID,
    CONF_MAINBOARD_ID,
    CONF_MODEL,
    DOMAIN,
)

# from requests.exceptions import ConnectionError as reConnectionError

_LOGGER = logging.getLogger(__name__)


def _validate_host(hostname):
    """Validate the host/ip address."""
    # TODO: try to connect to the machine...
    return True


class ChituBoxPrinterConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ChituBox Printer integration."""

    VERSION = 1
    # CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    _user_input: dict[str, Any] | None = None

    def __init__(self):
        self._host: Optional[str] = None
        self._name: Optional[str] = None
        self._uuid: Optional[str] = None
        self._user_input = {}
        self.user_input = None

    @callback
    def _async_get_entry(self):
        return self.async_create_entry(
            title=self.user_input[CONF_NAME], data=self.user_input
        )

    async def _finish_config(self) -> ConfigFlowResult:
        """Finish the configuration setup."""
        existing_entry = await self.async_set_unique_id(self._uuid)
        # if existing_entry is not None:
        #     _LOGGER.debug("Updating existing entry %s" % existing_entry)
        #     self.hass.config_entries.async_update_entry(existing_entry, data=user_input)
        #     # Reload the config entry otherwise devices will remain unavailable
        #     self.hass.async_create_task(
        #         self.hass.config_entries.async_reload(existing_entry.entry_id),
        #     )

        #     return self.async_abort(reason="reauth_successful")

        try:
            printer = SDCPWSClient(self.user_input[CONF_HOST], logger=_LOGGER)
            self.user_input[CONF_MACHINE_BRAND_ID] = printer.device.machine_brand_id
            self.user_input[CONF_MAINBOARD_ID] = printer.device.mainboard_id
            self.user_input[CONF_MODEL] = printer.device.model
            self.user_input[CONF_BRAND] = printer.device.brand

        except SDCPDeviceError as e:
            _LOGGER.error("Failed to connect to printer")
            raise CannotConnect from e

        await self.async_set_unique_id(
            self.user_input[CONF_ID], raise_on_progress=False
        )
        self._abort_if_unique_id_configured()
        result = self.async_create_entry(
            title=self.user_input[CONF_NAME], data=self.user_input
        )
        _LOGGER.debug("result - %s" % result)
        return result

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        _LOGGER.debug("user_input - %s" % user_input)
        self.user_input = user_input

        if user_input is not None:
            self.user_input[CONF_ID] = re.sub(
                r"[._-]+", "_", self.user_input[CONF_HOST]
            )

            await self._finish_config()
            return self._async_get_entry()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME): cv.string,
                    vol.Required(CONF_HOST): cv.string,
                }
            ),
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
