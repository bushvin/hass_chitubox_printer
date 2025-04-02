# Chitubox Printer custom integration

[![Github Releases][github-releases-badge]][github-releases]

[![License][license-badge]][license]

[![BuyMeCoffee][ko-fi-badge]][ko-fi]
[![hacs][hacs-badge]][hacs]

This is a Home Assistant integration for Chitubox 3d printers using the [Smart Device Control Protocol](https://github.com/cbd-tech/SDCP-Smart-Device-Control-Protocol-V3.0.0).

In order to use this component, you need a 3d printer supporting the v3.0.0 of the SDCP protocol, and the printer should be connected to your network. The printer does not need to be in the same subnet as your computer, but you need to know it's IP address.

## Overview

This integration allows you to add multiple printers, if you have them. Each printer is represented by a device with multiple sensors (entities)

| :warning: | Due to the rtsp implementation on the printer, and the limited amounts of streams, it is impossible to implement a camera sensor. |
|---|:--|

### Entities

| :exclamation: | When the *Printer* entity's state becomes `offline` (because the printer is turned off), all other entities become *Unavailable*
|---|:--|

| sensor | type | attributes | description |
|---|---|---|---|
| Camera Connected | `binary_sensor` | `video_streams_allowed`,`video_stream_connections` | Diagnostic sensor showing whether the camera is connected or not. |
| Enclosure Temperature | `temperature sensor` | `max_temperature` | Diagnostic sensor showing the enclosure temperature. |
| Exposure Screen Connected | `binary_sensor` | none | Diagnostic sensor showing whether the exposure screen is connected or not. |
| Job progress | `percentage sensor` | `total_time_ms`, `time_remaining_ms`, `current_layer`, `total_layers` | Shows the progress of the print in percent |
| Print job estimated finish time | `datetime sensor` | none | Shows the Estimated time when the current print will be done |
| Print job start time | `datetime sensor` | none | Shows the time when the current print started |
| Printer | `sensor` | `previous_state`, `action`, `filename` | The main sensor. The current state of the printer.|
| Rotary Motor Connected | `binary_sensor` | none | Diagnostic sensor showing whether the rotary motor is connected or not. |
| Strain Gauge Connected | `binary_sensor` | `status` | Diagnostic sensor showing whether the strain gauge is connected or not. |
| UV LED Connected | `binary_sensor` | none | Diagnostic sensor showing whether the UV LED is connected or not. |
| UV LED Temperature | `temperature sensor` | `max_temperature` | Diagnostic sensor showing the UV LED temperature. |
| Z-Motor Connected | `binary_sensor` | none | Diagnostic sensor whether the Z-Motot is connected or not. |

### Services

The following services are available

#### chitubox_printer.pause_print_job

Pause the current printing job. This allows to resume the print later.

|Service data attribute|Optional|Description|Example|
|-|-|-|-|
| `entity_id` | no | Printer or Printer list of `entity_id`s to pause | `sensor.chitubox_printer` |

#### chitubox_printer.resume_print_job

Resume the paused printing job.

|Service data attribute|Optional|Description|Example|
|-|-|-|-|
| `entity_id` | no | Printer or Printer list of `entity_id`s to resume printing | `sensor.chitubox_printer` |

#### chitubox_printer.start_print_job

Start a new printing job.

|Service data attribute|Optional|Description|Example|
|-|-|-|-|
| `entity_id` | no | Printer or Printer list of `entity_id`s to start printing | `sensor.chitubox_printer` |
| `filename` | no | The name of a file to print on the printer or usb stick | `/usb/printme.ctb` |
| `start_layer` | no | The layer to start the print from | 0

#### chitubox_printer.stop_print_job

Stop the current printing job. The job cannot be resumed.

|Service data attribute|Optional|Description|Example|
|-|-|-|-|
| `entity_id` | no | Printer or Printer list of `entity_id`s to stop printing | `sensor.chitubox_printer` |

#### chitubox_printer.turn_timelapse_off

Turn off timelapse. There is no way to determine whether timelapse is on at this moment. This is due to the SDCP protocol.

|Service data attribute|Optional|Description|Example|
|-|-|-|-|
| `entity_id` | no | Printer or Printer list of `entity_id`s to turn off timelapse | `sensor.chitubox_printer` |

#### chitubox_printer.turn_timelapse_on

Turn on timelapse. There is no way to determine whether timelapse is on at this moment. This is due to the SDCP protocol.

|Service data attribute|Optional|Description|Example|
|-|-|-|-|
| `entity_id` | no | Printer or Printer list of `entity_id`s to turn on timelapse | `sensor.chitubox_printer` |

#### chitubox_printer.turn_camera_off

Turn off camera stream. There is no way to determine whether camera is on at this moment. This is due to the SDCP protocol.

|Service data attribute|Optional|Description|Example|
|-|-|-|-|
| `entity_id` | no | Printer or Printer list of `entity_id`s to turn off the camera | `sensor.chitubox_printer` |

#### chitubox_printer.turn_camera_on

Turn on camera stream. There is no way to determine whether camera is on at this moment. This is due to the SDCP protocol.

**url** `rtsp://<ip of printer>:554/video`

|Service data attribute|Optional|Description|Example|
|-|-|-|-|
| `entity_id` | no | Printer or Printer list of `entity_id`s to turn off the camera | `sensor.chitubox_printer` |

## Installation

1. Use [HACS](https://hacs.xyz/docs/setup/download), in `HACS` search for "Chitubox Printer". After adding `https://github.com/bushvin/hass_chitubox_printer` as a custom repository.
2. Restart Home Assistant
3. Add the integration: in the Home Assitant UI go to "Settings" -> "Devices & Services" then click "+ ADD INTEGRATION" and search for "Chitubox Printer"
4. Enter the chose name for your printer and its IP Address or hostname

## Tested Printers

This is a list of 3D printers on which this integration has been tested:

- Elegoo Saturn 4 Ultra

## Contributions are welcome

Reach out, and we'll figure out how to progress...

---

[github-releases]: https://github.com/bushvin/hass_chitubox_printer/releases
[github-releases-badge]: https://img.shields.io/github/v/release/bushvin/hass_chitubox_printer?style=flat-square&color=teal

[ko-fi]: https://ko-fi.com/bushvin
[ko-fi-badge]: https://img.shields.io/badge/ko--fi-bushvin-red?logo=ko-fi&logoColor=white&style=flat-square&color=teal
[hacs]: https://github.com/hacs/integration
[hacs-badge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=flat-square&color=teal
[license]: LICENSE
[license-badge]: https://img.shields.io/github/license/bushvin/hass_chitubox_printer?style=flat-square&color=teal
