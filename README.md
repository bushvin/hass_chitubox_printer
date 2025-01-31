# Chitubox Printer custom integration

[![BuyMeCoffee][ko-fi-badge]][ko-fi]

[![hacs][hacs-badge]][hacs]

This is a Home Assistant integration for Chitupox 3d printers using the [Smart Device Control Protocol](https://github.com/cbd-tech/SDCP-Smart-Device-Control-Protocol-V3.0.0).

In order to use this component, you need a 3d printer supporting the v3.0.0 of the SDCP protocol, and the printer should be connected to your network. The printer does not need to be in the same subnet as your computer, but you need to know it's IP address.

| :warning: | This integration is still a WIP. Your mileage may vary. |
|---|:--|

## Installation

1. Use [HACS](https://hacs.xyz/docs/setup/download), in `HACS` search for "Chitubox Printer". After adding `https://gitlab.com/bushvin/hass_chitubox_printer` as a custom repository.
2. Restart Home Assistant
3. Add the integration: in the Home Assitant UI go to "Settings" -> "Devices & Services" then click "+ ADD INTEGRATION" and search for "Chitubox Printer"
4. Enter the chose name for your printer and its IP Address or hostname

## Contributions are welcome

TBD

---

[ko-fi]: https://ko-fi.com/bushvin
[ko-fi-badge]: https://img.shields.io/badge/Ko--fi-FF5E5B?logo=ko-fi&logoColor=white
[hacs]: https://github.com/hacs/integration
[hacs-badge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge