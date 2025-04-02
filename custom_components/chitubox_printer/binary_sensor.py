"""Sensor platform for SDCP Printer integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import (
    SDCPPrinterCameraConnectedBinarySensor,
    SDCPPrinterLCDConnectedBinarySensor,
    SDCPPrinterRotaryMotorConnectedBinarySensor,
    SDCPPrinterStrainGaugeConnectedBinarySensor,
    SDCPPrinterUSBDiskConnectedBinarySensor,
    SDCPPrinterUVLEDConnectedBinarySensor,
    SDCPPrinterZmotorConnectedBinarySensor,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the available ChituBox sensors."""

    assert entry.unique_id is not None

    entities = [
        SDCPPrinterUSBDiskConnectedBinarySensor(entry),
        SDCPPrinterUVLEDConnectedBinarySensor(entry),
        SDCPPrinterLCDConnectedBinarySensor(entry),
        SDCPPrinterStrainGaugeConnectedBinarySensor(entry),
        SDCPPrinterZmotorConnectedBinarySensor(entry),
        SDCPPrinterRotaryMotorConnectedBinarySensor(entry),
        SDCPPrinterCameraConnectedBinarySensor(entry),
    ]

    async_add_entities(entities)
