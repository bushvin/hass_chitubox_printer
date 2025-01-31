"""Sensor platform for SDCP Printer integration."""
from __future__ import annotations

import logging
import datetime
import time

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_ID, PERCENTAGE, UnitOfTemperature, STATE_ON, STATE_OFF, STATE_UNKNOWN
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo

from .const import DOMAIN, CONF_MACHINE_BRAND_ID, CONF_MAINBOARD_ID, CONF_MODEL, CONF_BRAND, DEFAULT_NAME
from .coordinator import SDCPDeviceCoordinator

from homeassistant.components.binary_sensor import BinarySensorEntity

# from homeassistant.components.sensor import (
#     SensorEntity,
#     SensorDeviceClass,
#     SensorStateClass,
# )

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
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
        SDCPPrinterUSBDiskStatusSensor(entry),
    ]

    async_add_entities(entities)

class SDCPPrinterBinarySensorBase(CoordinatorEntity, BinarySensorEntity):
    """Representation of a ChituBox printer binary sensor."""

    def __init__(self, entry):
        """Initialize the sensor."""
        super().__init__(entry.runtime_data)
        self.entry = entry

        self.client = self.coordinator.client

        self._device_id = self.entry.unique_id

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
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.client.is_available

class SDCPPrinterUSBDiskStatusSensor(SDCPPrinterBinarySensorBase):
    """USB Disk enabled"""
    _attr_icon = "mdi:usb-flash-drive"

    def __update_status(self, message):
        _LOGGER.debug("Received Status Update")

        if message.usbdisk_connected is None:
            return STATE_UNKNOWN


        self._attr_state = STATE_ON if bool(message.usbdisk_connected) else STATE_OFF

        self.schedule_update_ha_state(force_refresh=True)

    def __init__(self, entry):
        super().__init__(entry)

        self._attr_state = None
        self._attr_available = True

        self.client.add_callback("on_attributes_update", self.__update_status)
        self.sensor_type = "USB Disk Enabled"

        self._attr_name = f"{self.entry.data[CONF_NAME]} {self.sensor_type}"
        self._attr_unique_id = f"{self.sensor_type}-{self._device_id}"

    @property
    def state(self):
        return self._attr_state
