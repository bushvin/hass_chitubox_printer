"""Sensor platform for SDCP Printer integration."""

from __future__ import annotations

import datetime
import logging
import time

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_ID,
    CONF_NAME,
    PERCENTAGE,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    CONF_BRAND,
    CONF_MACHINE_BRAND_ID,
    CONF_MAINBOARD_ID,
    CONF_MODEL,
    DEFAULT_NAME,
    DOMAIN,
)
from .coordinator import SDCPDeviceCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the available ChituBox sensors."""

    assert entry.unique_id is not None

    entities = [
        SDCPPrinterStateSensor(entry),
        SDCPPrinterProgressSensor(entry),
        SDCPPrinterFinishTimeSensor(entry),
        SDCPPrinterStartTimeSensor(entry),
        SDCPPrinterTemperatureSensor(entry),
        SDCPPrinterUVLEDTemperatureSensor(entry),
    ]

    async_add_entities(entities)


class SDCPPrinterSensorBase(CoordinatorEntity, SensorEntity):
    """Representation of a ChituBox printer sensor."""

    def __init__(self, entry, sensor_type="sensor"):
        """Initialize the sensor."""
        super().__init__(entry.runtime_data)
        self.entry = entry
        self.sensor_type = sensor_type

        self.client = self.coordinator.client
        self._device_id = self.entry.unique_id

        self._attr_state = None
        self._attr_name = f"{self.entry.data[CONF_NAME]} {self.sensor_type}"
        self._attr_unique_id = f"{self.sensor_type}-{self._device_id}"

        if hasattr(self, "_client_update_status") and callable(
            self._client_update_status
        ):
            self.client.add_callback("on_status_update", self._client_update_status)

        if hasattr(self, "_client_update_attributes") and callable(
            self._client_update_attributes
        ):
            self.client.add_callback(
                "on_attributes_update", self._client_update_attributes
            )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.client.is_available

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information about this entity."""
        device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self.entry.data[CONF_NAME],
            manufacturer=self.entry.data[CONF_BRAND],
            model=self.entry.data[CONF_MODEL],
        )

        if hasattr(self.client.attributes, "firmware_version"):
            device_info["hw_version"] = self.client.attributes.firmware_version

        return device_info

    @property
    def state(self):
        return self._attr_state


class SDCPPrinterStateSensor(SDCPPrinterSensorBase):
    """ChituBox Printer State"""

    _attr_icon = "mdi:printer-3d"

    def _client_update_status(self, message):
        _LOGGER.debug("Received Status Update")

        if len(message.machine_status) > 0:
            self._attr_state = message.machine_status[0]
        else:
            self._attr_state = None

        self.schedule_update_ha_state(force_refresh=True)

    def __init__(self, entry):
        super().__init__(entry, "Current State")

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes"""
        attributes = {}

        if (
            hasattr(self.client.status, "machine_previous_status")
            and self.client.status.machine_previous_status is not None
        ):
            attributes["previous_state"] = self.client.status.machine_previous_status

        if (
            hasattr(self.client.status, "print_status")
            and self.client.status.print_status is not None
        ):
            attributes["action"] = self.client.status.print_status

        return attributes


class SDCPPrinterProgressSensor(SDCPPrinterSensorBase):
    """Progress of the print"""

    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:file-percent"

    def _client_update_status(self, message):
        _LOGGER.debug("Received Status Update")

        if message.print_progress is None:
            self._attr_state = None
        else:
            self._attr_state = round(message.print_progress, 2)

        self.schedule_update_ha_state(force_refresh=True)

    def __init__(self, entry):
        super().__init__(entry, "Job Progress")

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes"""
        attributes = {}

        if (
            hasattr(self.client.status, "print_total_time")
            and self.client.status.print_total_time is not None
        ):
            attributes["total_time_ms"] = self.client.status.print_total_time

        if (
            hasattr(self.client.status, "print_remaining_time")
            and self.client.status.print_remaining_time is not None
        ):
            attributes["time_remaining_ms"] = self.client.status.print_remaining_time

        if (
            hasattr(self.client.status, "print_started_at")
            and self.client.status.print_started_at is not None
        ):
            attributes["started_at"] = self.client.status.print_started_at

        if (
            hasattr(self.client.status, "print_finished_at")
            and self.client.status.print_finished_at is not None
        ):
            attributes["finished_at"] = self.client.status.print_finished_at

        if (
            hasattr(self.client.status, "print_current_layer")
            and self.client.status.print_current_layer is not None
        ):
            attributes["current_layer"] = self.client.status.print_current_layer

        if (
            hasattr(self.client.status, "print_total_layers")
            and self.client.status.print_total_layers is not None
        ):
            attributes["total_layers"] = self.client.status.print_total_layers

        return attributes

    @property
    def state(self):
        return self._attr_state


class SDCPPrinterFinishTimeSensor(SDCPPrinterSensorBase):
    """Finish Time of the print"""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:clock-end"

    def _client_update_status(self, message):
        _LOGGER.debug("Received Status Update")

        self._attr_state = message.print_finished_at_datetime

        self.schedule_update_ha_state(force_refresh=True)

    def __init__(self, entry):
        super().__init__(entry, "Print job estimated finish time")


class SDCPPrinterStartTimeSensor(SDCPPrinterSensorBase):
    """Start Time of the print"""

    _attr_icon = "mdi:clock-start"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def _client_update_status(self, message):
        _LOGGER.debug("Received Status Update")

        self._attr_state = message.print_started_at_datetime

        self.schedule_update_ha_state(force_refresh=True)

    def __init__(self, entry):
        super().__init__(entry, "Print job start time")


class SDCPPrinterTemperatureSensor(SDCPPrinterSensorBase):
    """Temperature of the printer enclosure"""

    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def _client_update_status(self, message):
        _LOGGER.debug("Received Status Update")

        if message.enclosure_temperature is None:
            return None
        self._attr_state = round(message.enclosure_temperature, 2)

        self.schedule_update_ha_state(force_refresh=True)

    def __init__(self, entry):
        super().__init__(entry, "Enclosure Temperature")

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes"""
        attributes = {}

        if (
            hasattr(self.client.status, "enclosure_target_temperature")
            and self.client.status.enclosure_target_temperature is not None
        ):
            attributes["target_enclosure_temperature"] = (
                self.client.status.enclosure_target_temperature
            )

        return attributes


class SDCPPrinterUVLEDTemperatureSensor(SDCPPrinterSensorBase):
    """Temperature of the printer enclosure"""

    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def _client_update_status(self, message):
        _LOGGER.debug("Received Status Update")

        if message.uvled_temperature is None:
            return None
        self._attr_state = round(message.uvled_temperature, 2)

        self.schedule_update_ha_state(force_refresh=True)

    def __init__(self, entry):
        super().__init__(entry, "UV LED Temperature")

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes"""
        attributes = {}

        if (
            hasattr(self.client.status, "enclosure_target_temperature")
            and self.client.status.enclosure_target_temperature is not None
        ):
            attributes["target_enclosure_temperature"] = (
                self.client.status.enclosure_target_temperature
            )

        return attributes
