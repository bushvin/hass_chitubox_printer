"""Image platform for SDCP Printer integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import SDCPDeviceImageEntityDescription
from .entity import SDCPDeviceImage

IMAGES: tuple[SDCPDeviceImageEntityDescription, ...] = (
    SDCPDeviceImageEntityDescription(
        key="Thumbnail",
        name="Thumbnail",
        icon="mdi:image",
        image_url=lambda _client: getattr(
            _client.current_task, "thumbnail", STATE_UNKNOWN
        ),
        extra_state_attributes={
            "thumbnail_url": lambda _client: getattr(
                _client.current_task, "thumbnail", STATE_UNKNOWN
            )
        },
        available=lambda _client: (
            _client.is_connected and hasattr(_client.current_task, "thumbnail")
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the available ChituBox images."""

    assert entry.unique_id is not None

    for image in IMAGES:
        async_add_entities(
            [SDCPDeviceImage(config_entry=entry, entity_description=image, hass=hass)],
            update_before_add=True,
        )
