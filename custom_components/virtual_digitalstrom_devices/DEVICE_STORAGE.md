# Device Persistence Layer

This module provides YAML-based persistence for virtual digitalSTROM devices.

## Overview

The persistence layer consists of two main components:

1. **VirtualDevice**: Represents a configured device instance
2. **DeviceStorage**: Manages reading/writing devices to YAML storage

## VirtualDevice

The `VirtualDevice` class represents a single virtual digitalSTROM device with the following attributes:

- `device_id`: Unique identifier (auto-generated UUID)
- `name`: Human-readable device name
- `group_id`: digitalSTROM group ID (device class)
- `ha_entity_id`: Home Assistant entity ID
- `dsid`: digitalSTROM device ID (auto-generated UUID)
- `zone_id`: Zone/room ID
- `attributes`: Additional device-specific attributes (dict)

### Example

```python
from virtual_device import VirtualDevice
from device_classes import DSGroupID

# Create a light device
light = VirtualDevice(
    name="Living Room Light",
    group_id=DSGroupID.LIGHTS,
    ha_entity_id="light.living_room",
    zone_id=1,
    attributes={"brightness": 255}
)
```

## DeviceStorage

The `DeviceStorage` class provides methods to persist devices to a YAML file:

### Methods

- `add_device(device)`: Add a new device
- `update_device(device_id, **kwargs)`: Update device attributes
- `delete_device(device_id)`: Remove a device
- `get_device(device_id)`: Get a specific device
- `get_all_devices()`: Get all devices
- `get_devices_by_group(group_id)`: Get devices by group
- `device_exists(device_id)`: Check if device exists

### Example

```python
from pathlib import Path
from device_storage import DeviceStorage

# Initialize storage
storage = DeviceStorage(Path("devices.yaml"))

# Add a device
storage.add_device(light)

# Update a device
storage.update_device(light.device_id, name="Main Light")

# Get all devices
devices = storage.get_all_devices()

# Delete a device
storage.delete_device(light.device_id)
```

## YAML Format

Devices are stored in the following YAML format:

```yaml
devices:
- device_id: 550e8400-e29b-41d4-a716-446655440000
  name: Living Room Light
  group_id: 1
  ha_entity_id: light.living_room
  dsid: 6ba7b810-9dad-11d1-80b4-00c04fd430c8
  zone_id: 1
  attributes:
    brightness: 255
    color_temp: 4000
```

## Integration with Home Assistant

The storage is automatically initialized when the integration is set up. The YAML file is stored in the Home Assistant configuration directory as `virtual_digitalstrom_devices.yaml`.

Access the storage from the integration:

```python
storage = hass.data[DOMAIN][entry.entry_id]["device_storage"]
```

## Running Examples

See `example_device_storage.py` for a complete working example:

```bash
python3 example_device_storage.py
```
