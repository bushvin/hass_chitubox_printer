from __future__ import annotations

import logging
from typing import Any, final

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.image import ImageEntity, ImageEntityDescription
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import (
    CONF_FILENAME,
    CONF_NAME,
    PERCENTAGE,
    STATE_OFF,
    STATE_OK,
    STATE_ON,
    STATE_PROBLEM,
    STATE_UNKNOWN,
    EntityCategory,
    UnitOfTemperature,
)
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import (
    CONF_BRAND,
    CONF_MODEL,
    CONF_START_LAYER,
    DOMAIN,
    STATE_OFFLINE,
    SDCPPrinterEntityFeature,
)

_LOGGER = logging.getLogger(__name__)

IMAGE_TYPE = ImageEntityDescription(
    key="thumbnail",
    translation_key="thumbnail",
)


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
    def available(self):
        """Return True if entity is available."""
        return self.client.is_connected

    def _eval_values(self, old_value, new_value, on_not_connected=STATE_OFFLINE):
        """Eval given values if connected"""
        if not self.client.is_connected:
            new_value = on_not_connected.capitalize()

        if old_value != new_value:
            return (new_value, True)
        else:
            return (old_value, False)


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


class SDCPPrinterSwitchBase(SDCPPrinterEntity, SwitchEntity):

    def __init__(self, entry):
        super().__init__(entry)
        SwitchEntity.__init__(self)


class SDCPPrinterImageBase(SDCPPrinterEntity, ImageEntity):

    def __init__(self, entry, hass):
        super().__init__(entry)
        ImageEntity.__init__(self, hass)


class SDCPPrinterSensor(SDCPPrinterSensorBase):
    """ChituBox Printer State"""

    _attr_icon = "mdi:printer-3d"
    _attr_supported_features: SDCPPrinterEntityFeature = SDCPPrinterEntityFeature(0) | (
        SDCPPrinterEntityFeature.PAUSE
        | SDCPPrinterEntityFeature.RESUME
        | SDCPPrinterEntityFeature.STOP
    )
    _attr_device_class = "3d-printer"
    _attr_extra_state_attributes = {
        "action": STATE_UNKNOWN,
        "all_statuses": STATE_UNKNOWN,
        "previous_state": STATE_UNKNOWN,
    }
    _attr_native_value = STATE_OFFLINE.capitalize()
    sdcp_entity_type = "Printer"

    def _client_update_status(self, message):
        """Handle status updates"""
        write_state = False

        self._attr_native_value, has_changed = self._eval_values(
            self._attr_native_value,
            (
                STATE_IDLE.capitalize()  # noqa: F821
                if len(self.client.status.machine_status) < 1
                else self.client.status.machine_status[0].capitalize()
            ),
        )

        write_state = write_state or has_changed

        _attr_extra_state_attributes = {
            "action": self.client.status.print_status,
            "all_statuses": self.client.status.machine_status,
            "previous_state": self.client.status.machine_previous_status,
        }
        if self._attr_extra_state_attributes != _attr_extra_state_attributes:
            self._attr_extra_state_attributes = _attr_extra_state_attributes
            write_state = True

        if write_state and self.hass is not None:
            self.schedule_update_ha_state()

    @property
    @final
    def state(self):
        if self.client.is_connected:
            return super().state
        else:
            return STATE_OFFLINE.capitalize()

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
        self.logger.warning(
            "The 'Turn timelapse off' service is deprecated and will be removed as of release 2025.5.1, use the timelapse switch instead."
        )
        self.client.turn_timelapse_off()

    def svc_turn_timelapse_on(self):
        """Turn timelapse on"""
        self.logger.warning(
            "The 'Turn timelapse on' service is deprecated and will be removed as of release 2025.5.1, use the timelapse switch instead."
        )
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

    _attr_extra_state_attributes = {
        "current_layer": STATE_UNKNOWN,
        "filename": STATE_UNKNOWN,
        "time_remaining_ms": STATE_UNKNOWN,
        "timelapse_url": STATE_UNKNOWN,
        "total_layers": STATE_UNKNOWN,
        "total_time_ms": STATE_UNKNOWN,
    }

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    sdcp_entity_type = "Job Progress"

    def _client_update_status(self, message):
        """Handle status updates"""
        write_state = False

        self._attr_native_value, has_changed = self._eval_values(
            self._attr_native_value,
            (
                0
                if self.client.status.print_progress is None
                else round(self.client.status.print_progress, 2)
            ),
        )
        write_state = write_state or has_changed

        _attr_extra_state_attributes = {
            "current_layer": self.client.status.print_current_layer,
            "filename": self.client.status.print_filename,
            "time_remaining_ms": self.client.status.print_total_time,
            "timelapse_url": (
                self.client.current_task.timelapse_url
                if hasattr(self.client.current_task, "timelapse_url")
                else STATE_UNKNOWN
            ),
            "total_layers": self.client.status.print_total_layers,
            "total_time_ms": self.client.status.print_total_time,
        }

        if self._attr_extra_state_attributes != _attr_extra_state_attributes:
            self._attr_extra_state_attributes = _attr_extra_state_attributes
            write_state = True

        if write_state and self.hass is not None:
            self.schedule_update_ha_state()


