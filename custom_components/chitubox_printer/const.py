"""Constants for ChituBox Printer integration."""

from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "chitubox_printer"
# DEFAULT_PORT = 3000
DEFAULT_NAME = "ChituBox"
CONF_MACHINE_BRAND_ID = "device_machine_brand_id"
CONF_MAINBOARD_ID = "device_mainboard_id"
CONF_MODEL = "device_model"
CONF_BRAND = "device_brand"

# PLATFORMS = [
#     Platform.BINARY_SENSOR,
#     Platform.BUTTON,
#     Platform.CAMERA,
#     Platform.SENSOR,
#     ]

PLATFORMS = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
]

UPDATE_INTERVAL = timedelta(seconds=5)
