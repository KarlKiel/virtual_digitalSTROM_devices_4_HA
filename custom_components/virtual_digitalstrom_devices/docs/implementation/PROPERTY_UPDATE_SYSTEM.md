# Property Update System Documentation

Complete documentation for updating CONFIG and STATE properties in virtual digitalSTROM devices.

## Overview

The property update system provides methods to update all properties with:
- **CONFIG updates**: Always persisted to YAML storage
- **STATE updates**: Pushed to mapped Home Assistant entities + selective persistence

Based on `COMPLETE_PROPERTY_CLASSIFICATION.md`:
- **81 CONFIG properties** (56%) - Always persisted
- **45 STATE properties** (31%) - Selectively persisted, pushed to HA entities
- **22 META properties** (15%) - Auto-calculated, not directly updatable

## Architecture

### Components

1. **PropertyUpdater**: Unified interface for all property updates
2. **ConfigPropertyUpdater**: Handles CONFIG property updates with automatic persistence
3. **StatePropertyUpdater**: Handles STATE property updates with HA entity pushing

### Property Flow

```
CONFIG Property Update:
User/UI → PropertyUpdater → ConfigPropertyUpdater → VirtualDevice → DeviceStorage (YAML)

STATE Property Update:
User/HA Entity → PropertyUpdater → StatePropertyUpdater → HA Entity (push) + VirtualDevice (persist) → DeviceStorage (YAML)
```

## CONFIG Property Updates

CONFIG properties describe the device and are **always persisted** to YAML.

### Examples of CONFIG Properties

- Device identity: `name`, `zone_id`, `group_id`, `model`, `model_version`
- Output settings: `outputSettings.mode`, `outputSettings.dimTimeUp`, `outputSettings.dimTimeDown`
- Input settings: `buttonInputSettings[i].group`, `sensorInputSettings[i].updateInterval`
- Channel descriptions: `channelDescriptions[i].name`, `channelDescriptions[i].channelType`
- Scene configurations: `scenes[i].sceneNo`, `scenes[i].sceneValues`

### Usage

```python
from .property_updater import PropertyUpdater

# Initialize
updater = PropertyUpdater(hass, device_storage)

# Update simple property
await updater.update_property(
    device_id="living_room_light",
    property_type="name",
    value="Living Room Main Light",
)

# Update nested property
await updater.config_updater.update_config_property(
    device_id="living_room_light",
    property_path="attributes.num_channels",
    value=4,
)

# Update indexed property (e.g., button settings)
await updater.config_updater.update_config_property(
    device_id="button_panel",
    property_path="buttonInputSettings[0].group",
    value=1,  # Yellow group (lights)
    index=0,
)

# Batch update
config_updates = {
    "name": "Bedroom Light",
    "zone_id": 3,
    "model_version": "2.0.0",
}
await updater.config_updater.update_multiple_config_properties(
    device_id="bedroom_light",
    updates=config_updates,
)
```

### Persistence

All CONFIG property changes are **immediately persisted** to YAML:
- Single updates trigger one file write
- Batch updates trigger one file write for all changes
- YAML file: `custom_components/virtual_digitalstrom_devices/virtual_digitalstrom_devices.yaml`

## STATE Property Updates

STATE properties are runtime values that:
1. **Push to mapped Home Assistant entities** (for OUTPUT/CONTROL properties only)
2. **Selectively persist** based on property type and use case
3. **Read-only INPUT properties** (sensor values, binary input values) are persisted but NOT pushed to HA

### Property Direction

**OUTPUT/CONTROL Properties** (Pushed to HA + Persisted):
- `channel[i].value` - Push to light/cover entities + persist for immediate display
- `control.heatingLevel` - Push to climate entities + MUST persist for DSS outage
- `control.coolingLevel` - Push to climate entities + MUST persist
- `control.ventilationLevel` - Push to climate entities + MUST persist
- `output.localPriority` - Push to relevant entities
- `connection_status`, `system_status` - Push to status entities

**INPUT Properties** (Persisted ONLY, NOT pushed):
- `sensor[i].value` - Read from sensor entities, persist to avoid waiting after restart
- `binary[i].value` - Read from binary_sensor entities, persist last known state
- `binary[i].extendedValue` - Read from entities, persist only
- `sensor[i].contextId`, `sensor[i].contextMsg` - Read from entities, persist only
- `button[i].value` - Read from button entities (transient, not persisted by default)

### Examples of STATE Properties

**Always Persisted (Critical OUTPUT/CONTROL):**
- `control.heatingLevel` - MUST persist for heating radiator during DSS outage
- `control.coolingLevel` - MUST persist for climate control
- `control.ventilationLevel` - MUST persist for fan control

