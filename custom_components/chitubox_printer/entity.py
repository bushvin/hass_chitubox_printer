from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    CONF_FILENAME,
    CONF_NAME,
    PERCENTAGE,
    STATE_IDLE,
    STATE_OFF,
    STATE_ON,
    STATE_UNKNOWN,
    UnitOfTemperature,
)
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_BRAND,
    CONF_MODEL,
    CONF_START_LAYER,
    DOMAIN,
    STATE_OFFLINE,
    SDCPPrinterEntityFeature,
)

_LOGGER = logging.getLogger(__name__)


class SDCPPrinterEntity(CoordinatorEntity):
    """Representation of a ChituBox printer sensor."""

    sdcp_entity_type: str = "sensor"

    def __init__(self, entry):
        """Initialize the entity."""
        super().__init__(entry.runtime_data)

        self.entry = entry

        self.client = self.coordinator.client
        self._device_id = self.entry.unique_id

        self._attr_state = None
        self._attr_name = f"{self.entry.data[CONF_NAME]} {self.sdcp_entity_type}"
        self._attr_unique_id = f"{self.sdcp_entity_type}-{self._device_id}"

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
    def device_info(self) -> dict[str, Any]:
        """Return device information about this entity."""
        device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self.entry.data[CONF_NAME],
            manufacturer=self.entry.data[CONF_BRAND],
            model=self.entry.data[CONF_MODEL],
        )

        if self.client.attributes.firmware_version is not None:
            device_info["hw_version"] = self.client.attributes.firmware_version

        return device_info

    @property
    def state(self):
        """Return the state of this entity."""
        if self.client.is_connected:
            return self._attr_state
        else:
            return STATE_UNKNOWN

    @property
    def available(self):
        """Return True if entity is available."""
        return self.client.is_connected


class SDCPPrinterSensorBase(SDCPPrinterEntity, SensorEntity):
    """Base sensor entity"""

    def __init__(self, entry):
        super().__init__(entry)
        SensorEntity.__init__(self)


class SDCPPrinterBinarySensor(SDCPPrinterEntity, BinarySensorEntity):
    """Base binary sensor entity"""

    def __init__(self, entry):
        super().__init__(entry)
        BinarySensorEntity.__init__(self)


