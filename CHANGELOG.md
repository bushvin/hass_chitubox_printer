# Change log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [CalVer](https://calver.org/about.html) versioning.
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
