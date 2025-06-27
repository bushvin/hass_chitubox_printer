from __future__ import annotations

import io
import logging
from collections.abc import Mapping
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.image import ImageEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, STATE_OFF, STATE_ON, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.typing import StateType, UndefinedType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util
from PIL import Image

from . import (
    SDCPDeviceBinarySensorEntityDescription,
    SDCPDeviceImageEntityDescription,
    SDCPDeviceSensorEntityDescription,
    SDCPDeviceSwitchEntityDescription,
)
from .const import CONF_BRAND, CONF_MAINBOARD_ID, CONF_MODEL, DOMAIN
from .coordinator import SDCPDeviceCoordinator

_LOGGER = logging.getLogger(__name__)


class SDCPDeviceEntity(CoordinatorEntity[SDCPDeviceCoordinator]):
    """SDCPDevice base coordinator entity"""

    def __init__(self, coordinator: SDCPDeviceCoordinator):
        """Initialize"""
        super().__init__(coordinator)
        self._attr_unique_id = (
            f"{self.entity_description.key}-{self.config_entry.unique_id}"
        )
        self._attr_name = (
            f"{self.config_entry.data[CONF_NAME]} {self.entity_description.name}"
        )
        self._attr_extra_state_attributes = {}

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information about this entity."""
        device_info = DeviceInfo(
            identifiers={(DOMAIN, self.config_entry.unique_id)},
            name=self.config_entry.data[CONF_NAME],
            manufacturer=self.config_entry.data[CONF_BRAND],
            model=self.config_entry.data[CONF_MODEL],
            serial_number=self.config_entry.data[CONF_MAINBOARD_ID],
        )

        _client = self.config_entry.runtime_data.client
        if getattr(_client.attributes, "firmware_version", None) is not None:
            device_info["hw_version"] = _client.attributes.firmware_version

        _LOGGER.warning("device_info %s" % device_info)
        return device_info

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        if (
            hasattr(self, "entity_description")
            and self.entity_description.available is not None
        ):
            _client = self.config_entry.runtime_data.client
            return self.entity_description.available(_client)

        return False

    @property
    def is_printing(self) -> bool:
        """Return True if entity is printing."""
        if (
            hasattr(self, "entity_description")
            and self.entity_description.is_printing is not None
        ):
            _client = self.config_entry.runtime_data.client
            return self.entity_description.is_printing(_client)

        return False

    @property
    def supported_features(self) -> int | None:
        """Flag supported features."""
        if (
            hasattr(self, "entity_description")
            and hasattr(self.entity_description, "supported_features")
            and self.entity_description.supported_features is not None
        ):
            self._attr_supported_features = self.entity_description.supported_features

        return super().supported_features

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        if (
            hasattr(self, "entity_description")
            and self.entity_description.extra_state_attributes is not None
        ):
            self._attr_extra_state_attributes = {}
            _client = self.config_entry.runtime_data.client
            for attr, value in self.entity_description.extra_state_attributes.items():
                self._attr_extra_state_attributes[attr] = value(_client)

        return super().extra_state_attributes


class SDCPDeviceBinarySensor(SDCPDeviceEntity, BinarySensorEntity):
    """SDCPDevice binary sensor"""

    def __init__(
        self,
        config_entry: ConfigEntry,
        entity_description: SDCPDeviceBinarySensorEntityDescription,
    ) -> None:
        """Initialize"""
        self.config_entry: ConfigEntry = config_entry
        self.coordinator: SDCPDeviceCoordinator = config_entry.runtime_data.coordinator
        self.entity_description: SDCPDeviceBinarySensorEntityDescription = (
            entity_description
        )
        self.client = config_entry.runtime_data.client
        super().__init__(self.coordinator)
        BinarySensorEntity.__init__(self)

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        if (
            hasattr(self, "entity_description")
            and self.entity_description.is_on is not None
        ):
            _client = self.config_entry.runtime_data.client
            is_on = self.entity_description.is_on(_client)
            if isinstance(is_on, bool) and is_on:
                return STATE_ON
            elif isinstance(is_on, bool):
                return STATE_OFF

        return STATE_UNKNOWN


class SDCPDeviceImage(SDCPDeviceEntity, ImageEntity):
    """SDCPDevice Image"""

    def __init__(
        self,
        config_entry: ConfigEntry,
        entity_description: SDCPDeviceImageEntityDescription,
        hass: HomeAssistant,
    ) -> None:
        """Initialize"""

        self.config_entry: ConfigEntry = config_entry
        self.entity_description: SDCPDeviceImageEntityDescription = entity_description
        self.coordinator: SDCPDeviceCoordinator = config_entry.runtime_data.coordinator
        self.client = config_entry.runtime_data.client
        self.hass = hass
        super().__init__(self.coordinator)
        ImageEntity.__init__(self, self.hass)

        self._attr_image_last_updated = dt_util.utcnow()

    @property
    def icon(self):
        """Return an icon when there is no thumbnail"""
        if not self.available or not self.is_printing:
            return self.entity_description.icon

        if (
            hasattr(self, "entity_description")
            and self.entity_description.icon is not None
            and self._attr_image_url is None
        ):
            return super().icon
        else:
            return None

    @property
    def image_url(self) -> str | None | UndefinedType:
        """Return URL of image."""
        if not self.available or not self.is_printing:
            self._cached_image = None
            return None

        if (
            hasattr(self, "entity_description")
            and self.entity_description.image_url is not None
        ):
            _client = self.config_entry.runtime_data.client
            new_image_url = self.entity_description.image_url(_client)
            if new_image_url != self._attr_image_url:
                self._cached_image = None
                self._attr_image_last_updated = dt_util.now()
                self._attr_image_url = new_image_url

            return self._attr_image_url

        return None

    @property
    def entity_picture(self) -> str | None:
        """Return the entity picture to use in the frontend, if any."""

        if not self.available or not self.is_printing:
            self._cached_image = None
            return None

        if hasattr(self, "entity_description") and self._attr_image_url is not None:
            return super().entity_picture

        return None

    async def _fetch_url(self, url: str):
        """Fetch a URL.

        Chitubox provides 'text/plain' as content type
        so this is a hack to provide a correct image content type
        to Home Assistant.
        """

        response = await super()._fetch_url(url)
        response.headers["content-type"] = "image/bmp"

        return response

    async def _async_load_image_from_url(self, url: str):
        """Load an image by url

        Chitubox thumbnail is bitmap, which is no longer/not supported
        by many browsers. This converts the bitmap into png, which is
        widely supported."
        """

        image = await super()._async_load_image_from_url(url)
        if image is not None:
            new_image = Image.open(io.BytesIO(image.content))
            buffer = io.BytesIO()
            new_image.save(buffer, "PNG")
            image.content = buffer.getvalue()
            image.content_type = "image/png"

        return image


class SDCPDeviceSwitch(SDCPDeviceEntity, SwitchEntity):
    """SDCPDevice Switch"""

    def __init__(
        self,
        config_entry: ConfigEntry,
        entity_description: SDCPDeviceSwitchEntityDescription,
    ) -> None:
        """Initialize"""
        self.config_entry: ConfigEntry = config_entry
        self.coordinator: SDCPDeviceCoordinator = config_entry.runtime_data.coordinator
        self.entity_description: SDCPDeviceSwitchEntityDescription = entity_description
        self.client = config_entry.runtime_data.client
        super().__init__(self.coordinator)
        SwitchEntity.__init__(self)

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        if (
            hasattr(self, "entity_description")
            and self.entity_description.is_on is not None
        ):
            _client = self.config_entry.runtime_data.client
            is_on = self.entity_description.is_on(_client)
            if isinstance(is_on, bool) and is_on:
                return STATE_ON
            elif isinstance(is_on, bool):
                return STATE_OFF

        return STATE_UNKNOWN

    def turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        if (
            hasattr(self, "entity_description")
            and self.entity_description.turn_on is not None
        ):
            _client = self.config_entry.runtime_data.client
            self.entity_description.turn_on(_client)

    def turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        if (
            hasattr(self, "entity_description")
            and self.entity_description.turn_off is not None
        ):
            _client = self.config_entry.runtime_data.client
            self.entity_description.turn_off(_client)


class SDCPDeviceSensor(SDCPDeviceEntity, SensorEntity):
    """SDCPDevice Sensor Device"""

    def __init__(
        self,
        config_entry: ConfigEntry,
        entity_description: SDCPDeviceSensorEntityDescription,
    ) -> None:
        """Initialize"""
        self.config_entry: ConfigEntry = config_entry
        self.coordinator: SDCPDeviceCoordinator = config_entry.runtime_data.coordinator
        self.entity_description: SDCPDeviceSensorEntityDescription = entity_description
        self.client = config_entry.runtime_data.client
        super().__init__(self.coordinator)

    @property
    def native_value(self) -> StateType | date | datetime | Decimal:
        """Return the value reported by the sensor."""
        if not self.available:
            return None

        if (
            hasattr(self, "entity_description")
            and self.entity_description.native_value is not None
        ):
            _client = self.config_entry.runtime_data.client
            new_value = self.entity_description.native_value(_client)
            if (
                self.device_class == SensorDeviceClass.TIMESTAMP
                and new_value is not None
                and new_value.tzinfo is None
            ):
                new_value = new_value.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)

            if new_value != self._attr_native_value:
                self._attr_native_value = new_value

        return super().native_value