class SDCPPrinterSensor(SDCPPrinterSensorBase):
    """ChituBox Printer State"""

    _attr_icon = "mdi:printer-3d"
    _attr_supported_features: SDCPPrinterEntityFeature = SDCPPrinterEntityFeature(0) | (
        SDCPPrinterEntityFeature.PAUSE
        | SDCPPrinterEntityFeature.RESUME
        | SDCPPrinterEntityFeature.STOP
    )
    _attr_device_class = "3d-printer"
    sdcp_entity_type = "Printer"

    def _client_update_status(self, message):
        """Handle status updates"""

        if len(self.client.status.machine_status) > 0:
            new_state = self.client.status.machine_status[0]
        else:
            new_state = STATE_IDLE

        if self._attr_state != new_state:
            self._attr_state = new_state
            self.schedule_update_ha_state()

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes"""
        attributes = {
            "previous_state": STATE_UNKNOWN,
            "action": STATE_IDLE,
            "filename": STATE_UNKNOWN,
        }

        if self.client.status.machine_previous_status is not None:
            attributes["previous_state"] = self.client.status.machine_previous_status

        if self.client.status.print_status is not None:
            attributes["action"] = self.client.status.print_status

        if self.client.status.print_filename is not None:
            attributes["filename"] = self.client.status.print_filename

        if not self.client.is_connected:
            attributes["action"] = STATE_OFFLINE

        return attributes

    @property
    def state(self):
        """Return the state of this entity."""
        if self.client.is_connected:
            return self._attr_state
        else:
            return STATE_OFFLINE

    @property
    def available(self):
        """Return True if entity is available."""
        return True

    @property
    def supported_features(self) -> SDCPPrinterEntityFeature:
        """Flag supported features."""
        return self._attr_supported_features

    def svc_pause_print_job(self):
        """Pause the current print job"""
        self.client.pause_print()

    def svc_resume_print_job(self):
        """Resume the current print job"""
        self.client.resume_print()

    def svc_stop_print_job(self):
        """Stop the current job"""
        self.client.stop_print()

    def svc_start_print_job(self, printer, service_call):
        """Start a print job"""

        filename = service_call.data[CONF_FILENAME]
        start_layer = service_call.data[CONF_START_LAYER]

        self.client.start_print(filename, start_layer)

    def svc_turn_timelapse_off(self):
        """Turn timelapse off"""
        self.client.turn_timelapse_off()

    def svc_turn_timelapse_on(self):
        """Turn timelapse on"""
        self.client.turn_timelapse_on()

    def turn_camera_off(self):
        """Turn camera off"""
        self.client.turn_camera_off()

    def turn_camera_on(self):
        """Turn camera on"""
        self.client.turn_camera_on()


class SDCPPrinterProgressSensor(SDCPPrinterSensorBase):
    """Progress of the print"""

    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:file-percent"
    _extra_attr_total_time_ms = STATE_UNKNOWN
    _extra_attr_time_remaining_ms = STATE_UNKNOWN
    _extra_attr_current_layer = STATE_UNKNOWN
    _extra_attr_total_layers = STATE_UNKNOWN
    sdcp_entity_type = "Job Progress"

    def _client_update_status(self, message):
        """Handle status updates"""
        write_state = False
        if self.client.status.print_progress is None:
            new_state = None
        else:
            new_state = round(self.client.status.print_progress, 2)

        if self._attr_state != new_state:
            self._attr_state = new_state
            write_state = True

        if self._extra_attr_total_time_ms != self.client.status.print_total_time:
            self._extra_attr_total_time_ms = self.client.status.print_total_time
            write_state = True

        if (
            self._extra_attr_time_remaining_ms
            != self.client.status.print_remaining_time
        ):
            self._extra_attr_time_remaining_ms = self.client.status.print_remaining_time
            write_state = True

        if self._extra_attr_current_layer != self.client.status.print_current_layer:
            self._extra_attr_current_layer = self.client.status.print_current_layer
            write_state = True

        if self._extra_attr_total_layers != self.client.status.print_total_layers:
            self._extra_attr_total_layers = self.client.status.print_total_layers
            write_state = True

        if write_state:
            self.schedule_update_ha_state()

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes"""
        return {
            attr: value
            for attr, value in (
                ("total_time_ms", self._extra_attr_total_time_ms),
                ("time_remaining_ms", self._extra_attr_time_remaining_ms),
                ("current_layer", self._extra_attr_current_layer),
                ("total_layers", self._extra_attr_total_layers),
            )
            if value is not None
        }


class SDCPPrinterFinishTimeSensor(SDCPPrinterSensorBase):
    """Finish Time of the print"""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:clock-end"
    sdcp_entity_type = "Print job estimated finish time"

    def _client_update_status(self, message):
        """Handle status updates"""

        if self._attr_state != self.client.status.print_finished_at:
            self._attr_state = self.client.status.print_finished_at
            self.schedule_update_ha_state()


class SDCPPrinterStartTimeSensor(SDCPPrinterSensorBase):
    """Start Time of the print"""

    _attr_icon = "mdi:clock-start"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    sdcp_entity_type = "Print job start time"

    def _client_update_status(self, message):
        """Handle status updates"""

        if self._attr_state != self.client.status.print_started_at:
            self._attr_state = self.client.status.print_started_at
            self.schedule_update_ha_state()


