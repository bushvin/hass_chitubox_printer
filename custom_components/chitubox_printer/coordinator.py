import logging

import homeassistant.util.dt as dt_util
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from sdcpapi import SDCPWSClient

from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class SDCPDeviceCoordinator(DataUpdateCoordinator):
    """Gather data from the SDCP Device"""

    client: SDCPWSClient
    entry: ConfigEntry

    def __init__(self, hass, client):
        """Initialize update coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
        )
        self.client = client

    async def _async_setup(self):
        """Do nothing actually"""

    async def _async_update_data(self):
        """Initiate sensor updates."""
        self.client.request_attributes_update()
        self.client.request_status_update()

        return {
            "last_read_time": dt_util.utcnow(),
        }