class SDCPPrinterFinishTimeSensor(SDCPPrinterSensorBase):
    """Finish Time of the print"""

    _attr_icon = "mdi:clock-end"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    sdcp_entity_type = "Print job estimated finish time"

    def _client_update_status(self, message):
        """Handle status updates"""

        write_state = False
        new_time = self.client.status.print_finished_at_datetime
        if new_time is not None and new_time.tzinfo is None:
            new_time = new_time.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)

        old_state = None
        if hasattr(self._attr_native_value, "timestamp") and callable(
            self._attr_native_value.timestamp
        ):
            old_state = self._attr_native_value.timestamp()

        if hasattr(new_time, "timestamp") and old_state != new_time.timestamp():
            self._attr_native_value = new_time
            write_state = True
        elif new_time is None and old_state is not None:
            self._attr_native_value = None
            write_state = True

        if write_state and self.hass is not None:
            self.schedule_update_ha_state()


class SDCPPrinterStartTimeSensor(SDCPPrinterSensorBase):
    """Start Time of the print"""

    _attr_icon = "mdi:clock-start"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    sdcp_entity_type = "Print job start time"

    def _client_update_status(self, message):
        """Handle status updates"""

        write_state = False
        new_time = self.client.status.print_started_at_datetime
        if new_time is not None and new_time.tzinfo is None:
            new_time = new_time.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)

        old_state = None
        if hasattr(self._attr_native_value, "timestamp") and callable(
            self._attr_native_value.timestamp
        ):
            old_state = self._attr_native_value.timestamp()

        if hasattr(new_time, "timestamp") and old_state != new_time.timestamp():
            self._attr_native_value = new_time
            write_state = True
        elif new_time is None and old_state is not None:
            self._attr_native_value = None
            write_state = True

        if write_state and self.hass is not None:
            self.schedule_update_ha_state()


class SDCPPrinterReleaseFilmSensor(SDCPPrinterSensorBase):
    """Release Film status"""

    _attr_icon = "mdi:filmstrip-box"
    _attr_extra_state_attributes = {
        "release_film_use_count": STATE_UNKNOWN,
        "release_film_max_uses": STATE_UNKNOWN,
    }
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    sdcp_entity_type = "Release Film Status"

    def _client_update_status(self, message):
        """Handle status updates"""

        write_state = False

        self._attr_native_value, has_changed = self._eval_values(
            self._attr_native_value,
            (
                STATE_OK.capitalize()
                if self.client.attributes.release_film_status == "normal"
                else STATE_PROBLEM.capitalize()
            ),
        )
        write_state = write_state or has_changed

        _attr_extra_state_attributes = {
            "release_film_use_count": (
                self.client.status.release_film_use_count
                if hasattr(self.client.status, "release_film_use_count")
                else STATE_UNKNOWN
            ),
            "release_film_max_uses": (
                self.client.attributes.release_film_max_uses
                if hasattr(self.client.attributes, "release_film_max_uses")
                else STATE_UNKNOWN
            ),
        }
        if self._attr_extra_state_attributes != _attr_extra_state_attributes:
            self._attr_extra_state_attributes = _attr_extra_state_attributes
            write_state = True

        if write_state and self.hass is not None:
            self.schedule_update_ha_state()


class SDCPPrinterTemperatureSensor(SDCPPrinterSensorBase):
    """Temperature of the printer enclosure"""

    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_extra_state_attributes = {
        "target_enclosure_temperature": STATE_UNKNOWN,
    }
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    sdcp_entity_type = "Enclosure Temperature"

    def _client_update_status(self, message):
        """Handle status updates"""
        write_state = False

        self._attr_native_value, has_changed = self._eval_values(
            self._attr_native_value,
            (
                None
                if self.client.status.enclosure_temperature is None
                else round(self.client.status.enclosure_temperature, 2)
            ),
        )
        write_state = write_state or has_changed

        _attr_extra_state_attributes = {
            "target_enclosure_temperature": self.client.status.enclosure_target_temperature,
        }
        if self._attr_extra_state_attributes != _attr_extra_state_attributes:
            self._attr_extra_state_attributes = _attr_extra_state_attributes
            write_state = True

        if write_state and self.hass is not None:
            self.schedule_update_ha_state()


