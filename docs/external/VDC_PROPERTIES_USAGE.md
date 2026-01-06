# vDC Property Classes - Usage Guide

This guide explains how to use the `vdc_properties.py` Python module to create and manage virtual digitalSTROM devices (vdSD).

## Overview

The `vdc_properties.py` module provides Python classes that represent all vDC device properties as defined in the vDC-API-properties specification (July 2022). These classes allow you to:

- Create virtual digitalSTROM devices with proper type safety
- Build complex device configurations programmatically
- Manage device states and properties
- Serialize devices to JSON format for the vDC API

## Quick Start

### Basic Example: Creating a Simple Light Switch

```python
from vdc_properties import *

# 1. Create device properties
device_props = DeviceProperties(
    primary_group=1,  # Light group
    zone_id=0,
    model_features={"dimmable": True},
    configurations=["default"],
)

# 2. Create the virtual device
device = VirtualDevice(
    ds_uid="0123456789ABCDEF0123456789ABCDEF01",
    properties=device_props,
)

# 3. Add a dimmer output
dimmer = create_dimmer_output(name="Main Light", default_group=1, max_power=60.0)
device.output = dimmer

# 4. Add a brightness channel
brightness = create_brightness_channel(ds_index=0, initial_value=0.0)
device.add_channel(brightness)

# 5. Convert to dictionary for JSON serialization
device_dict = device.to_dict()
```

## Core Concepts

### Device Structure

A `VirtualDevice` consists of several components:

1. **General Properties**: Basic device information (group, zone, features)
2. **Inputs**: Buttons, binary inputs, and sensors
3. **Outputs**: Output functionality and channels
4. **Scenes**: Scene configurations
5. **Actions**: Device actions and capabilities
6. **States & Properties**: Device states and custom properties

### Class Hierarchy

```
VirtualDevice
├── DeviceProperties (general properties)
├── ButtonInput[] (button inputs)
│   ├── ButtonInputDescription
│   ├── ButtonInputSettings
│   └── ButtonInputState
├── BinaryInput[] (binary inputs)
│   ├── BinaryInputDescription
│   ├── BinaryInputSettings
│   └── BinaryInputState
├── SensorInput[] (sensor inputs)
│   ├── SensorInputDescription
│   ├── SensorInputSettings
│   └── SensorInputState
├── Output (single output)
│   ├── OutputDescription
│   ├── OutputSettings
│   └── OutputState
├── Channel[] (output channels)
│   ├── ChannelDescription
│   └── ChannelState
└── Scene[] (scenes)
```

## Examples

### Example 1: Temperature Sensor Device

```python
from vdc_properties import *

# Create device properties
props = DeviceProperties(
    primary_group=2,  # Climate group
    zone_id=1,
    model_features={"temperature_sensor": True},
    configurations=["default"],
)

# Create virtual device
device = VirtualDevice(
    ds_uid="TEMP00000000000000000000000000000001",
    properties=props,
)

# Add temperature sensor
temp_sensor = create_temperature_sensor(
    name="Living Room Temperature",
    ds_index=0,
    group=2,
    min_temp=-20.0,
    max_temp=60.0,
    resolution=0.1,
)
device.add_sensor_input(temp_sensor)

# Update sensor value
device.sensor_inputs[0].state.value = 21.5  # 21.5°C
device.sensor_inputs[0].state.age = 0.0
```

### Example 2: Two-Way Pushbutton (Rocker Switch)

```python
from vdc_properties import *

# Create device
props = DeviceProperties(
    primary_group=0,  # Generic
    zone_id=1,
    model_features={"two_way_button": True},
    configurations=["default"],
)

device = VirtualDevice(
    ds_uid="BTN2W000000000000000000000000000001",
    properties=props,
)

# Create DOWN button (index 0)
btn_down = ButtonInput(
    description=ButtonInputDescription(
        name="Button Down",
        ds_index=0,
        supports_local_key_mode=True,
        button_type=ButtonType.TWO_WAY_PUSHBUTTON,
        button_element_id=ButtonElementID.DOWN,
        button_id=0,
    ),
    settings=ButtonInputSettings(
        group=1,
        function=0,
        mode=ButtonMode.BUTTON1_DOWN,  # Mode 6
        channel=0,
    ),
)

# Create UP button (index 1)
btn_up = ButtonInput(
    description=ButtonInputDescription(
        name="Button Up",
        ds_index=1,
        supports_local_key_mode=True,
        button_type=ButtonType.TWO_WAY_PUSHBUTTON,
        button_element_id=ButtonElementID.UP,
        button_id=0,
    ),
    settings=ButtonInputSettings(
        group=1,
        function=0,
        mode=ButtonMode.BUTTON1_UP,  # Mode 9
        channel=0,
    ),
)

device.add_button_input(btn_down)
device.add_button_input(btn_up)
```

### Example 3: RGB Color Light

