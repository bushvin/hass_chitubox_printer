from __future__ import annotations

import datetime
import logging
import time

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
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
    STATE_IDLE,
    STATE_OFF,
    STATE_ON,
    STATE_UNKNOWN,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
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
    STATE_OFFLINE,
    SDCPPrinterEntityFeature,
)
from .coordinator import SDCPDeviceCoordinator

_LOGGER = logging.getLogger(__name__)


class SDCPPrinterEntity(CoordinatorEntity, SensorEntity):
    """Representation of a ChituBox printer sensor."""

    def __init__(self, entry, sdcp_entity_type="sensor"):
        """Initialize the entity."""
        super().__init__(entry.runtime_data)
        _LOGGER.debug("SDCPPrinterEntity::__init__")
        self.entry = entry
        self.sdcp_entity_type = sdcp_entity_type

        self.client = self.coordinator.client
        self._device_id = self.entry.unique_id

        self._attr_state = None
        self._attr_name = f"{self.entry.data[CONF_NAME]} {self.sdcp_entity_type}"
        self._attr_unique_id = f"{self.sdcp_entity_type}-{self._device_id}"
        self._attr_available = True

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

        if len(self.client.callback["on_status_update"]) > 0:
            self.client.add_callback("on_status_update", self.schedule_update_ha_state)

        if len(self.client.callback["on_attributes_update"]) > 0:
            self.client.add_callback(
                "on_attributes_update", self.schedule_update_ha_state
            )

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information about this entity."""
        _LOGGER.debug("SDCPPrinterEntity::device_info")
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
        """Return the state of this entity."""
        _LOGGER.debug("SDCPPrinterEntity::state")

        return self._attr_state


class SDCPPrinterSensorBase(SDCPPrinterEntity):
    """Base sensor entity"""


class SDCPPrinterBinarySensor(SDCPPrinterEntity):
    """Base binary sensor entity"""


class SDCPPrinterDateTime(SDCPPrinterEntity):
    """Base datetime entity"""


class SDCPPrinterSensor(SDCPPrinterSensorBase):
    """ChituBox Printer State"""

    _attr_icon = "mdi:printer-3d"
    _attr_supported_features: SDCPPrinterEntityFeature = SDCPPrinterEntityFeature(0) | (
        SDCPPrinterEntityFeature.PAUSE
        | SDCPPrinterEntityFeature.RESUME
        | SDCPPrinterEntityFeature.STOP
    )
    _attr_device_class = "3d-printer"

    def _client_update_status(self, message):
        """Handle status updates"""
        _LOGGER.debug("SDCPPrinterStateSensor::_client_update_status")

        if len(message.machine_status) > 0:
            self._attr_state = message.machine_status[0]
        else:
            self._attr_state = "idle"

    def __init__(self, entry):
        """Initialize the State entity"""
        super().__init__(entry, "Printer")
        _LOGGER.debug("SDCPPrinterStateSensor::__init__")
        self.client.request_status_update()

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes"""
        _LOGGER.debug("SDCPPrinterStateSensor::extra_state_attributes")
        attributes = {
            "previous_state": STATE_UNKNOWN,
            "action": STATE_IDLE,
            "filename": STATE_UNKNOWN,
        }

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

        if (
            hasattr(self.client.status, "print_filename")
            and self.client.status.print_filename is not None
        ):
            attributes["filename"] = self.client.status.print_filename

        if not self.client.is_available:
            attributes["action"] = STATE_OFFLINE

        return attributes

    @property
    def state(self):
        """Return the state of this entity."""
        _LOGGER.debug("SDCPPrinterStateSensor::state")
        if self.client.is_available:
            return self._attr_state
        else:
            return STATE_OFFLINE

    @property
    def supported_features(self) -> SDCPPrinterEntityFeature:
        """Flag supported features."""
        _LOGGER.debug("SDCPPrinterStateSensor::supported_features")
        return self._attr_supported_features

    def pause_print_job(self):
        """Pause the current print job"""
        _LOGGER.debug("SDCPPrinterStateSensor::pause_print_job")
        self.client.request_job_pause()

    def resume_print_job(self):
        """Resume the current print job"""
        _LOGGER.debug("SDCPPrinterStateSensor::resume_print_job")
        self.client.request_job_resume()

    def stop_print_job(self):
        """Stop the current job"""
        _LOGGER.debug("SDCPPrinterStateSensor::stop_print_job")
        self.client.request_job_stop()