class SDCPPrinterTemperatureSensor(SDCPPrinterSensorBase):
    """Temperature of the printer enclosure"""

    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _extra_attr_target_enclosure_temperature = STATE_UNKNOWN
    sdcp_entity_type = "Enclosure Temperature"

    def _client_update_status(self, message):
        """Handle status updates"""
        write_state = False

        if (
            self.client.status.enclosure_temperature is None
            and self._attr_state is not None
        ):
            self._attr_state = None
            write_state = True

        elif (
            self.client.status.enclosure_temperature is not None
            and self._attr_state != round(self.client.status.enclosure_temperature, 2)
        ):
            self._attr_state = round(self.client.status.enclosure_temperature, 2)
            write_state = True

        if self._extra_attr_target_enclosure_temperature != (
            self.client.status.enclosure_target_temperature
        ):
            self._extra_attr_target_enclosure_temperature = (
                self.client.status.enclosure_target_temperature
            )
            write_state = True

        if write_state:
            self.schedule_update_ha_state()

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes"""
        return {
            attr: value
            for attr, value in (
                (
                    "target_enclosure_temperature",
                    self._extra_attr_target_enclosure_temperature,
                ),
            )
            if value is not None
        }


class SDCPPrinterUVLEDTemperatureSensor(SDCPPrinterSensorBase):
    """Temperature of the printer enclosure"""

    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _extra_attr_max_temperature = STATE_UNKNOWN
    sdcp_entity_type = "UV LED Temperature"

    def _client_update_status(self, message):
        """Handle status updates"""
        write_state = False

        if (
            self.client.status.uvled_temperature is None
            and self._attr_state is not None
        ):
            self._attr_state = None
            write_state = True

        elif (
            self.client.status.uvled_temperature is not None
            and self._attr_state != round(self.client.status.uvled_temperature, 2)
        ):
            self._attr_state = round(self.client.status.uvled_temperature, 2)
            write_state = True

        if self._extra_attr_max_temperature != self.client.attributes.uvled_max_temp:
            self._extra_attr_max_temperature = self.client.attributes.uvled_max_temp
            write_state = True

        if write_state:
            self.schedule_update_ha_state()

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes"""
        return {
            attr: value
            for attr, value in (("max_temperature", self._extra_attr_max_temperature),)
            if value is not None
        }


class SDCPPrinterUSBDiskConnectedBinarySensor(SDCPPrinterBinarySensor):
    """USB Disk Connected"""

    _attr_icon = "mdi:usb-flash-drive"
    sdcp_entity_type = "USB Disk Connected"

    def _client_update_attributes(self, message):
        """Handle status updates"""

        if self.client.attributes.usbdisk_connected is None:
            new_state = STATE_UNKNOWN
        else:
            new_state = (
                STATE_ON
                if bool(self.client.attributes.usbdisk_connected)
                else STATE_OFF
            )

        if self._attr_state != new_state:
            self._attr_state = new_state
            self.schedule_update_ha_state()


class SDCPPrinterUVLEDConnectedBinarySensor(SDCPPrinterBinarySensor):
    """UV LED Connected"""

    _attr_icon = "mdi:led-on"
    _extra_attr_status = STATE_UNKNOWN
    sdcp_entity_type = "UV LED Connected"

    def _client_update_attributes(self, message):
        """Handle status updates"""

        write_state = False

        if self.client.attributes.uvled_temp_sensor_connected is None:
            new_state = STATE_UNKNOWN
        else:
            new_state = (
                STATE_ON
                if bool(self.client.attributes.uvled_temp_sensor_connected)
                else STATE_OFF
            )

        if self._attr_state != new_state:
            self._attr_state = new_state
            write_state = True

        if self._extra_attr_status != self.client.attributes.uvled_temp_sensor_status:
            self._extra_attr_status = self.client.attributes.uvled_temp_sensor_status
            write_state = True

        if write_state:
            self.schedule_update_ha_state()

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes"""
        return {
            attr: value
            for attr, value in (("status", self._extra_attr_status),)
            if value is not None
        }


class SDCPPrinterLCDConnectedBinarySensor(SDCPPrinterBinarySensor):
    """Exposure Screen Connected"""

    _attr_icon = "mdi:fit-to-screen"
    sdcp_entity_type = "Exposure Screen Connected"

    def _client_update_attributes(self, message):
        """Handle status updates"""

        if self.client.attributes.lcd_connected is None:
            new_state = STATE_UNKNOWN
        else:
            new_state = (
                STATE_ON if bool(self.client.attributes.lcd_connected) else STATE_OFF
            )

        if self._attr_state != new_state:
            self._attr_state = new_state
            self.schedule_update_ha_state()


class SDCPPrinterStrainGaugeConnectedBinarySensor(SDCPPrinterBinarySensor):
    """UV LED COnnected"""

    _attr_icon = "mdi:led-on"
    _extra_attr_status = STATE_UNKNOWN
    sdcp_entity_type = "Strain Gauge Connected"

    def _client_update_attributes(self, message):
        """Handle status updates"""

        write_state = False

        if self.client.attributes.strain_gauge_connected is None:
            new_state = STATE_UNKNOWN
        else:
            new_state = (
                STATE_ON
                if bool(self.client.attributes.strain_gauge_connected)
                else STATE_OFF
            )

        if self._attr_state != new_state:
            self._attr_state = new_state
            write_state = True

        if self._extra_attr_status != self.client.attributes.strain_gauge_status:
            self._extra_attr_status = self.client.attributes.strain_gauge_status
            write_state = True

        if write_state:
            self.schedule_update_ha_state()

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes"""
        return {
            attr: value
            for attr, value in (("status", self._extra_attr_status),)
            if value is not None
        }


