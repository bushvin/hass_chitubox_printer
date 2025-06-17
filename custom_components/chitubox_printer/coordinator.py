import logging
from dataclasses import dataclass

import homeassistant.util.dt as dt_util
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


@dataclass
class CurrentTaskData:
    thumbnail_url: str = STATE_UNKNOWN


@dataclass
class StatusData:
    machine_status = [STATE_UNKNOWN]
    print_status: str = STATE_UNKNOWN
    machine_previous_status: str = STATE_UNKNOWN


@dataclass
class CoordinatorData:
    current_task: CurrentTaskData
    status: StatusData


class SDCPDeviceCoordinator(DataUpdateCoordinator):
    """Gather data from the SDCP Device"""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize update coordinator."""
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self):
        """Initiate sensor updates."""
        return {
            "last_read_time": dt_util.utcnow(),
        }