class SDCPPrinterProgressSensor(SDCPPrinterSensorBase):
    """Progress of the print"""

    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:file-percent"

    def _client_update_status(self, message):
        """Handle status updates"""
        _LOGGER.debug("SDCPPrinterProgressSensor::_client_update_status")

        if message.print_progress is None:
            self._attr_state = None
        else:
            self._attr_state = round(message.print_progress, 2)

    def __init__(self, entry):
        """Initialize the Progress entity"""
        super().__init__(entry, "Job Progress")
        _LOGGER.debug("SDCPPrinterProgressSensor::__init__")

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes"""
        _LOGGER.debug("SDCPPrinterProgressSensor::extra_state_attributes")
        attributes = {
            "total_time_ms": STATE_UNKNOWN,
            "time_remaining_ms": STATE_UNKNOWN,
            "current_layer": STATE_UNKNOWN,
            "total_layers": STATE_UNKNOWN,
        }

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


class SDCPPrinterFinishTimeSensor(SDCPPrinterSensorBase):
    """Finish Time of the print"""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:clock-end"

    def _client_update_status(self, message):
        """Handle status updates"""
        _LOGGER.debug(
            "SDCPPrinterFinishTimeSensor::_client_update_status - Received Status Update"
        )

        self._attr_state = message.print_finished_at_datetime

    def __init__(self, entry):
        """Initialize the Finish Time entity"""
        super().__init__(entry, "Print job estimated finish time")
        _LOGGER.debug("SDCPPrinterFinishTimeSensor::__init__")


class SDCPPrinterStartTimeSensor(SDCPPrinterSensorBase):
    """Start Time of the print"""

    _attr_icon = "mdi:clock-start"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def _client_update_status(self, message):
        """Handle status updates"""
        _LOGGER.debug("SDCPPrinterStartTimeSensor::_client_update_status")

        self._attr_state = message.print_started_at_datetime

    def __init__(self, entry):
        """Initialize the Start Time entity"""
        super().__init__(entry, "Print job start time")
        _LOGGER.debug("SDCPPrinterStartTimeSensor::__init__")


class SDCPPrinterTemperatureSensor(SDCPPrinterSensorBase):
    """Temperature of the printer enclosure"""

    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def _client_update_status(self, message):
        """Handle status updates"""
        _LOGGER.debug("SDCPPrinterTemperatureSensor::_client_update_statuse")

        if message.enclosure_temperature is None:
            return None
        self._attr_state = round(message.enclosure_temperature, 2)

    def __init__(self, entry):
        """Initialize the Enclosure Temperature entity"""
        super().__init__(entry, "Enclosure Temperature")
        _LOGGER.debug("SDCPPrinterTemperatureSensor::__init__")

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes"""
        _LOGGER.debug("SDCPPrinterTemperatureSensor::extra_state_attributes")
        attributes = {
            "target_enclosure_temperature": STATE_UNKNOWN,
        }

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
        """Handle status updates"""
        _LOGGER.debug("SDCPPrinterUVLEDTemperatureSensor::_client_update_status")

        if message.uvled_temperature is None:
            return None
        self._attr_state = round(message.uvled_temperature, 2)

    def __init__(self, entry):
        """Initialize the UV LED Temperature entity"""
        super().__init__(entry, "UV LED Temperature")
        _LOGGER.debug("SDCPPrinterUVLEDTemperatureSensor::__init__")

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes"""
        _LOGGER.debug("SDCPPrinterUVLEDConnectedBinarySensor::extra_state_attributes")
        attributes = {
            "max_temperature": STATE_UNKNOWN,
        }

        if (
            hasattr(self.client.attributes, "uvled_max_temp")
            and self.client.attributes.uvled_max_temp is not None
        ):
            attributes["max_temperature"] = self.client.attributes.uvled_max_temp

        return attributes


class SDCPPrinterUSBDiskConnectedBinarySensor(SDCPPrinterBinarySensor):
    """USB Disk Connected"""

    _attr_icon = "mdi:usb-flash-drive"

    def _client_update_attributes(self, message):
        """Handle status updates"""
        _LOGGER.debug(
            "SDCPPrinterUSBDiskConnectedBinarySensor::_client_update_attributes"
        )

        if message.usbdisk_connected is None:
            return STATE_UNKNOWN

        self._attr_state = STATE_ON if bool(message.usbdisk_connected) else STATE_OFF

    def __init__(self, entry):
        """Initialize the USB Disk entity"""
        super().__init__(entry, "USB Disk Connected")
        _LOGGER.debug("SDCPPrinterUSBDiskConnectedBinarySensor::__init__")


class SDCPPrinterUVLEDConnectedBinarySensor(SDCPPrinterBinarySensor):
    """UV LED Connected"""

    _attr_icon = "mdi:led-on"

    def _client_update_attributes(self, message):
        """Handle status updates"""
        _LOGGER.debug(
            "SDCPPrinterUVLEDConnectedBinarySensor::_client_update_attributes"
        )

        if message.uvled_temp_sensor_connected is None:
            return STATE_UNKNOWN

        self._attr_state = (
            STATE_ON if bool(message.uvled_temp_sensor_connected) else STATE_OFF
        )

    def __init__(self, entry):
        """Initialize the UV LED entity"""
        super().__init__(entry, "UV LED Connected")
        _LOGGER.debug("SDCPPrinterUVLEDConnectedBinarySensor::__init__")

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes"""
        _LOGGER.debug("SDCPPrinterUVLEDConnectedBinarySensor::extra_state_attributes")
        attributes = {"status": STATE_UNKNOWN}

        if (
            hasattr(self.client.attributes, "uvled_temp_sensor_status")
            and self.client.attributes.uvled_temp_sensor_status is not None
        ):
            attributes["status"] = self.client.attributes.uvled_temp_sensor_status

        return attributes


