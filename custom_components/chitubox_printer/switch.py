"""Switch platform for SDCP Printer integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import SDCPDeviceSwitchEntityDescription
from .entity import SDCPDeviceSwitch

SWITCHES: tuple[SDCPDeviceSwitchEntityDescription, ...] = (
    SDCPDeviceSwitchEntityDescription(
        key="Timelapse",
        name="Timelapse",
        icon="mdi:camera-burst",
        is_on=lambda _client: _client.status.timelapse_enabled,
        turn_on=lambda _client: _client.turn_timelapse_on(),
        turn_off=lambda _client: _client.turn_timelapse_off(),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the available ChituBox switches."""

    assert entry.unique_id is not None

    for switch in SWITCHES:
        async_add_entities(
            [SDCPDeviceSwitch(config_entry=entry, entity_description=switch)],
            update_before_add=True,
        )
