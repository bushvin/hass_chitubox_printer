"""Sensor platform for SDCP Printer integration."""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    STATE_OK,
    STATE_PROBLEM,
    STATE_UNKNOWN,
    EntityCategory,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import SDCPDeviceSensorEntityDescription
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
    STATE_OFFLINE,
    SDCPPrinterEntityFeature,
)
from .entity import SDCPDeviceSensor

SENSORS: tuple[SDCPDeviceSensorEntityDescription, ...] = (
    SDCPDeviceSensorEntityDescription(
        key="Printer",
        name="Printer",
        icon="mdi:printer-3d",
        available=lambda _client: True,
        device_class="3d-printer",
        native_value=lambda _client: (
            STATE_OFFLINE
            if _client.status.machine_status is None
            or len(_client.status.machine_status) == 0
            else _client.status.machine_status[0]
        ).capitalize(),
        supported_features=SDCPPrinterEntityFeature(0)
        | (
            SDCPPrinterEntityFeature.PAUSE
            | SDCPPrinterEntityFeature.RESUME
            | SDCPPrinterEntityFeature.STOP
        ),
        extra_state_attributes={
            "action": lambda _client: _client.status.print_status,
            "all_statuses": lambda _client: _client.status.machine_status,
            "previous_state": lambda _client: _client.status.machine_previous_status,
        },
    ),
)
DIAGNOSTIC_SENSORS: tuple[SDCPDeviceSensorEntityDescription, ...] = (
    SDCPDeviceSensorEntityDescription(
        key="Job progress",
        name="Job Progress",
        icon="mdi:file-percent",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_value=lambda _client: (
            0
            if _client.status.print_progress is None
            else round(_client.status.print_progress, 2)
        ),
        native_unit_of_measurement=PERCENTAGE,
        extra_state_attributes={
            "current_layer": lambda _client: _client.status.print_current_layer,
            "current_task_id": lambda _client: _client.status.print_task_id,
            "filename": lambda _client: _client.status.print_filename,
            "time_remaining_ms": lambda _client: _client.status.print_current_layer,
            "timelapse_url": lambda _client: (
                _client.current_task.timelapse_url
                if hasattr(_client.current_task, "timelapse_url")
                else STATE_UNKNOWN
            ),
            "total_layers": lambda _client: _client.status.print_total_layers,
            "total_time_ms": lambda _client: _client.status.print_total_time,
        },
    ),
    SDCPDeviceSensorEntityDescription(
        key="UV LED Temperature",
        name="UV LED Temperature",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_value=lambda _client: (
            None
            if _client.status.uvled_temperature is None
            else round(_client.status.uvled_temperature, 2)
        ),
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        extra_state_attributes={
            "max_temperature": lambda _client: (
                None
                if _client.status.uvled_temperature is None
                else round(_client.status.uvled_temperature, 2)
            )
        },
    ),
    SDCPDeviceSensorEntityDescription(
        key="Enclosure Temperature",
        name="Enclosure Temperature",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_value=lambda _client: (
            None
            if _client.status.enclosure_temperature is None
            else round(_client.status.enclosure_temperature, 2)
        ),
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        extra_state_attributes={
            "target_enclosure_temperature": lambda _client: (
                None
                if _client.status.enclosure_target_temperature is None
                else round(_client.status.enclosure_target_temperature, 2)
            )
        },
    ),
    SDCPDeviceSensorEntityDescription(
        key="Release Film Status",
        name="Release Film Status",
        icon="mdi:filmstrip-box",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_value=lambda _client: (
            STATE_OK.capitalize()
            if _client.attributes.release_film_status == "normal"
            else STATE_PROBLEM.capitalize()
        ),
        extra_state_attributes={
            "release_film_use_count": lambda _client: _client.status.release_film_use_count,
            "release_film_max_uses": lambda _client: _client.attributes.release_film_max_uses,
        },
    ),
    SDCPDeviceSensorEntityDescription(
        key="Print job estimated finish time",
        name="Print job estimated finish time",
        icon="mdi:clock-end",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.TIMESTAMP,
        native_value=lambda _client: _client.status.print_finished_at_datetime,
    ),
    SDCPDeviceSensorEntityDescription(
        key="Print job start time",
        name="Print job start time",
        icon="mdi:clock-start",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.TIMESTAMP,
        native_value=lambda _client: _client.status.print_started_at_datetime,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the available ChituBox sensors."""

    assert entry.unique_id is not None

    for sensor in SENSORS:
        async_add_entities(
            [
                SDCPDeviceSensor(
                    config_entry=entry,
                    entity_description=sensor,
                )
            ],
            update_before_add=True,
        )

    for sensor in DIAGNOSTIC_SENSORS:
        async_add_entities(
            [
                SDCPDeviceSensor(
                    config_entry=entry,
                    entity_description=sensor,
                )
            ],
            update_before_add=True,
        )

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