class SDCPPrinterLCDConnectedBinarySensor(SDCPPrinterBinarySensor):
    """Exposure Screen Connected"""

    _attr_icon = "mdi:fit-to-screen"

    def _client_update_attributes(self, message):
        """Handle status updates"""
        _LOGGER.debug("SDCPPrinterLCDConnectedBinarySensor::_client_update_attributes")

        if message.lcd_connected is None:
            return STATE_UNKNOWN

        self._attr_state = STATE_ON if bool(message.lcd_connected) else STATE_OFF

    def __init__(self, entry):
        """Initialize the Exposure Screen entity"""
        super().__init__(entry, "Exposure Screen Connected")
        _LOGGER.debug("SDCPPrinterLCDConnectedBinarySensor::__init__")


class SDCPPrinterStrainGaugeConnectedBinarySensor(SDCPPrinterBinarySensor):
    """UV LED COnnected"""

    _attr_icon = "mdi:led-on"

    def _client_update_attributes(self, message):
        """Handle status updates"""
        _LOGGER.debug(
            "SDCPPrinterStrainGaugeConnectedBinarySensor::_client_update_attributes"
        )

        if message.strain_gauge_connected is None:
            return STATE_UNKNOWN

        self._attr_state = (
            STATE_ON if bool(message.strain_gauge_connected) else STATE_OFF
        )

    def __init__(self, entry):
        """Initialize the Strain Gauge entity"""
        super().__init__(entry, "Strain Gauge Connected")
        _LOGGER.debug("SDCPPrinterStrainGaugeConnectedBinarySensor::__init__")

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes"""
        _LOGGER.debug(
            "SDCPPrinterStrainGaugeConnectedBinarySensor::extra_state_attributes"
        )
        attributes = {"status": STATE_UNKNOWN}

        if (
            hasattr(self.client.attributes, "strain_gauge_status")
            and self.client.attributes.strain_gauge_status is not None
        ):
            attributes["status"] = self.client.attributes.strain_gauge_status

        return attributes


class SDCPPrinterZmotorConnectedBinarySensor(SDCPPrinterBinarySensor):
    """Z-Motor Connected"""

    _attr_icon = "mdi:axis-z-arrow"

    def _client_update_attributes(self, message):
        """Handle status updates"""
        _LOGGER.debug(
            "SDCPPrinterZmotorConnectedBinarySensor::_client_update_attributes"
        )

        if message.z_motor_connected is None:
            return STATE_UNKNOWN

        self._attr_state = STATE_ON if bool(message.z_motor_connected) else STATE_OFF

    def __init__(self, entry):
        """Initialize the USB Disk entity"""
        super().__init__(entry, "Z-Motor Connected")
        _LOGGER.debug("SDCPPrinterZmotorConnectedBinarySensor::__init__")


class SDCPPrinterRotaryMotorConnectedBinarySensor(SDCPPrinterBinarySensor):
    """Z-Motor Connected"""

    _attr_icon = "mdi:rotate-360"

    def _client_update_attributes(self, message):
        """Handle status updates"""
        _LOGGER.debug(
            "SDCPPrinterRotaryMotorConnectedBinarySensor::_client_update_attributes"
        )

        if message.rotary_motor_connected is None:
            return STATE_UNKNOWN

        self._attr_state = (
            STATE_ON if bool(message.rotary_motor_connected) else STATE_OFF
        )

    def __init__(self, entry):
        """Initialize the USB Disk entity"""
        super().__init__(entry, "Rotary Motor Connected")
        _LOGGER.debug("SDCPPrinterRotaryMotorConnectedBinarySensor::__init__")


class SDCPPrinterCameraConnectedConnectedBinarySensor(SDCPPrinterBinarySensor):
    """Camera Connected"""

    _attr_icon = "mdi:camera"

    def _client_update_attributes(self, message):
        """Handle status updates"""
        _LOGGER.debug(
            "SDCPPrinterCameraConnectedConnectedBinarySensor::_client_update_attributes"
        )

        if message.camera_connected is None:
            return STATE_UNKNOWN

        self._attr_state = STATE_ON if bool(message.camera_connected) else STATE_OFF

    def __init__(self, entry):
        """Initialize the USB Disk entity"""
        super().__init__(entry, "Camera Connected")
        _LOGGER.debug("SDCPPrinterCameraConnectedConnectedBinarySensor::__init__")