class SDCPPrinterUVLEDTemperatureSensor(SDCPPrinterSensorBase):
    """Temperature of the printer enclosure"""

    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_extra_state_attributes = {
        "max_temperature": STATE_UNKNOWN,
    }
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    sdcp_entity_type = "UV LED Temperature"

    def _client_update_status(self, message):
        """Handle status updates"""
        write_state = False

        self._attr_native_value, has_changed = self._eval_values(
            self._attr_native_value,
            (
                None
                if self.client.status.uvled_temperature is None
                else round(self.client.status.uvled_temperature, 2)
            ),
        )
        write_state = write_state or has_changed

        _attr_extra_state_attributes = {
            "max_temperature": self.client.attributes.uvled_max_temp,
        }
        if self._attr_extra_state_attributes != _attr_extra_state_attributes:
            self._attr_extra_state_attributes = _attr_extra_state_attributes
            write_state = True

        if write_state and self.hass is not None:
            self.schedule_update_ha_state()


class SDCPPrinterUSBDiskConnectedBinarySensor(SDCPPrinterBinarySensor):
    """USB Disk Connected"""

    _attr_icon = "mdi:usb-flash-drive"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    sdcp_entity_type = "USB Disk Connected"

    def _client_update_attributes(self, message):
        """Handle status updates"""

        if not self.client.is_connected:
            is_on = STATE_OFFLINE
        elif self.client.attributes.usbdisk_connected is None:
            is_on = STATE_UNKNOWN
        else:
            is_on = self.client.attributes.usbdisk_connected

        if self._attr_is_on != is_on:
            self._attr_is_on = is_on
            if self.hass is not None:
                self.schedule_update_ha_state()


class SDCPPrinterUVLEDConnectedBinarySensor(SDCPPrinterBinarySensor):
    """UV LED Connected"""

    _attr_icon = "mdi:led-on"
    _attr_extra_state_attributes = {
        "status": STATE_UNKNOWN,
    }
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    sdcp_entity_type = "UV LED Connected"

    def _client_update_attributes(self, message):
        """Handle status updates"""

        write_state = False

        if not self.client.is_connected:
            is_on = STATE_OFFLINE
        elif self.client.attributes.uvled_temp_sensor_connected is None:
            is_on = STATE_UNKNOWN
        else:
            is_on = self.client.attributes.uvled_temp_sensor_connected

        if self._attr_is_on != is_on:
            self._attr_is_on = is_on
            write_state = True

        _attr_extra_state_attributes = {
            "status": self.client.attributes.uvled_temp_sensor_status,
        }
        if self._attr_extra_state_attributes != _attr_extra_state_attributes:
            self._attr_extra_state_attributes = _attr_extra_state_attributes
            write_state = True

        if write_state and self.hass is not None:
            self.schedule_update_ha_state()


class SDCPPrinterLCDConnectedBinarySensor(SDCPPrinterBinarySensor):
    """Exposure Screen Connected"""

    _attr_icon = "mdi:fit-to-screen"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    sdcp_entity_type = "Exposure Screen Connected"

    def _client_update_attributes(self, message):
        """Handle status updates"""

        if not self.client.is_connected:
            is_on = STATE_OFFLINE
        elif self.client.attributes.lcd_connected is None:
            is_on = STATE_UNKNOWN
        else:
            is_on = self.client.attributes.lcd_connected

        if self._attr_is_on != is_on:
            self._attr_is_on = is_on
            if self.hass is not None:
                self.schedule_update_ha_state()


class SDCPPrinterStrainGaugeConnectedBinarySensor(SDCPPrinterBinarySensor):
    """UV LED COnnected"""

    _attr_icon = "mdi:led-on"
    _attr_extra_state_attributes = {
        "status": STATE_UNKNOWN,
    }
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    sdcp_entity_type = "Strain Gauge Connected"

    def _client_update_attributes(self, message):
        """Handle status updates"""

        write_state = False

        if not self.client.is_connected:
            is_on = STATE_OFFLINE
        elif self.client.attributes.strain_gauge_connected is None:
            is_on = STATE_UNKNOWN
        else:
            is_on = self.client.attributes.strain_gauge_connected

        if self._attr_is_on != is_on:
            self._attr_is_on = is_on
            write_state = True

        _attr_extra_state_attributes = {
            "status": self.client.attributes.strain_gauge_status,
        }
        if self._attr_extra_state_attributes != _attr_extra_state_attributes:
            self._attr_extra_state_attributes = _attr_extra_state_attributes
            write_state = True

        if write_state and self.hass is not None:
            self.schedule_update_ha_state()


