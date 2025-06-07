# Change log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [CalVer](https://calver.org/about.html) versioning.

## [2025.6.3] - 2025-06-07

### Fixed

- issue with release drafter

## [2025.6.2] - 2025-06-06

### Changed

- `SDCPPrinterThumbnail` now provides a png instead of a bitmap image.

## [2025.6.1] - 2025-06-06

### Fixed

- `SDCPPrinterThumbnail.entity_picture` returns `None` when the printer if offline or not printing
- `SDCPPrinterThumbnail` empties image cache when thumbnail_url is changed to force reload the thumbnail
- `SDCPPrinterThumbnail` add thumbnail_url to state attributes
- `SDCPPrinterProgressSensor` add current_task_id to state attributes
- `SDCPPrinterThumbnail.icon` returns mdi:image when the printer is offline

## [2025.5.2] - 2025-05-15

### Fixed

- Workflow

## [2025.5.1] - 2025-05-15

### Fixed

- Bumped sdcpapi requirement to 2.4.0

## [2025.4.5] - 2025-04-22

### Added

- Thumbnail entity to show the thumbnail of the current job

### Fixed

- progress % now shows only 2 decimals
- progress is 0 when not printing
- printer is `Offline` when it is not available
- fixed an issue with updating the start and finish sensors
- capitalization of `Printer` and `Release Film status` state sensors

## [2025.4.4] - 2025-04-16

### Changed

- sdcpapi version bump (2.3.0)

### Fixed

- schedule_update_ha_state() can cause an issue when hass is not fully started
- *Print Job estimated Finish time* and *Print Job start time* were broken due to change in global `state` method in component (thanks, @ecentinela for raising this)

## [2025.4.3] - 2025-04-11

### Changed

- sdcpapi version bump (2.2.1)

## [2025.4.2] - 2025-04-10

This release introduces some more standardization among entities and leverage of the parent classes provided by HASS

### Added

- Timelapse control to enable/disable timelapse from a switch
- Release Film Status to provide information about the release film

### Changed

- all entities except for Printer and Timelapse are now diagnostic entities
- `chitubox_printer.turn_timelapse_off` is deprecated
- `chitubox_printer.turn_timelapse_on` is **deprecated**

## [2025.4.1] - 2025-04-02

This release includes a big number of updates, mostly due to a rewrite of the sdcpapi library.

Unfortunately no camera, as it has it's own challenges... Check the [README](./README.md).

### Added

- `chitubox_printer.start_print_job` service to start a new print job
- `chitubox_printer.turn_timelapse_off` service to turn off the creation of a timelapse video
- `chitubox_printer.turn_timelapse_on` service to turn on the creation of a timelapse video
- `chitubox_printer.turn_camera_off` service to turn off the camera stream (although the stream seems to be on all the time)
- `chitubox_printer.turn_camera_on` service to turn on the camera stream (although the stream seems to be on all the time)

### Fixed

- performance and stability

## [2025.3.1] - 2025-03-17

### Fixed

- missing import: re (thank you, @ecentinela)

## [2025.2.2] - 2025-02-07

### Fixed

- unloading an entry was failing

## [2025.2.1] - 2025-02-07

Some cleanup, rework and reorganization of the code

### Added

- services (pause, resume, stop)

### Changed

- all sensors are now in entity.py instead of the relevant platform sensor files for ease of use

### Fixed

- device is offline instead of unavailable when not turned on

## [2025.2.0] - 2025-02-01

This is the first release of this component.

### Added

- everything
