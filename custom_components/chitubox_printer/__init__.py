"""
Custom integration to integrate SDCP based devices with Home Assistant

For more information about this integration, please refer to
https://github.com/bushvin/hass_chitubox_printer
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.image import ImageEntityDescription
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.components.switch import SwitchEntityDescription
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


@dataclass(frozen=True, kw_only=True)
class SDCPDeviceEntityDescription:
    """base SDCP Device Entity Description"""

    available: Callable[..., bool] = lambda _client: _client.is_connected


@dataclass(frozen=True, kw_only=True)
class SDCPDeviceImageEntityDescription(
    SDCPDeviceEntityDescription, ImageEntityDescription
):
    """A class that describes SDCP image entities."""

    image_url: Callable[..., str] = None
    extra_state_attributes: dict[str, Callable] = None


@dataclass(frozen=True, kw_only=True)
class SDCPDeviceSensorEntityDescription(
    SDCPDeviceEntityDescription, SensorEntityDescription
):
    """A class that describes SDCP sensor entities."""

    native_value: Callable = None
    supported_features: int = None
    extra_state_attributes: dict[str, Callable] = None


@dataclass(frozen=True, kw_only=True)
class SDCPDeviceSwitchEntityDescription(
    SDCPDeviceEntityDescription, SwitchEntityDescription
):
    """A class that describes SDCP switch entities."""

    is_on: Callable[..., bool] = None
    turn_on: Callable = None
    turn_off: Callable = None


@dataclass(frozen=True, kw_only=True)
class SDCPDeviceBinarySensorEntityDescription(
    SDCPDeviceEntityDescription, BinarySensorEntityDescription
):
    """A class that describes SDCP button entities."""

    is_on: Callable[..., bool] = None
    extra_state_attributes: dict[str, Callable] = None


@dataclass
class SDCPDeviceData:
    client: SDCPWSClient
    coordinator: SDCPDeviceCoordinator


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Setup the integration from configuration.yaml"""
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
    coordinator = SDCPDeviceCoordinator(hass, entry)
    entry.runtime_data = SDCPDeviceData(client=client, coordinator=coordinator)

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        entry.runtime_data.client.disconnect()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
