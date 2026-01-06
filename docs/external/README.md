# vDC Property Documentation - README

This directory contains comprehensive documentation and Python implementation for vDC (Virtual Device Connector) device properties based on the official vDC-API-properties specification (July 2022).

## 📁 Files in this Directory

### Documentation Files

1. **vDC-property-subtrees-list.md** 
   - Complete structured list of all device property subtrees from Chapter 4
   - All properties clearly marked as [REQUIRED] or [OPTIONAL]
   - Detailed descriptions, types, and ranges for every property
   - Organized by property category (Inputs, Outputs, Channels, Scenes, Actions, etc.)
   - **Use this for**: Complete reference documentation

2. **VDC_PROPERTY_TREE_REFERENCE.md**
   - Visual quick reference showing complete property hierarchy
   - Common enumerations (sensor types, scene numbers, error codes, etc.)
   - Python class to property tree mapping
   - Minimal usage example
   - **Use this for**: Quick lookups and cheat sheet

3. **VDC_PROPERTIES_USAGE.md**
   - Comprehensive usage guide for the Python module
   - Multiple working examples (temperature sensor, RGB light, heating valve, etc.)
   - Class hierarchy explanation
   - Best practices and common patterns
   - Integration guidance for Home Assistant
   - **Use this for**: Learning how to use the Python classes

### Source PDF Files

4. **vDC-overview.pdf**
   - Overview of the vDC concept
   - Device types and architecture
   - Discovery mechanism

5. **vDC-API.pdf**
   - Complete vDC API specification
   - Connection management
   - Methods and notifications
   - Device operations

6. **vDC-API-properties_JULY 2022.pdf**
   - Detailed property specifications (Chapter 4 is the main focus)
   - Property types and structures
   - Common properties for all entities

### Python Implementation

7. **vdc_properties.py**
   - Complete Python module with classes for all vDC properties
   - Enumerations for all property types
   - Dataclasses for structured data
   - VirtualDevice container class
   - Helper functions for common device types
   - JSON serialization support
   - Working examples in `__main__` section
   - **Use this for**: Creating virtual devices programmatically

## 🚀 Quick Start

### Reading the Documentation

Start here based on your needs:

```
Need to understand all properties?
  → Start with vDC-property-subtrees-list.md

Need a quick reference?
  → Use VDC_PROPERTY_TREE_REFERENCE.md

Want to write code?
  → Read VDC_PROPERTIES_USAGE.md
  → Use vdc_properties.py
```

### Using the Python Module

```python
from vdc_properties import *

# Create a simple light device
device = VirtualDevice(
    ds_uid="0123456789ABCDEF0123456789ABCDEF01",
    properties=DeviceProperties(
        primary_group=1,  # Light
        zone_id=0,
        model_features={"dimmable": True},
        configurations=["default"],
    ),
)

# Add output and channel
device.output = create_dimmer_output("Light", 1)
device.add_channel(create_brightness_channel(0, 0.0))

# Convert to JSON-compatible dictionary
data = device.to_dict()
```

See **VDC_PROPERTIES_USAGE.md** for complete examples.

## 📖 Understanding the vDC Concept

### What is vDC?

vDC (Virtual Device Connector) enables integration of IP-based devices into the digitalSTROM system. It allows non-digitalSTROM devices to appear and behave like native digitalSTROM devices.

### Key Concepts

- **vdSD (virtual digitalSTROM device)**: A virtual representation of a physical device
- **vDC (virtual device connector)**: The logical entity managing one or more device classes
- **vdSM (virtual digitalSTROM meter)**: The connection point to the digitalSTROM system
- **Properties**: Named values describing device characteristics and state
- **Channels**: Individual controllable outputs (e.g., brightness, hue, position)
- **Scenes**: Predefined device states that can be recalled

### Device Structure

Every vdSD consists of:
- **General Properties**: Basic device info (group, zone, features)
- **Inputs**: Buttons, binary inputs, sensors
- **Output**: Single output with multiple channels
- **Scenes**: Scene configurations
- **Actions**: Device capabilities and operations

## 🎯 Common Use Cases

### 1. Creating a Temperature Sensor
```python
sensor = create_temperature_sensor("Room Temp", 0, 2)
device.add_sensor_input(sensor)
```

### 2. Creating a Pushbutton
```python
button = create_pushbutton("Light Switch", 0, 1)
device.add_button_input(button)
```

### 3. Creating an RGB Light
```python
device.output = create_dimmer_output("RGB Light", 1)
device.add_channel(create_brightness_channel(0))
# Add hue and saturation channels...
```

See **VDC_PROPERTIES_USAGE.md** for complete examples.

## 📊 Property Categories

The vDC specification defines properties in these categories:

1. **General Device Properties** (Section 4.1.1)
   - primaryGroup, zoneID, modelFeatures, etc.

2. **Button Inputs** (Section 4.2)
   - Descriptions, Settings, States

3. **Binary Inputs** (Section 4.3)
   - Descriptions, Settings, States

4. **Sensor Inputs** (Section 4.4)
   - Descriptions, Settings, States (temperature, humidity, etc.)

5. **Device Actions** (Section 4.5)
   - Action descriptions and parameters

6. **Device States & Properties** (Section 4.6)
   - Custom states and properties

7. **Device Events** (Section 4.7)
   - Event descriptions

8. **Output** (Section 4.8)
   - Description, Settings, State

9. **Channels** (Section 4.9)
   - Channel descriptions and states

10. **Scenes** (Section 4.10)
    - Scene configurations with channel values

11. **Control Values** (Section 4.11)
    - Write-only control values (e.g., heatingLevel)

## 🔧 Python Module Features

### Type Safety
- Uses Python dataclasses with type hints
- Enumerations for all property types
- Runtime type validation

### Completeness
- Covers all properties from the specification
- Includes all enumerations and constants
- Implements all required and optional fields

### Ease of Use
- Helper functions for common device types
- Clear class hierarchy
- Comprehensive documentation strings
- Working examples included

### Integration Ready
- JSON serialization via `to_dict()`
- Compatible with vDC API format
- Suitable for Home Assistant integration

## 📚 Reference Tables

### Common Sensor Types
- 1: Temperature (°C)
- 2: Humidity (%)
- 3: Illumination (lux)
- 14: Active Power (W)
- 22: CO2 (ppm)

### Common dS Groups
- 0: Generic (Black)
- 1: Light (Yellow)
- 2: Climate (Blue)
- 5: Security (Red)

### Standard Scene Numbers
- 0: Off
- 1-4: Preset 1-4
- 5: Deep Off
- 69: Panic

See **VDC_PROPERTY_TREE_REFERENCE.md** for complete tables.

## ✅ Validation & Testing

The Python module has been:
- ✅ Tested with working examples
- ✅ Code reviewed
- ✅ Validated against specification
- ✅ Type-checked with mypy-compatible hints

## 🤝 Contributing

When working with these files:
1. Keep documentation synchronized with code
2. Test all Python changes with the example code
3. Update examples when adding new features
4. Maintain consistency with the vDC specification

## 📄 License

This documentation and code is part of the virtual_digitalSTROM_devices_4_HA project.

## 🔗 Related Resources

- vDC Specification Documents (in this directory)
- digitalSTROM Developer Documentation
- Home Assistant Integration

---

**Last Updated**: January 2026
**Specification Version**: vDC-API-properties July 2022
**Python Module Version**: 1.0
