# Virtual digitalSTROM Devices for Home Assistant

This repository contains a Home Assistant Integration that provides a vDC to create and manage Digitalstrom vDSDs based on Home Assistant Devices and Entities.

## Installation

### Manual Installation (via GitHub Web UI)

1. Download the repository as a ZIP file from GitHub
2. Extract the ZIP file
3. Copy the `custom_components/virtual_digitalstrom_devices` folder to your Home Assistant `config/custom_components/` directory
4. Restart Home Assistant

### HACS Installation (coming soon)

This integration will be available through HACS in the future.

## Configuration

1. In Home Assistant, go to **Settings** → **Devices & Services**
2. Click the **+ Add Integration** button
3. Search for "Virtual digitalSTROM Devices"
4. Follow the configuration steps

## Features

- Create virtual digitalSTROM devices based on Home Assistant entities
- Manage digitalSTROM vDSDs
- Integration with Home Assistant's configuration UI
- Full support for all digitalSTROM device classes (12 standard classes)
  - Yellow (Lights), Gray (Blinds), Blue (Climate), Cyan (Audio), Magenta (Video)
  - Black (Joker - Configurable), and more
- See [DEVICE_CLASSES.md](custom_components/virtual_digitalstrom_devices/DEVICE_CLASSES.md) for complete device class documentation

## Development

This integration is under active development. Contributions are welcome!

### Structure

```
custom_components/virtual_digitalstrom_devices/
├── __init__.py              # Integration setup and entry point
├── config_flow.py           # Configuration UI flow
├── const.py                 # Constants used throughout the integration
├── device_classes.py        # digitalSTROM device classes and color groups
├── DEVICE_CLASSES.md        # Device classes documentation
├── example_device_classes.py # Example usage of device classes
├── manifest.json            # Integration metadata
├── strings.json             # UI strings
├── ds-basics.pdf            # digitalSTROM specification reference
└── translations/
    └── en.json              # English translations
```

### Device Classes

The integration supports all 12 standard digitalSTROM device classes organized by color groups:

- **Yellow (Lights)**: Room lights, garden lights, building illuminations
- **Gray (Blinds)**: Blinds, shades, awnings, curtains
- **Blue (Climate)**: Heating, cooling, ventilation, temperature control, windows
- **Cyan (Audio)**: Music, radio
- **Magenta (Video)**: TV, video
- **Black (Joker)**: Configurable devices
- Additional groups for Security (Red), Access (Green), and Single Devices (White)

For detailed information about device classes, see [DEVICE_CLASSES.md](custom_components/virtual_digitalstrom_devices/DEVICE_CLASSES.md).

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/KarlKiel/virtual_digitalSTROM_devices_4_HA).

## License

See the LICENSE file for details.
