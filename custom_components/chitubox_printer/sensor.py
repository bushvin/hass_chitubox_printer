"""Sensor platform for SDCP Printer integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    METHOD_PAUSE_PRINT_JOB,
    METHOD_RESUME_PRINT_JOB,
    METHOD_START_PRINT_JOB,
    METHOD_STOP_PRINT_JOB,
    METHOD_TURN_CAMERA_OFF,
    METHOD_TURN_CAMERA_ON,
    METHOD_TURN_TIMELAPSE_OFF,
    METHOD_TURN_TIMELAPSE_ON,
    SCHEMA_PAUSE_PRINT_JOB,
    SCHEMA_RESUME_PRINT_JOB,
    SCHEMA_START_PRINT_JOB,
    SCHEMA_STOP_PRINT_JOB,
    SCHEMA_TURN_CAMERA_OFF,
    SCHEMA_TURN_CAMERA_ON,
    SCHEMA_TURN_TIMELAPSE_OFF,
    SCHEMA_TURN_TIMELAPSE_ON,
    SERVICE_PAUSE_PRINT_JOB,
    SERVICE_RESUME_PRINT_JOB,
    SERVICE_START_PRINT_JOB,
    SERVICE_STOP_PRINT_JOB,
    SERVICE_TURN_CAMERA_OFF,
    SERVICE_TURN_CAMERA_ON,
    SERVICE_TURN_TIMELAPSE_OFF,
    SERVICE_TURN_TIMELAPSE_ON,
    SDCPPrinterEntityFeature,
)
from .entity import (
    SDCPPrinterFinishTimeSensor,
    SDCPPrinterProgressSensor,
    SDCPPrinterReleaseFilmSensor,
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
        SDCPPrinterReleaseFilmSensor(entry),
    ]

    async_add_entities(entities)

    """Set up Chitubox services"""
    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        SERVICE_PAUSE_PRINT_JOB,
        SCHEMA_PAUSE_PRINT_JOB,
        METHOD_PAUSE_PRINT_JOB,
        [SDCPPrinterEntityFeature.PAUSE],
    )

    platform.async_register_entity_service(
        SERVICE_RESUME_PRINT_JOB,
        SCHEMA_RESUME_PRINT_JOB,
        METHOD_RESUME_PRINT_JOB,
        [SDCPPrinterEntityFeature.RESUME],
    )

    platform.async_register_entity_service(
        SERVICE_START_PRINT_JOB,
        SCHEMA_START_PRINT_JOB,
        METHOD_START_PRINT_JOB,
        [SDCPPrinterEntityFeature.START],
    )

    platform.async_register_entity_service(
        SERVICE_STOP_PRINT_JOB,
        SCHEMA_STOP_PRINT_JOB,
        METHOD_STOP_PRINT_JOB,
        [SDCPPrinterEntityFeature.STOP],
    )

    platform.async_register_entity_service(
        SERVICE_TURN_TIMELAPSE_OFF,
        SCHEMA_TURN_TIMELAPSE_OFF,
        METHOD_TURN_TIMELAPSE_OFF,
        [SDCPPrinterEntityFeature.TIMELAPSE_OFF],
    )

    platform.async_register_entity_service(
        SERVICE_TURN_TIMELAPSE_ON,
        SCHEMA_TURN_TIMELAPSE_ON,
        METHOD_TURN_TIMELAPSE_ON,
        [SDCPPrinterEntityFeature.TIMELAPSE_ON],
    )

    platform.async_register_entity_service(
        SERVICE_TURN_CAMERA_OFF,
        SCHEMA_TURN_CAMERA_OFF,
        METHOD_TURN_CAMERA_OFF,
        [SDCPPrinterEntityFeature.CAMERA_OFF],
    )

    platform.async_register_entity_service(
        SERVICE_TURN_CAMERA_ON,
        SCHEMA_TURN_CAMERA_ON,
        METHOD_TURN_CAMERA_ON,
        [SDCPPrinterEntityFeature.CAMERA_ON],
    )