**Recommended Persisted (INPUT - Read-Only):**
- `sensor[i].value` - Persist to avoid waiting for slow sensors after restart (NOT pushed to HA)
- `binary[i].value` - Persist last known state (NOT pushed to HA)

**Recommended Persisted (OUTPUT):**
- `channel[i].value` - Persist for immediate display after restart (pushed to HA)
- `connection_status`, `system_status` - Persist system state (pushed to HA)

**Not Persisted (Transient):**
- `button[i].value` - Transient button press events (read from HA, not pushed back)
- `button[i].actionId` - Transient action events

### Usage

```python
from .state_listener import StatePropertyType

# Update channel value (brightness) - OUTPUT property
# Pushes to light.living_room entity AND persists locally
await updater.update_property(
    device_id="living_room_light",
    property_type=StatePropertyType.CHANNEL_VALUE.value,
    value=75.0,  # 75% brightness
    index=0,
)

# Update sensor value (temperature) - INPUT property (READ-ONLY)
# Does NOT push to sensor.temperature (read-only input from sensor)
# Only persists locally to avoid waiting for slow sensors
await updater.update_property(
    device_id="temp_sensor",
    property_type=StatePropertyType.SENSOR_VALUE.value,
    value=23.5,  # 23.5°C
    index=0,
    persist_state=True,  # Force persistence
)

# Update button value (transient event) - INPUT property
# Does NOT push to binary_sensor.button (read-only input from button)
# Does NOT persist (transient event)
await updater.update_property(
    device_id="button_panel",
    property_type=StatePropertyType.BUTTON_VALUE.value,
    value=True,  # Button pressed
    index=0,
    persist_state=False,  # Don't persist
)

# Update critical control value
# Pushes to climate.radiator entity AND auto-persists (critical!)
await updater.update_property(
    device_id="bedroom_radiator",
    property_type=StatePropertyType.CONTROL_HEATING_LEVEL.value,
    value=21.5,  # 21.5°C target
    # persist_state=True automatic for control values
)
```

### Multi-Instance Properties

Many STATE properties have multiple instances (buttons, sensors, channels):

```python
# RGB+W light with 4 channels
channel_values = [100.0, 255.0, 128.0, 64.0]  # Brightness, R, G, B
for i, value in enumerate(channel_values):
    await updater.update_property(
        device_id="rgb_light",
        property_type=StatePropertyType.CHANNEL_VALUE.value,
        value=value,
        index=i,  # Channel index
    )

# 8-button control panel
for button_idx in range(8):
    await updater.update_property(
        device_id="button_panel",
        property_type=StatePropertyType.BUTTON_VALUE.value,
        value=False,  # All buttons released
        index=button_idx,
    )
```

### Batch STATE Updates

For efficiency, update multiple STATE properties at once:

```python
# Update all RGB channels at once
state_updates = {
    (StatePropertyType.CHANNEL_VALUE, 0): 100.0,  # Brightness
    (StatePropertyType.CHANNEL_VALUE, 1): 255.0,  # Red
    (StatePropertyType.CHANNEL_VALUE, 2): 0.0,    # Green
    (StatePropertyType.CHANNEL_VALUE, 3): 0.0,    # Blue
}
await updater.state_updater.update_multiple_state_properties(
    device_id="rgb_light",
    updates=state_updates,
    persist=True,
)
```

### Entity Mapping

STATE values are pushed to Home Assistant entities based on `entity_mappings` in device attributes:

```python
device.attributes = {
    "entity_mappings": {
        "channel[0].value": "light.living_room",
        "channel[1].value": "light.living_room@red",
        "channel[2].value": "light.living_room@green",
        "sensor[0].value": "sensor.temperature",
        "button[0].value": "binary_sensor.button_0",
    }
}
```

Format: `"property[index].subproperty": "entity_id"` or `"entity_id@attribute"`

### Supported Entity Types

**Lights** (`light.*`):
- `channel.value` → `brightness` (0-100% → 0-255)
- `binary.value` → `on/off`

**Covers** (`cover.*`):
- `channel.value` → `position` (if default) or `tilt`

**Climate** (`climate.*`):
- `control.heatingLevel` → `temperature`
- `control.coolingLevel` → `temperature`
- `control.ventilationLevel` → `fan_mode` (mapped)

**Switches** (`switch.*`):
- `binary.value` → `on/off`

**Input Helpers**:
- `input_number` → `set_value`
- `input_boolean` → `turn_on/turn_off`
- `input_text` → `set_value`