```python
from vdc_properties import *

# Create device
props = DeviceProperties(
    primary_group=1,  # Light
    zone_id=1,
    model_features={"dimmable": True, "color": True},
    configurations=["default"],
)

device = VirtualDevice(
    ds_uid="RGBL0000000000000000000000000000001",
    properties=props,
)

# Create full color dimmer output
output = Output(
    description=OutputDescription(
        default_group=1,
        name="RGB Light",
        function=OutputFunction.FULL_COLOR_DIMMER,
        output_usage=OutputUsage.ROOM,
        variable_ramp=True,
        max_power=12.0,  # 12W LED
    ),
    settings=OutputSettings(
        active_group=1,
        groups={1: True},
        mode=OutputMode.GRADUAL,
        push_changes=True,
    ),
)
device.output = output

# Add channels: brightness, hue, saturation
channels = [
    Channel(
        description=ChannelDescription(
            name="Brightness",
            channel_type=1,
            ds_index=0,
            min=0.0,
            max=100.0,
            resolution=0.1,
        ),
        state=ChannelState(value=0.0),
    ),
    Channel(
        description=ChannelDescription(
            name="Hue",
            channel_type=2,
            ds_index=1,
            min=0.0,
            max=360.0,
            resolution=1.0,
        ),
        state=ChannelState(value=0.0),
    ),
    Channel(
        description=ChannelDescription(
            name="Saturation",
            channel_type=3,
            ds_index=2,
            min=0.0,
            max=100.0,
            resolution=0.1,
        ),
        state=ChannelState(value=0.0),
    ),
]

for channel in channels:
    device.add_channel(channel)

# Add a colorful scene
scene = Scene(
    scene_number=1,
    channels={
        1: SceneValue(value=75.0, dont_care=False),  # Brightness
        2: SceneValue(value=120.0, dont_care=False),  # Hue (green)
        3: SceneValue(value=100.0, dont_care=False),  # Saturation
    },
    effect=SceneEffect.SMOOTH_NORMAL,
)
device.add_scene(scene)
```

### Example 4: Binary Input (Window Contact Sensor)

```python
from vdc_properties import *

# Create device
props = DeviceProperties(
    primary_group=0,  # Generic
    zone_id=1,
    model_features={"window_contact": True},
    configurations=["default"],
)

device = VirtualDevice(
    ds_uid="WNDW0000000000000000000000000000001",
    properties=props,
)

# Create window contact binary input
window_contact = BinaryInput(
    description=BinaryInputDescription(
        name="Window Contact",
        ds_index=0,
        input_type=InputType.DETECTS_CHANGES,
        input_usage=InputUsage.ROOM_CLIMATE,
        sensor_function=BinarySensorFunction.WINDOW_CONTACT,
        update_interval=1.0,
    ),
    settings=BinaryInputSettings(
        group=2,  # Climate group
        sensor_function=BinarySensorFunction.WINDOW_CONTACT,
    ),
    state=BinaryInputState(
        value=False,  # Window closed
        age=0.0,
        error=ErrorCode.OK,
    ),
)

device.add_binary_input(window_contact)

# Simulate window opening
device.binary_inputs[0].state.value = True
device.binary_inputs[0].state.age = 0.0
```

### Example 5: Heating Valve with Temperature Sensor

```python
from vdc_properties import *

# Create device
props = DeviceProperties(
    primary_group=2,  # Climate
    zone_id=1,
    model_features={"heating": True, "temperature_sensor": True},
    configurations=["default"],
)

device = VirtualDevice(
    ds_uid="HEAT0000000000000000000000000000001",
    properties=props,
)

# Add temperature sensor
temp_sensor = create_temperature_sensor(
    name="Room Temperature",
    ds_index=0,
    group=2,
    min_temp=0.0,
    max_temp=40.0,
)
device.add_sensor_input(temp_sensor)

# Create heating valve output
heating_output = Output(
    description=OutputDescription(
        default_group=2,
        name="Heating Valve",
        function=OutputFunction.INTERNALLY_CONTROLLED,
        output_usage=OutputUsage.ROOM,
        variable_ramp=True,
    ),
    settings=OutputSettings(
        active_group=2,
        groups={2: True},
        mode=OutputMode.GRADUAL,
        push_changes=True,
        heating_system_capability=HeatingSystemCapability.HEATING_ONLY,
        heating_system_type=HeatingSystemType.RADIATOR,
    ),
)
device.output = heating_output

# Add valve position channel
valve_channel = Channel(
    description=ChannelDescription(
        name="Valve Position",
        channel_type=1,
        ds_index=0,
        min=0.0,
        max=100.0,
        resolution=1.0,
    ),
    state=ChannelState(value=0.0),
)
device.add_channel(valve_channel)
```

## Working with Device States

### Updating Button States

```python
# Simulate button press
button = device.get_button_input(0)
button.state.value = True
button.state.click_type = ClickType.CLICK_1X
button.state.age = 0.0
button.state.error = ErrorCode.OK
```

### Updating Sensor Values

```python
# Update temperature sensor
sensor = device.get_sensor_input(0)
sensor.state.value = 22.3  # 22.3°C
sensor.state.age = 0.0
sensor.state.error = ErrorCode.OK
```

### Updating Channel Values

