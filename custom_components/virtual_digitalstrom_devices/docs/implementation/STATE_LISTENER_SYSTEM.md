# State Listener System Documentation

## Overview

The State Listener System provides a comprehensive framework for tracking changes to STATE-classified properties by monitoring Home Assistant entities. This enables virtual digitalSTROM devices to synchronize with real Home Assistant entities in real-time.

## Architecture

### Core Components

1. **StateListener (Base Class)**
   - Abstract base class for all state listeners
   - Handles HA entity tracking via `async_track_state_change_event`
   - Provides callback mechanism for state updates
   - Manages start/stop lifecycle

2. **Specialized Listeners**
   - `BooleanStateListener` - For boolean values (button.value, binary.value, output.localPriority)
   - `NumericStateListener` - For float values (sensor.value, channel.value, control levels)
   - `IntegerStateListener` - For integer values (actionId, contextId, extendedValue)
   - `StringStateListener` - For string values (contextMsg, connection_status, device states)
   - `EnumStateListener` - For enum values (error codes, actionMode)
   - `AttributeStateListener` - For values in entity attributes

3. **StateListenerManager**
   - Centralized management of all listeners
   - YAML-based mapping configuration
   - Global state update callbacks
   - Device-level listener grouping
   - Statistics and monitoring

4. **StateUpdate**
   - Immutable event object representing a state change
   - Contains: property_type, device_id, entity_id, old_value, new_value, timestamp, index

## STATE Properties Coverage

Based on `COMPLETE_PROPERTY_CLASSIFICATION.md`, the system tracks all 45 STATE properties:

### Button Input States (Section 4.2.3)
- `button.value` - Current button state (boolean)
- `button.error` - Error code (enum 0-6)
- `button.actionId` - Scene call alternative (integer)
- `button.actionMode` - Action mode (enum 0-2)

### Binary Input States (Section 4.3.3)
- `binary.value` - Current binary state (boolean)
- `binary.extendedValue` - Extended value (integer)
- `binary.error` - Error code (enum 0-6)

### Sensor Input States (Section 4.4.3)
- `sensor.value` - Current sensor reading (float) - **persist for slow sensors**
- `sensor.contextId` - Context identifier (integer)
- `sensor.contextMsg` - Context message (string)
- `sensor.error` - Error code (enum 0-6)

### Dynamic Actions (Section 4.6.1)
- `dynamicAction.name` - Dynamic action name (string)
- `dynamicAction.title` - Display title (string)

### Device States (Section 4.7.1)
- `deviceState.name` - State name (string)
- `deviceState.value` - State value (string)

### Device Properties (Section 4.7.2)
- `deviceProperty.name` - Property name (string)
- `deviceProperty.value` - Property value (any)

### Output States (Section 4.8.3)
- `output.localPriority` - Local priority active (boolean)
- `output.error` - Error code (enum 0-6)

### Channel States (Section 4.9.3)
- `channel.value` - Current channel value 0-100% (float) - **persist**

### Control Values (Section 4.11)
- `control.heatingLevel` - Heating level (float) - **persist for connection loss**
- `control.coolingLevel` - Cooling level (float) - **persist for connection loss**
- `control.ventilationLevel` - Ventilation level (float) - **persist for connection loss**

### System States (General)
- `device.progMode` - Programming mode (boolean)
- `device.connection_status` - Connection status (string)
- `device.system_status` - System status (string)

## Usage Examples

### Basic Usage - Single Listener

```python
from homeassistant.core import HomeAssistant
from custom_components.virtual_digitalstrom_devices.state_listener import (
    create_sensor_value_listener,
    StateUpdate,
)

# Create a listener for a temperature sensor
listener = create_sensor_value_listener(
    hass=hass,
    device_id="my_virtual_device_id",
    entity_id="sensor.living_room_temperature",
    sensor_index=0,
)

# Add a callback to handle updates
def handle_temperature_update(update: StateUpdate):
    print(f"Temperature changed: {update.old_value}°C -> {update.new_value}°C")
    # Persist the value, update vDC API, etc.

listener.add_callback(handle_temperature_update)

# Start listening
await listener.async_start()

# Later, stop listening
await listener.async_stop()
```

### Using the Manager

```python
from pathlib import Path
from custom_components.virtual_digitalstrom_devices.state_listener_manager import (
    StateListenerManager,
)
from custom_components.virtual_digitalstrom_devices.state_listener import (
    NumericStateListener,
    BooleanStateListener,
    StatePropertyType,
    StateUpdate,
)

# Initialize manager with mapping file
manager = StateListenerManager(
    hass=hass,
    mapping_file=Path(hass.config.path("virtual_digitalstrom_listener_mappings.yaml")),
)

# Add a global callback for all state updates (e.g., for persistence)
def persist_state_update(update: StateUpdate):
    print(f"Persisting state update: {update}")
    # Save to state.yaml file

manager.add_state_update_callback(persist_state_update)

# Add listeners programmatically
await manager.async_add_listener(
    device_id="living_room_light",
    entity_id="light.living_room",
    property_type=StatePropertyType.CHANNEL_VALUE,
    listener_class=NumericStateListener,
    index=0,  # Channel index
    auto_start=True,
)

await manager.async_add_listener(
    device_id="bedroom_blind",
    entity_id="cover.bedroom_blinds",
    property_type=StatePropertyType.CHANNEL_VALUE,
    listener_class=NumericStateListener,
    index=0,
    auto_start=True,
)

# Save mappings to YAML for persistence
await manager.async_save_mappings()

# Later, load mappings on startup
await manager.async_load_mappings()

# Get statistics
stats = manager.get_statistics()
print(f"Total listeners: {stats['total_listeners']}")
print(f"By type: {stats['listeners_by_type']}")
```