class SDCPPrinterZmotorConnectedBinarySensor(SDCPPrinterBinarySensor):
    """Z-Motor Connected"""

    _attr_icon = "mdi:axis-z-arrow"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    sdcp_entity_type = "Z-Motor Connected"

    def _client_update_attributes(self, message):
        """Handle status updates"""

        if not self.client.is_connected:
            is_on = STATE_OFFLINE
        elif self.client.attributes.z_motor_connected is None:
            is_on = STATE_UNKNOWN
        else:
            is_on = self.client.attributes.z_motor_connected

        if self._attr_is_on != is_on:
            self._attr_is_on = is_on
            if self.hass is not None:
                self.schedule_update_ha_state()


class SDCPPrinterRotaryMotorConnectedBinarySensor(SDCPPrinterBinarySensor):
    """Z-Motor Connected"""

    _attr_icon = "mdi:rotate-360"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    sdcp_entity_type = "Rotary Motor Connected"

    def _client_update_attributes(self, message):
        """Handle status updates"""

        if not self.client.is_connected:
            is_on = STATE_OFFLINE
        elif self.client.attributes.rotary_motor_connected is None:
            is_on = STATE_UNKNOWN
        else:
            is_on = self.client.attributes.rotary_motor_connected

        if self._attr_is_on != is_on:
            self._attr_is_on = is_on
            if self.hass is not None:
                self.schedule_update_ha_state()


class SDCPPrinterCameraConnectedBinarySensor(SDCPPrinterBinarySensor):
    """Camera Connected"""

    _attr_icon = "mdi:camera"
    _attr_extra_state_attributes = {
        "video_streams_allowed": STATE_UNKNOWN,
        "video_stream_connections": STATE_UNKNOWN,
    }
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    sdcp_entity_type = "Camera Connected"

    def _client_update_attributes(self, message):
        """Handle status updates"""

        write_state = False

        if not self.client.is_connected:
            is_on = STATE_OFFLINE
        elif self.client.attributes.camera_connected is None:
            is_on = STATE_UNKNOWN
        else:
            is_on = (
                STATE_ON if bool(self.client.attributes.camera_connected) else STATE_OFF
            )

        if self._attr_is_on != is_on:
            self._attr_is_on = is_on
            write_state = True

        _attr_extra_state_attributes = {
            "video_streams_allowed": self.client.attributes.video_streams_allowed,
            "video_stream_connections": self.client.attributes.video_stream_connections,
        }

        if self._attr_extra_state_attributes != _attr_extra_state_attributes:
            self._attr_extra_state_attributes = _attr_extra_state_attributes
            write_state = True

        if write_state and self.hass is not None:
            self.schedule_update_ha_state()


class SDCPPrinterTimelapseSwitch(SDCPPrinterSwitchBase):

    _attr_icon = "mdi:camera-burst"
    _attr_is_on = STATE_OFFLINE

    sdcp_entity_type = "Timelapse"

    def _client_update_status(self, message):
        """Handle status updates"""

        if not self.client.is_connected:
            is_on = STATE_OFFLINE
        elif self.client.status.timelapse_enabled:
            is_on = True
        else:
            is_on = False

        if self._attr_is_on != is_on:
            self._attr_is_on = is_on
            if self.hass is not None:
                self.schedule_update_ha_state()

    def turn_on(self, **kwargs):
        self.client.turn_timelapse_on()
        self._attr_is_on = True
        if self.hass is not None:
            self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        self.client.turn_timelapse_off()
        self._attr_is_on = False
        if self.hass is not None:
            self.schedule_update_ha_state()


class SDCPPrinterThumbnail(SDCPPrinterImageBase):

    _attr_image_url = None
    _attr_image_last_updated = dt_util.now()

    _attr_extra_state_attributes = {
        "thumbnail_url": STATE_UNKNOWN,
    }

    sdcp_entity_type = "Thumbnail"
    entity_description = IMAGE_TYPE

    @property
    def icon(self):
        """Return an icon when there is no thumbnail"""
        if self._attr_image_url is None or not self.client.is_connected:
            return "mdi:image"
        else:
            return None

    def _client_update_status(self, message):
        """Handle status updates"""
        write_state = False

        self._attr_image_url, has_changed = self._eval_values(
            self._attr_image_url,
            (
                None
                if not hasattr(self.client.current_task, "thumbnail")
                else self.client.current_task.thumbnail
            ),
        )

        write_state = write_state or has_changed

        if write_state and self.hass is not None:
            self._attr_image_last_updated = dt_util.now()
            self.schedule_update_ha_state()

    async def _fetch_url(self, url: str):
        """Fetch a URL.

        Chitubox provides 'text/plain' as content type
        so this is a hack to provide a correct image content type
        to Home Assistant.
        """

        response = await super()._fetch_url(url)
        response.headers["content-type"] = "image/bmp"

        return response
