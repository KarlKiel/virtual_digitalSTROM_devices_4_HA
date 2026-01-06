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
- **Automatic state persistence and restoration across restarts**
  - Critical device states (heating/cooling levels, channel values, sensor readings) are saved to YAML
  - States automatically restored on Home Assistant startup
  - See [STATE_RESTORATION.md](custom_components/virtual_digitalstrom_devices/STATE_RESTORATION.md) for details
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
├── device_storage.py        # YAML-based device persistence
├── virtual_device.py        # Virtual device data model
├── state_restorer.py        # State restoration on startup
├── state_listener.py        # State tracking from HA entities
├── state_listener_manager.py # State listener coordination
├── property_updater.py      # Property update and persistence
├── device_listener_configurator.py # Auto-configure listeners
├── DEVICE_CLASSES.md        # Device classes documentation
├── DEVICE_STORAGE.md        # Device persistence documentation
├── STATE_RESTORATION.md     # State restoration documentation
├── STATE_LISTENER_SYSTEM.md # State listener documentation
├── PROPERTY_UPDATE_SYSTEM.md # Property update documentation
├── example_*.py             # Example scripts
├── manifest.json            # Integration metadata
├── strings.json             # UI strings
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
