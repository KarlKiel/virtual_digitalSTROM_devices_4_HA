# Virtual digitalSTROM Devices Integration Structure

This document describes the organization and structure of the Virtual digitalSTROM Devices Home Assistant integration.

## Directory Structure

```
custom_components/virtual_digitalstrom_devices/
├── __init__.py                 # Integration setup and entry point
├── const.py                    # Constants and configuration
├── manifest.json               # Integration metadata
│
├── api/                        # vDC Protocol Implementation
│   ├── __init__.py
│   ├── message_builder.py      # Build outgoing protobuf messages
│   ├── message_handler.py      # Handle incoming protobuf messages
│   ├── vdc_message_dispatcher.py  # Message routing and dispatching
│   ├── genericVDC.proto        # Protocol buffer definition
│   └── genericVDC_pb2.py       # Generated protobuf code
│
├── models/                     # Data Models
│   ├── __init__.py
│   ├── device_classes.py       # digitalSTROM device classifications
│   ├── virtual_device.py       # Virtual device data model
│   └── dsuid_generator.py      # DSUID generation utilities
│
├── storage/                    # Persistence Layer
│   ├── __init__.py
│   ├── device_storage.py       # YAML-based device storage
│   ├── vdc_manager.py          # vDC entity management
│   ├── property_updater.py     # Property update and persistence
│   └── state_restorer.py       # State restoration on startup
│
├── listeners/                  # State Tracking
│   ├── __init__.py
│   ├── state_listener.py       # Base state listener classes
│   ├── state_listener_manager.py  # Listener lifecycle management
│   └── device_listener_configurator.py  # Auto-configure listeners
│
└── docs/                       # Documentation
    ├── implementation/         # Implementation documentation
    │   ├── DEVICE_CLASSES.md
    │   ├── DEVICE_STORAGE.md
    │   ├── STATE_RESTORATION.md
    │   ├── STATE_LISTENER_SYSTEM.md
    │   ├── PROPERTY_UPDATE_SYSTEM.md
    │   ├── VDC_ENTITY.md
    │   ├── VDC_MESSAGE_HANDLING.md
    │   ├── IMPLEMENTATION_SUMMARY.md
    │   └── ...
    ├── examples/               # Example scripts
    │   ├── example_device_classes.py
    │   ├── example_device_storage.py
    │   ├── example_message_handling.py
    │   ├── example_property_updates.py
    │   ├── example_state_listeners.py
    │   └── example_state_restoration.py
    └── api/                    # API documentation (future)

docs/external/                  # External Documentation (outside integration)
├── ds-basics.pdf              # digitalSTROM basics
├── vDC-API.pdf                # vDC API specification
├── vDC-overview.pdf           # vDC overview
└── ...                        # Other reference materials
```

## Package Organization

### Core Files

- **`__init__.py`**: Integration setup, loads all components
- **`const.py`**: Constants, domain name, storage paths
- **`manifest.json`**: Integration metadata for Home Assistant

### API Package (`api/`)

Implements the vDC (Virtual Device Connector) protocol for communication with digitalSTROM servers:

- **Message Building**: Create protobuf messages for responses and notifications
- **Message Handling**: Process incoming messages from digitalSTROM
- **Dispatching**: Route messages to appropriate handlers
- **Protocol Definitions**: Protobuf definitions and generated code

### Models Package (`models/`)

Data models and classification systems:

- **Device Classes**: digitalSTROM color groups and device types
- **Virtual Devices**: Core device data structure
- **DSUID Generation**: Unique identifier generation for devices

### Storage Package (`storage/`)

Persistence and data management:

- **Device Storage**: YAML-based persistence for device configurations
- **vDC Manager**: Manages the vDC entity metadata
- **Property Updater**: Handles property updates and persistence
- **State Restorer**: Restores device states on startup

### Listeners Package (`listeners/`)

State tracking and synchronization with Home Assistant:

- **State Listeners**: Monitor HA entity state changes
- **Listener Manager**: Lifecycle management for listeners
- **Auto-Configurator**: Automatically set up listeners for devices

### Documentation (`docs/`)

- **implementation/**: Technical documentation about the implementation
- **examples/**: Example scripts demonstrating usage
- **api/**: API documentation (future)

## Data Storage Locations

The integration stores its configuration data within the integration folder itself:

```
/config/custom_components/virtual_digitalstrom_devices/
├── __init__.py                                     # Integration code
├── ... (other integration files)
│
├── virtual_digitalstrom_devices.yaml               # Device configurations
├── virtual_digitalstrom_listener_mappings.yaml     # State listener mappings
└── virtual_digitalstrom_vdc_config.yaml            # vDC entity configuration
```

**Important**: Storage files are located within the integration directory using `Path(__file__).parent` to ensure they're co-located with the integration code. These YAML files are excluded from version control via `.gitignore`.

## Import Structure

The package uses absolute imports from the integration root:

```python
# From integration __init__.py
from .storage import DeviceStorage, VdcManager
from .listeners import StateListenerManager
from .models.device_classes import DSColor

# From storage/property_updater.py
from .device_storage import DeviceStorage
from ..listeners.state_listener import StatePropertyType
from ..models.virtual_device import VirtualDevice
```

## Key Design Principles

1. **Separation of Concerns**: Each package has a clear, focused responsibility
2. **No Storage in Integration Folder**: All YAML data files are in `/config/`
3. **Standard HA Structure**: Follows Home Assistant integration conventions
4. **Documentation Separation**: Implementation docs in integration, reference docs outside
5. **Clear Package Boundaries**: Well-defined interfaces between packages

## Migration Notes

This structure was created to:
- Comply with Home Assistant integration best practices
- Improve code organization and maintainability
- Separate concerns for better testability
- Make the codebase easier to navigate and understand

All file references and imports have been updated to work with the new structure.
