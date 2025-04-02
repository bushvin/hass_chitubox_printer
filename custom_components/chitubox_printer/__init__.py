"""The __init__ file for ChituBox Printer integration."""

import logging

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_HOST, CONF_ID, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from sdcpapi.wsclient import SDCPWSClient

from .const import (
    CONF_BRAND,
    CONF_MACHINE_BRAND_ID,
    CONF_MAINBOARD_ID,
    CONF_MODEL,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import SDCPDeviceCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Setup the integration from configuration.yaml"""
    _LOGGER.debug("hass - %s" % hass)
    if DOMAIN not in config:
        _LOGGER.debug("No config found in configuration.yaml")
        return True

    domain_config = config[DOMAIN]

    for conf in domain_config:
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": SOURCE_IMPORT},
                data={
                    CONF_NAME: conf[CONF_NAME],
                    CONF_HOST: conf[CONF_HOST],
                    CONF_ID: conf[CONF_ID],
                    CONF_MACHINE_BRAND_ID: conf[CONF_MACHINE_BRAND_ID],
                    CONF_MAINBOARD_ID: conf[CONF_MAINBOARD_ID],
                    CONF_MODEL: conf[CONF_MODEL],
                    CONF_BRAND: conf[CONF_BRAND],
                },
            )
        )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the ChituBox Printer from a config entry."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    client = SDCPWSClient(entry.data[CONF_HOST], logger=_LOGGER)

    coordinator = SDCPDeviceCoordinator(hass, client)

    entry.runtime_data = coordinator

    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        entry.runtime_data.client.disconnect()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
