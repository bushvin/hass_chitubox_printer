"""Constants for ChituBox Printer integration."""

from datetime import timedelta
from enum import IntFlag, StrEnum

from homeassistant.const import Platform

DOMAIN = "chitubox_printer"
DEFAULT_NAME = "ChituBox"
CONF_MACHINE_BRAND_ID = "device_machine_brand_id"
CONF_MAINBOARD_ID = "device_mainboard_id"
CONF_MODEL = "device_model"
CONF_BRAND = "device_brand"

SERVICE_PAUSE_PRINT_JOB = "pause_print_job"
SERVICE_RESUME_PRINT_JOB = "resume_print_job"
SERVICE_STOP_PRINT_JOB = "stop_print_job"

PLATFORMS = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
]

UPDATE_INTERVAL = timedelta(seconds=5)

STATE_OFFLINE = "offline"

PAUSE_PRINT_JOB_SCHEMA = {}
RESUME_PRINT_JOB_SCHEMA = {}
STOP_PRINT_JOB_SCHEMA = {}


class SDCPPrinterEntityFeature(IntFlag):
    """Supported features of the SDCP Printer entity."""

    PAUSE = 1
    RESUME = 2
    STOP = 4