```python
# Set brightness to 75%
channel = device.get_channel(0)
channel.state.value = 75.0
channel.state.age = None  # Not yet applied to hardware
```

## Enumerations Reference

### Common Enumerations

- **ButtonType**: UNDEFINED, SINGLE_PUSHBUTTON, TWO_WAY_PUSHBUTTON, etc.
- **ClickType**: TIP_1X, CLICK_1X, HOLD_START, etc.
- **SensorType**: TEMPERATURE, HUMIDITY, ILLUMINATION, CO2_CONCENTRATION, etc.
- **OutputFunction**: ON_OFF_ONLY, DIMMER, POSITIONAL, FULL_COLOR_DIMMER, etc.
- **ErrorCode**: OK, OPEN_CIRCUIT, SHORT_CIRCUIT, BUS_CONNECTION_PROBLEM, etc.

See the module source code for complete enumeration values.

## Helper Functions

The module provides helper functions for common device types:

- `create_temperature_sensor()`: Create a temperature sensor
- `create_pushbutton()`: Create a simple pushbutton
- `create_dimmer_output()`: Create a dimmer output
- `create_brightness_channel()`: Create a brightness channel

## Serialization

Convert a device to a dictionary (JSON-compatible):

```python
device_dict = device.to_dict()

# Can be serialized to JSON
import json
json_str = json.dumps(device_dict, indent=2)
```

## Best Practices

1. **Use Type Safety**: The classes use Python type hints and dataclasses for validation
2. **Initialize States**: Always initialize state objects, even if values are unknown (use None)
3. **Index Consistency**: Ensure ds_index values are consistent and sequential (0, 1, 2, ...)
4. **Group Assignment**: Use appropriate dS group numbers for device functionality
5. **Scene Numbers**: Use standard dS scene numbers (0-127)
6. **dSUID Format**: Use proper dSUID format (34 hex characters)

## Common Patterns

### Adding Multiple Sensors

```python
sensors = [
    create_temperature_sensor("Temperature", 0, 2),
    SensorInput(
        description=SensorInputDescription(
            name="Humidity",
            ds_index=1,
            sensor_type=SensorType.HUMIDITY,
            sensor_usage=SensorUsage.ROOM,
            min=0.0,
            max=100.0,
            resolution=0.1,
            update_interval=60.0,
            alive_sign_interval=300.0,
        ),
        settings=SensorInputSettings(group=2),
    ),
]

for sensor in sensors:
    device.add_sensor_input(sensor)
```

### Creating Scene Table

```python
# Standard light scenes
scenes = [
    Scene(5, {1: SceneValue(0.0)}, SceneEffect.SMOOTH_NORMAL),  # Deep Off
    Scene(0, {1: SceneValue(0.0)}, SceneEffect.NO_EFFECT),  # Off
    Scene(1, {1: SceneValue(75.0)}, SceneEffect.SMOOTH_NORMAL),  # Preset 1
    Scene(2, {1: SceneValue(50.0)}, SceneEffect.SMOOTH_NORMAL),  # Preset 2
    Scene(3, {1: SceneValue(25.0)}, SceneEffect.SMOOTH_NORMAL),  # Preset 3
    Scene(4, {1: SceneValue(10.0)}, SceneEffect.SMOOTH_NORMAL),  # Preset 4
]

for scene in scenes:
    device.add_scene(scene)
```

## Integration with Home Assistant

This module can be used to create virtual devices for Home Assistant integration:

```python
# Create a device that represents a Home Assistant entity
def create_ha_light_device(entity_id: str, name: str, brightness: float = 0.0):
    props = DeviceProperties(
        primary_group=1,
        zone_id=0,
        model_features={"dimmable": True, "ha_entity": True},
        configurations=["default"],
    )
    
    device = VirtualDevice(
        ds_uid=generate_dsuid_from_entity_id(entity_id),
        properties=props,
    )
    
    # Add output and channel
    device.output = create_dimmer_output(name=name, default_group=1)
    device.add_channel(create_brightness_channel(initial_value=brightness))
    
    return device

def generate_dsuid_from_entity_id(entity_id: str) -> str:
    """Generate a deterministic dSUID from Home Assistant entity ID"""
    import hashlib
    hash_bytes = hashlib.sha256(entity_id.encode()).digest()
    return hash_bytes[:17].hex().upper() + "01"
```

## Error Handling

```python
try:
    # Create button with invalid configuration
    button = ButtonInput(
        description="invalid",  # Wrong type
        settings=ButtonInputSettings(group=1, function=0, mode=ButtonMode.STANDARD, channel=0),
    )
except TypeError as e:
    print(f"Type error: {e}")

# Validate indices
if 0 <= index < len(device.button_inputs):
    button = device.get_button_input(index)
else:
    print(f"Invalid button index: {index}")
```

## Further Reading

- vDC-API-properties_JULY 2022.pdf: Complete specification
- vDC-API.pdf: API methods and protocols
- vDC-overview.pdf: System overview and concepts
- vDC-property-subtrees-list.md: Comprehensive property reference

## License

This module is part of the virtual_digitalSTROM_devices_4_HA project.