### Mapping Configuration File

The manager can load/save listener mappings from YAML:

```yaml
# virtual_digitalstrom_listener_mappings.yaml
listener_mappings:
  - device_id: living_room_light
    property_type: channel.value
    entity_id: light.living_room
    listener_class: NumericStateListener
    index: 0
    enabled: true

  - device_id: living_room_light
    property_type: sensor.value
    entity_id: sensor.living_room_temperature
    listener_class: NumericStateListener
    index: 0
    enabled: true

  - device_id: heating_radiator
    property_type: control.heatingLevel
    entity_id: climate.living_room
    listener_class: NumericStateListener
    enabled: true
    
  - device_id: main_door_switch
    property_type: button.value
    entity_id: binary_sensor.door_button
    listener_class: BooleanStateListener
    index: 0
    enabled: true

  - device_id: motion_sensor_01
    property_type: binary.value
    entity_id: binary_sensor.motion_living_room
    listener_class: BooleanStateListener
    index: 0
    enabled: true
```

### Integration with Home Assistant

```python
# In __init__.py
from .state_listener_manager import StateListenerManager
from .const import DOMAIN, STATE_LISTENER_MAPPINGS_FILE

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Virtual digitalSTROM Devices from a config entry."""
    
    # Initialize state listener manager
    mapping_file = Path(hass.config.path(STATE_LISTENER_MAPPINGS_FILE))
    state_listener_manager = StateListenerManager(hass, mapping_file)
    
    # Add global callback for state persistence
    def persist_state(update: StateUpdate):
        # Save to state storage
        state_storage = hass.data[DOMAIN][entry.entry_id]["state_storage"]
        state_storage.update_state(
            device_id=update.device_id,
            property_type=update.property_type.value,
            value=update.new_value,
            timestamp=update.timestamp,
            index=update.index,
        )
    
    state_listener_manager.add_state_update_callback(persist_state)
    
    # Load existing mappings
    await state_listener_manager.async_load_mappings()
    
    # Store in hass.data
    hass.data[DOMAIN][entry.entry_id]["state_listener_manager"] = state_listener_manager
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    
    # Stop all listeners
    manager = hass.data[DOMAIN][entry.entry_id]["state_listener_manager"]
    await manager.async_stop_all()
    
    # Save mappings
    await manager.async_save_mappings()
    
    return True
```

## UI Mapping (Future Implementation)

The system is designed to support UI-based configuration where users can:

1. Select a virtual device
2. Choose a STATE property (e.g., "sensor.value[0]")
3. Browse available HA entities
4. Map the HA entity to the STATE property
5. Enable/disable the mapping

Example UI workflow:
```
Device: Living Room Light (device_id: living_room_light_01)
├─ Channel[0].value → light.living_room (brightness)
├─ Sensor[0].value → sensor.power_consumption
└─ Output.localPriority → input_boolean.manual_mode

Device: Heating Radiator (device_id: radiator_bedroom)
└─ Control.heatingLevel → climate.bedroom (target_temperature)
```

## Persistence Strategy

State values should be persisted based on use case:

### Always Persist
- Sensor values (especially slow update cycles)
- Channel values (for immediate display after restart)
- Control values (critical for device operation during DSS connection loss)
- Connection/system status

### May Not Persist
- Transient button clicks
- Temporary events
- Calculated values that can be regenerated

## Performance Considerations

1. **Event Filtering**: Listeners only notify callbacks when values actually change
2. **Async Operations**: All start/stop operations are async to avoid blocking
3. **Error Handling**: Callbacks are wrapped in try/except to prevent one failure from affecting others
4. **Selective Subscription**: Only creates HA state subscriptions for mapped entities

## Error Handling

The system provides comprehensive error handling:

- Invalid entity IDs: Logged as warnings, listener remains inactive
- Callback errors: Logged but don't affect other callbacks
- YAML loading errors: Logged, system continues with empty mappings
- Type conversion errors: Return None, logged at debug level

## Testing

```python
# Example test for state listener
async def test_sensor_value_listener(hass):
    """Test sensor value listener tracks changes."""
    
    # Create listener
    listener = create_sensor_value_listener(
        hass=hass,
        device_id="test_device",
        entity_id="sensor.test_temp",
        sensor_index=0,
    )
    
    # Track updates
    updates = []
    listener.add_callback(lambda u: updates.append(u))
    
    # Start listener
    await listener.async_start()
    
    # Trigger state change
    hass.states.async_set("sensor.test_temp", "23.5")
    await hass.async_block_till_done()
    
    # Verify
    assert len(updates) == 1
    assert updates[0].new_value == 23.5
    assert updates[0].property_type == StatePropertyType.SENSOR_VALUE
    
    # Cleanup
    await listener.async_stop()
```

## Future Enhancements

1. **Bidirectional Sync**: Support updating HA entities from vDC state changes
2. **Value Transformations**: Support custom transform functions (e.g., unit conversions)
3. **Conditional Mapping**: Enable/disable listeners based on conditions
4. **Rate Limiting**: Throttle rapid state changes
5. **Historical Data**: Track state change history
6. **UI Configuration**: Web-based mapping configuration panel
