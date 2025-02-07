"""Sensor platform for SDCP Printer integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    PAUSE_PRINT_JOB_SCHEMA,
    RESUME_PRINT_JOB_SCHEMA,
    SERVICE_PAUSE_PRINT_JOB,
    SERVICE_RESUME_PRINT_JOB,
    SERVICE_STOP_PRINT_JOB,
    STOP_PRINT_JOB_SCHEMA,
    SDCPPrinterEntityFeature,
)
from .entity import (
    SDCPPrinterFinishTimeSensor,
    SDCPPrinterProgressSensor,
    SDCPPrinterSensor,
    SDCPPrinterStartTimeSensor,
    SDCPPrinterTemperatureSensor,
    SDCPPrinterUVLEDTemperatureSensor,
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
        SDCPPrinterSensor(entry),
        SDCPPrinterProgressSensor(entry),
        SDCPPrinterFinishTimeSensor(entry),
        SDCPPrinterStartTimeSensor(entry),
        SDCPPrinterTemperatureSensor(entry),
        SDCPPrinterUVLEDTemperatureSensor(entry),
    ]

    async_add_entities(entities)

    """Set up Chitubox services"""
    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        SERVICE_PAUSE_PRINT_JOB,
        PAUSE_PRINT_JOB_SCHEMA,
        "pause_print_job",
        [SDCPPrinterEntityFeature.PAUSE],
    )

    platform.async_register_entity_service(
        SERVICE_RESUME_PRINT_JOB,
        RESUME_PRINT_JOB_SCHEMA,
        "resume_print_job",
        [SDCPPrinterEntityFeature.RESUME],
    )

    platform.async_register_entity_service(
        SERVICE_STOP_PRINT_JOB,
        STOP_PRINT_JOB_SCHEMA,
        "stop_print_job",
        [SDCPPrinterEntityFeature.STOP],
    )
