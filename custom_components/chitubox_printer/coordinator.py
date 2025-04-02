import logging

import homeassistant.util.dt as dt_util
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from sdcpapi.wsclient import SDCPWSClient

from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class SDCPDeviceCoordinator(DataUpdateCoordinator):
    """Gather data from the SDCP Device"""

    client: SDCPWSClient
    entry: ConfigEntry

    def __init__(self, hass, client):
        """Initialize update coordinator."""

        def _update_method():
            """Update method to make sure everything works correctly"""
            return True

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.client = client

    async def _async_setup(self):
        """Do nothing actually"""
        return {
            "setup_time": dt_util.utcnow(),
        }

    async def _async_update_data(self):
        """Initiate sensor updates."""
        return {
            "last_read_time": dt_util.utcnow(),
        }