class SDCPPrinterZmotorConnectedBinarySensor(SDCPPrinterBinarySensor):
    """Z-Motor Connected"""

    _attr_icon = "mdi:axis-z-arrow"
    sdcp_entity_type = "Z-Motor Connected"

    def _client_update_attributes(self, message):
        """Handle status updates"""

        if self.client.attributes.z_motor_connected is None:
            new_state = STATE_UNKNOWN
        else:
            new_state = (
                STATE_ON
                if bool(self.client.attributes.z_motor_connected)
                else STATE_OFF
            )

        if self._attr_state != new_state:
            self._attr_state = new_state
            self.schedule_update_ha_state()


class SDCPPrinterRotaryMotorConnectedBinarySensor(SDCPPrinterBinarySensor):
    """Z-Motor Connected"""

    _attr_icon = "mdi:rotate-360"
    sdcp_entity_type = "Rotary Motor Connected"

    def _client_update_attributes(self, message):
        """Handle status updates"""

        if self.client.attributes.rotary_motor_connected is None:
            new_state = STATE_UNKNOWN
        else:
            new_state = (
                STATE_ON
                if bool(self.client.attributes.rotary_motor_connected)
                else STATE_OFF
            )

        if self._attr_state != new_state:
            self._attr_state = new_state
            self.schedule_update_ha_state()


class SDCPPrinterCameraConnectedBinarySensor(SDCPPrinterBinarySensor):
    """Camera Connected"""

    _attr_icon = "mdi:camera"
    _extra_attr_video_streams_allowed = STATE_UNKNOWN
    _extra_attr_video_stream_connections = STATE_UNKNOWN
    sdcp_entity_type = "Camera Connected"

    def _client_update_attributes(self, message):
        """Handle status updates"""

        write_state = False

        if self.client.attributes.camera_connected is None:
            new_state = STATE_UNKNOWN
        else:
            new_state = (
                STATE_ON if bool(self.client.attributes.camera_connected) else STATE_OFF
            )

        if self._attr_state != new_state:
            self._attr_state = new_state
            write_state = True

        if (
            self._extra_attr_video_streams_allowed
            != self.client.attributes.video_streams_allowed
        ):
            self._extra_attr_video_streams_allowed = (
                self.client.attributes.video_streams_allowed
            )
            write_state = True

        if (
            self._extra_attr_video_stream_connections
            != self.client.attributes.video_stream_connections
        ):
            self._extra_attr_video_stream_connections = (
                self.client.attributes.video_stream_connections
            )
            write_state = True

        if write_state:
            self.schedule_update_ha_state()

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes"""
        return {
            attr: value
            for attr, value in (
                ("video_streams_allowed", self._extra_attr_video_streams_allowed),
                ("video_stream_connections", self._extra_attr_video_stream_connections),
            )
            if value is not None
        }
