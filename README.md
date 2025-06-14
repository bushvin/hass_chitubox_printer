# Chitubox Printer custom integration

[![Github Releases][github-releases-badge]][github-releases]

[![License][license-badge]][license]

[![BuyMeCoffee][ko-fi-badge]][ko-fi]
[![hacs][hacs-badge]][hacs]

This is a Home Assistant integration for Chitubox 3d printers using the [Smart Device Control Protocol](https://github.com/cbd-tech/SDCP-Smart-Device-Control-Protocol-V3.0.0).

In order to use this component, you need a 3d printer supporting the v3.0.0 of the SDCP protocol, and the printer should be connected to your network. The printer does not need to be in the same subnet as your computer, but you need to know it's IP address.

## Overview

This integration allows you to add multiple printers, if you have them. Each printer is represented by a device with multiple sensors (entities)

### Camera

Due to the rtsp implementation on the printer, and the limited amounts of streams, it is impossible to implement a camera sensor in the integration. But...

A solution to this problem was discussed [here](https://github.com/danielcherubini/elegoo-homeassistant/issues/12), and the basis for this config.

But [AlexxIT](https://github.com/AlexxIT/)'s [WebRTC integration](https://github.com/AlexxIT/WebRTC) allows for you to show the camera stream.

Your exact URL can be found as an attribute (`video_stream_url`) for the `Camera Connected` sensor.

#### Elegoo Saturn 4

The functioning webrtc-camera card code is:

```yml
type: custom:webrtc-camera
url: >-
  ffmpeg:rtsp://<PRINTER_HOSTNAME>:554/video?#input=rtsp/udp#video=h264#media=video#resolution=1280x720#framerate=30

```

Replace `<PRINTER_HOSTNAME>` with your printer's hostname or IP address.

The number of video streams on the Elegoo Saturn 4 stream is officially capped at 2, so refreshing often or connecting to your Home Assistant dashboard from multiple devices may at some point stop working.

### Entities

| :exclamation: | When the *Printer* entity's state becomes `offline` (because the printer is turned off), all other entities become *Unavailable* |
|---|:--|

#### Controls

| sensor | type | attributes | description |
|---|---|---|---|
| Timelapse | `switch` | none | Control your device's timelapse function. |

#### Sensors

| sensor | type | attributes | description |
|---|---|---|---|
| Printer | `sensor` | `action`, `all_statuses`, `previous_state` | The main sensor. The current state of the printer.|
| Thumbnail | `image` | `thumbnail_url` | The thumbnail of the current print job. |

#### Diagnostic

| sensor | type | attributes | description |
|---|---|---|---|
| Camera Connected | `binary_sensor` | `video_streams_allowed`,`video_stream_connections`, `video_stream_url` | Sensor showing whether the camera is connected or not. |
| Enclosure Temperature | `temperature sensor` | `target_enclosure_temperature` | Sensor showing the enclosure temperature. |
| Exposure Screen Connected | `binary_sensor` | none | Sensor showing whether the exposure screen is connected or not. |
| Job progress | `percentage sensor` | `current_layer`, `filename`, `time_remaining_ms`, `timelapse_url`, `total_layers`, `total_time_ms` | Shows the progress of the print in percent |
| Print job estimated finish time | `datetime sensor` | none | Shows the Estimated time when the current print will be done |
| Print job start time | `datetime sensor` | none | Shows the time when the current print started |
| Release Film Status | `sensor` | `release_film_use_count`, `release_film_max_uses` | Shows the status of your Release Film |
| Rotary Motor Connected | `binary_sensor` | none | Sensor showing whether the rotary motor is connected or not. |
| Strain Gauge Connected | `binary_sensor` | `status` | Sensor showing whether the strain gauge is connected or not. |
| USB Disk Connected | `binary_sensor` | none | Sensor showing whether a USB disk is connected or not. |
| UV LED Connected | `binary_sensor` | none | Sensor showing whether the UV LED is connected or not. |
| UV LED Temperature | `temperature sensor` | `max_temperature` | Sensor showing the UV LED temperature. |
| Z-Motor Connected | `binary_sensor` | none | Sensor whether the Z-Motor is connected or not. |

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

***:warning: DEPRECATED*** use the timelapse switch

Turn off timelapse. There is no way to determine whether timelapse is on at this moment. This is due to the SDCP protocol.

|Service data attribute|Optional|Description|Example|
|-|-|-|-|
| `entity_id` | no | Printer or Printer list of `entity_id`s to turn off timelapse | `sensor.chitubox_printer` |

#### chitubox_printer.turn_timelapse_on

***:warning: DEPRECATED*** use the timelapse switch

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
- Elegoo Saturn 4 Ultra 16k

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
