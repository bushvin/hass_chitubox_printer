"""Binary Sensor platform for SDCP Printer integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import SDCPDeviceBinarySensorEntityDescription
from .entity import SDCPDeviceBinarySensor

BINARY_SENSORS: tuple[SDCPDeviceBinarySensorEntityDescription, ...] = (
    SDCPDeviceBinarySensorEntityDescription(
        key="USB Disk Connected",
        name="USB Disk Connected",
        icon="mdi:usb-flash-drive",
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on=lambda _client: _client.attributes.usbdisk_connected,
    ),
    SDCPDeviceBinarySensorEntityDescription(
        key="UV LED Connected",
        name="UV LED Connected",
        icon="mdi:led-on",
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on=lambda _client: _client.attributes.uvled_temp_sensor_connected,
        extra_state_attributes={
            "status": lambda _client: _client.attributes.uvled_temp_sensor_status
        },
    ),
    SDCPDeviceBinarySensorEntityDescription(
        key="Exposure Screen Connected",
        name="Exposure Screen Connected",
        icon="mdi:fit-to-screen",
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on=lambda _client: _client.attributes.lcd_connected,
    ),
    SDCPDeviceBinarySensorEntityDescription(
        key="Strain Gauge Connected",
        name="Strain Gauge Connected",
        icon="mdi:led-on",
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on=lambda _client: _client.attributes.strain_gauge_connected,
        extra_state_attributes={
            "status": lambda _client: _client.attributes.strain_gauge_status
        },
    ),
    SDCPDeviceBinarySensorEntityDescription(
        key="Z-Motor Connected",
        name="Z-Motor Connected",
        icon="mdi:axis-z-arrow",
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on=lambda _client: _client.attributes.z_motor_connected,
    ),
    SDCPDeviceBinarySensorEntityDescription(
        key="Rotary Motor Connected",
        name="Rotary Motor Connected",
        icon="mdi:rotate-360",
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on=lambda _client: _client.attributes.rotary_motor_connected,
    ),
    SDCPDeviceBinarySensorEntityDescription(
        key="Camera Connected",
        name="Camera Connected",
        icon="mdi:camera",
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on=lambda _client: _client.attributes.camera_connected,
        extra_state_attributes={
            "video_streams_allowed": lambda _client: _client.attributes.video_streams_allowed,
            "video_stream_connections": lambda _client: _client.attributes.video_stream_connections,
            "video_stream_url": lambda _client: _client.video_url,
        },
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the available ChituBox sensors."""

    assert entry.unique_id is not None

    for sensor in BINARY_SENSORS:
        async_add_entities(
            [SDCPDeviceBinarySensor(config_entry=entry, entity_description=sensor)],
            update_before_add=True,
        )
