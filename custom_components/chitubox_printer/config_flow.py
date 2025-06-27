"""Config flow for ChituBox Printer integration."""

import logging
import re
from time import sleep
from typing import Any, Optional

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_ID, CONF_NAME
from homeassistant.core import callback
from sdcpapi.exceptions import DeviceInvalidHostname, DeviceResolutionError
from sdcpapi.wsclient import SDCPWSClient

from .const import (
    CONF_BRAND,
    CONF_MACHINE_BRAND_ID,
    CONF_MAINBOARD_ID,
    CONF_MODEL,
    CONFIG_SCHEMA,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class ChituBoxPrinterConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ChituBox Printer integration."""

    VERSION = 2
    MINOR_VERSION = 0

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

        self.user_input[CONF_MACHINE_BRAND_ID] = self.printer.device.machine_brand_id
        self.user_input[CONF_MAINBOARD_ID] = self.printer.device.mainboard_id
        self.user_input[CONF_MODEL] = self.printer.device.model
        self.user_input[CONF_BRAND] = self.printer.device.brand

        await self.async_set_unique_id(
            self.user_input[CONF_ID], raise_on_progress=False
        )
        self._abort_if_unique_id_configured()
        result = self.async_create_entry(
            title=self.user_input[CONF_NAME], data=self.user_input
        )
        return result

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""

        errors = {}
        self.user_input = user_input

        if user_input is not None:
            for entry in self._async_current_entries():
                if (
                    user_input[CONF_HOST].lower() == entry.data[CONF_HOST].lower()
                    or user_input[CONF_NAME].lower() == entry.data[CONF_NAME].lower()
                ):
                    return self.async_abort(reason="already_configured")

            if (
                error := await self.hass.async_add_executor_job(self.validate_input)
            ) is None:

                self.user_input[CONF_ID] = re.sub(
                    r"[._-]+", "_", self.user_input[CONF_HOST]
                )

                await self._finish_config()
                return self._async_get_entry()

            errors["base"] = error
        return self.async_show_form(
            step_id="user", data_schema=CONFIG_SCHEMA, errors=errors
        )

    def validate_input(self):
        """Validate the host/ip address."""

        try:
            self.printer = SDCPWSClient(self.user_input[CONF_HOST], logger=_LOGGER)
        except DeviceInvalidHostname:
            return "invalid_hostname"
        except DeviceResolutionError:
            return "invalid_hostname"

        timeout = 10
        while timeout > 0:
            if self.printer.device.brand is None and self.printer.device.model is None:
                timeout = timeout - 1
                sleep(1)
            else:
                return None

        self.printer.disconnect()
        return "cannot_connect"
