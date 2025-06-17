"""Constants for ChituBox Printer integration."""

from datetime import timedelta
from enum import IntFlag

import voluptuous as vol
from homeassistant.const import CONF_FILENAME, Platform
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import VolDictType

DOMAIN = "chitubox_printer"
DEFAULT_NAME = "ChituBox"
CONF_BRAND = "device_brand"
CONF_MACHINE_BRAND_ID = "device_machine_brand_id"
CONF_MAINBOARD_ID = "device_mainboard_id"
CONF_MODEL = "device_model"
CONF_START_LAYER = "starting_layer"

SERVICE_PAUSE_PRINT_JOB = "pause_print_job"
SERVICE_RESUME_PRINT_JOB = "resume_print_job"
SERVICE_START_PRINT_JOB = "start_print_job"
SERVICE_STOP_PRINT_JOB = "stop_print_job"
SERVICE_TURN_TIMELAPSE_OFF = "turn_timelapse_off"
SERVICE_TURN_TIMELAPSE_ON = "turn_timelapse_on"
SERVICE_TURN_CAMERA_OFF = "turn_camera_off"
SERVICE_TURN_CAMERA_ON = "turn_camera_on"

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.IMAGE,
    Platform.SENSOR,
    Platform.SWITCH,
]

UPDATE_INTERVAL = timedelta(seconds=2)
STATE_OFFLINE = "offline"

SCHEMA_PAUSE_PRINT_JOB = {}
SCHEMA_RESUME_PRINT_JOB = {}
SCHEMA_START_PRINT_JOB: VolDictType = {
    vol.Required(CONF_FILENAME): cv.template,
    vol.Optional(CONF_START_LAYER, default=30): vol.Coerce(int),
}
SCHEMA_STOP_PRINT_JOB = {}
SCHEMA_TURN_TIMELAPSE_OFF = {}
SCHEMA_TURN_TIMELAPSE_ON = {}
SCHEMA_TURN_CAMERA_OFF = {}
SCHEMA_TURN_CAMERA_ON = {}

METHOD_PAUSE_PRINT_JOB = "svc_pause_print_job"
METHOD_RESUME_PRINT_JOB = "svc_resume_print_job"
METHOD_START_PRINT_JOB = "svc_start_print_job"
METHOD_STOP_PRINT_JOB = "svc_stop_print_job"
METHOD_TURN_TIMELAPSE_OFF = "svc_turn_timelapse_off"
METHOD_TURN_TIMELAPSE_ON = "svc_turn_timelapse_on"
METHOD_TURN_CAMERA_OFF = "svc_turn_camera_off"
METHOD_TURN_CAMERA_ON = "svc_turn_camera_on"


class SDCPPrinterEntityFeature(IntFlag):
    """Supported features of the SDCP Printer entity."""

    PAUSE = 1
    RESUME = 2
    STOP = 4
    START = 8
    TIMELAPSE_OFF = 16
    TIMELAPSE_ON = 32
    CAMERA_ON = 64
    CAMERA_OFF = 128
