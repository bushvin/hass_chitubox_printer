# Change log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [CalVer](https://calver.org/about.html) versioning.

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
