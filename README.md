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
4. Follow the configuration steps to set up the vDC hub
5. Once set up, click **Configure** on the integration to add virtual devices

The integration creates a vDC (Virtual Device Connector) hub, and all virtual devices are registered as child devices of this hub.

## Features

- **User-friendly device creation** via configuration UI with category selection
- Create virtual digitalSTROM devices based on Home Assistant entities
- Manage digitalSTROM vDSDs
- Integration with Home Assistant's configuration UI
- **Automatic state persistence and restoration across restarts**
  - Critical device states (heating/cooling levels, channel values, sensor readings) are saved to YAML
  - States automatically restored on Home Assistant startup
  - See [STATE_RESTORATION.md](custom_components/virtual_digitalstrom_devices/docs/implementation/STATE_RESTORATION.md) for details
- Full support for all digitalSTROM device classes (12 standard classes)
  - Yellow (Lights), Gray (Blinds), Blue (Climate), Cyan (Audio), Magenta (Video)
  - Black (Joker - Configurable), and more
- See [DEVICE_CLASSES.md](custom_components/virtual_digitalstrom_devices/docs/implementation/DEVICE_CLASSES.md) for complete device class documentation

## Storage Locations

The integration stores its configuration data within the integration folder:

```
custom_components/virtual_digitalstrom_devices/
├── virtual_digitalstrom_devices.yaml           # Device configurations
├── virtual_digitalstrom_listener_mappings.yaml # State listener mappings
└── virtual_digitalstrom_vdc_config.yaml        # vDC entity configuration
```

These files are automatically managed by the integration and persist across restarts.

**Note:** These YAML files are excluded from version control via `.gitignore` as they contain user-specific configuration data.

## Development

This integration is under active development. Contributions are welcome!

### Project Structure

```
custom_components/virtual_digitalstrom_devices/
├── __init__.py              # Integration setup and entry point
├── config_flow.py           # Configuration UI flow
├── const.py                 # Constants and configuration
├── manifest.json            # Integration metadata
├── strings.json             # UI strings
├── translations/            # Localized UI strings
│   └── en.json
├── api/                     # vDC Protocol Implementation
│   ├── message_builder.py
│   ├── message_handler.py
│   └── vdc_message_dispatcher.py
├── models/                  # Data Models
│   ├── device_classes.py
│   ├── virtual_device.py
│   └── dsuid_generator.py
├── storage/                 # Persistence Layer
│   ├── device_storage.py
│   ├── vdc_manager.py
│   ├── property_updater.py
│   └── state_restorer.py
├── listeners/               # State Tracking
│   ├── state_listener.py
│   ├── state_listener_manager.py
│   └── device_listener_configurator.py
└── docs/                    # Documentation
    ├── implementation/      # Technical documentation
    ├── examples/            # Example scripts
    └── STRUCTURE.md         # Detailed structure documentation
```

For a detailed explanation of the project structure, see [STRUCTURE.md](custom_components/virtual_digitalstrom_devices/docs/STRUCTURE.md).

### Device Classes

The integration supports all 12 standard digitalSTROM device classes organized by color groups:

- **Yellow (Lights)**: Room lights, garden lights, building illuminations
- **Gray (Blinds)**: Blinds, shades, awnings, curtains
- **Blue (Climate)**: Heating, cooling, ventilation, temperature control, windows
- **Cyan (Audio)**: Music, radio
- **Magenta (Video)**: TV, video
- **Black (Joker)**: Configurable devices
- Additional groups for Security (Red), Access (Green), and Single Devices (White)

For detailed information about device classes, see [DEVICE_CLASSES.md](custom_components/virtual_digitalstrom_devices/docs/implementation/DEVICE_CLASSES.md).

### Documentation

All documentation is organized in the `docs/` directory:

- **Implementation docs**: `docs/implementation/` - Technical documentation
- **Examples**: `docs/examples/` - Example scripts
- **External references**: `/docs/external/` - digitalSTROM specifications and API docs

See [docs/README.md](custom_components/virtual_digitalstrom_devices/docs/README.md) for a complete documentation index.

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/KarlKiel/virtual_digitalSTROM_devices_4_HA).

## License

See the LICENSE file for details.
