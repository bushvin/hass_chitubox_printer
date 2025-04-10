from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import SDCPPrinterTimelapseSwitch


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the available ChituBox switches."""

    assert entry.unique_id is not None

    entities = [
        SDCPPrinterTimelapseSwitch(entry),
    ]

    async_add_entities(entities)