### Persistence Strategy

| Property Type | Auto-Persist | Push to HA | Reason |
|--------------|--------------|------------|---------|
| **CONFIG Properties** | ✅ Always | ❌ No | Device description must never be lost |
| `control.heatingLevel` | ✅ Always | ✅ Yes | CRITICAL: Radiator must work during DSS outage |
| `control.coolingLevel` | ✅ Always | ✅ Yes | CRITICAL: Climate control continuity |
| `control.ventilationLevel` | ✅ Always | ✅ Yes | CRITICAL: Fan control continuity |
| `channel[i].value` | ✅ Yes | ✅ Yes | Immediate display after restart, push to lights/covers |
| `sensor[i].value` | ✅ Yes | ❌ No | INPUT: Read from sensor entities, avoid waiting after restart |
| `binary[i].value` | ✅ Yes | ❌ No | INPUT: Read from binary_sensor entities, show last state |
| `connection_status` | ✅ Yes | ✅ Yes | System status visibility |
| `button[i].value` | ❌ No | ❌ No | INPUT: Transient event from button |
| `button[i].actionId` | ❌ No | ❌ No | INPUT: Transient event |

## Integration Usage

### Initialization

In `__init__.py`:

```python
from .property_updater import PropertyUpdater

async def async_setup_entry(hass, entry):
    # ... existing setup ...
    
    # Initialize property updater
    property_updater = PropertyUpdater(hass, device_storage)
    hass.data[DOMAIN][entry.entry_id]["property_updater"] = property_updater
```

### Access in Services

```python
async def handle_update_property(call):
    """Handle update_property service call."""
    property_updater = hass.data[DOMAIN][entry_id]["property_updater"]
    
    await property_updater.update_property(
        device_id=call.data.get("device_id"),
        property_type=call.data.get("property_type"),
        value=call.data.get("value"),
        index=call.data.get("index"),
        persist_state=call.data.get("persist_state"),
    )
```

### Access from Listeners

State listeners can trigger updates when HA entities change:

```python
async def on_state_change(state_update: StateUpdate):
    """Called when HA entity state changes."""
    property_updater = hass.data[DOMAIN][entry_id]["property_updater"]
    
    # Update the STATE property (this will also persist if needed)
    await property_updater.state_updater.update_state_property(
        device_id=state_update.device_id,
        property_type=state_update.property_type,
        value=state_update.new_value,
        index=state_update.index,
    )
```

## Error Handling

### PropertyUpdateError

Raised when update fails:

```python
from .property_updater import PropertyUpdateError

try:
    await updater.update_property(
        device_id="non_existent",
        property_type="name",
        value="Test",
    )
except PropertyUpdateError as e:
    _LOGGER.error(f"Update failed: {e}")
```

### Common Errors

- `Device {id} not found`: Device ID doesn't exist
- `Failed to push value to entity`: HA entity doesn't exist or service call failed
- `Invalid property path`: Property path syntax error
- `Permission denied writing YAML`: File system permission issue

## Performance Considerations

### Batch Updates

Use batch updates when updating multiple properties:

```python
# Good: Single transaction, one file write
await updater.config_updater.update_multiple_config_properties(
    device_id=device_id,
    updates={"name": "New Name", "zone_id": 5},
)

# Avoid: Multiple transactions, multiple file writes
await updater.update_property(device_id, "name", "New Name")
await updater.update_property(device_id, "zone_id", 5)
```

### STATE Persistence

Control which STATE properties persist:

```python
# Default: Auto-decide based on property type
await updater.update_property(device_id, prop, value)

# Force persist (expensive - use sparingly)
await updater.update_property(device_id, prop, value, persist_state=True)

# Force no persist (for high-frequency updates)
await updater.update_property(device_id, prop, value, persist_state=False)
```

## Examples

See `example_property_updates.py` for comprehensive examples including:
1. Basic CONFIG property updates
2. Basic STATE property updates
3. Critical control values (heating radiator)
4. Batch updates
5. Indexed CONFIG properties
6. Multi-instance STATE updates
7. Connection status updates
8. Error handling
9. Complete workflow (create → configure → update)

## Summary

- **CONFIG properties**: Always persisted, describe the device
- **STATE properties**: Pushed to HA entities, selectively persisted
- **Critical properties**: Control values MUST persist for device functionality
- **Batch updates**: Use for efficiency
- **Multi-instance**: Support unlimited buttons/sensors/channels
- **Error handling**: PropertyUpdateError for all failures
- **Integration**: Auto-initialized in `async_setup_entry()`
