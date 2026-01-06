# State Restoration System

## Overview

The State Restoration System ensures that virtual digitalSTROM devices maintain their state across Home Assistant restarts by reading persisted STATE property values from YAML storage and restoring them during integration startup.

## Architecture

### Core Components

1. **StateRestorer** (`state_restorer.py`)
   - Reads persisted state_values from device attributes
   - Parses state keys to extract property types and indices
   - Optionally pushes restored values to Home Assistant entities
   - Provides statistics on restoration process

2. **Integration Startup Flow** (`__init__.py`)
   - Device storage loads devices from YAML (including state_values)
   - State restoration reads and restores state_values
   - State listener manager loads listener mappings
   - State listeners begin tracking new changes

3. **State Persistence** (`property_updater.py`)
   - StatePropertyUpdater stores STATE values in `device.attributes['state_values']`
   - DeviceStorage saves the entire device structure to YAML
   - State values include timestamp metadata

## State Restoration Flow

```
Startup Sequence:
┌─────────────────────────────────────────────────────────────┐
│ 1. DeviceStorage loads devices from YAML                    │
│    - Devices loaded with all attributes                     │
│    - state_values preserved in device.attributes            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. StateRestorer restores persisted state values           │
│    - Reads state_values from each device                    │
│    - Parses property types (e.g., "channel.value[0]")      │
│    - Optionally pushes to HA entities                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. StateListenerManager loads listener mappings            │
│    - Creates listeners for mapped properties                │
│    - Starts tracking state changes                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Normal Operation                                         │
│    - Listeners track HA entity changes                      │
│    - PropertyUpdater persists critical STATE values         │
└─────────────────────────────────────────────────────────────┘
```

## Persisted State Format

### YAML Structure

```yaml
devices:
  - device_id: 550e8400-e29b-41d4-a716-446655440000
    name: Living Room Light
    group_id: 1
    ha_entity_id: light.living_room
    attributes:
      state_values:
        # Channel value (indexed property)
        channel.value[0]:
          value: 75.5
          timestamp: '2024-01-06T12:00:00'
        
        # Sensor value (indexed property)
        sensor.value[0]:
          value: 42.3
          timestamp: '2024-01-06T12:00:00'
        
        # Control value (non-indexed property)
        control.heatingLevel:
          value: 21.5
          timestamp: '2024-01-06T11:30:00'
        
        # Connection status (non-indexed property)
        device.connection_status:
          value: connected
          timestamp: '2024-01-06T12:00:00'
```

### State Key Format

State keys follow the pattern: `property.type[index]` or `property.type`

Examples:
- `channel.value[0]` - Channel 0 value
- `channel.value[1]` - Channel 1 value
- `sensor.value[0]` - Sensor 0 value
- `control.heatingLevel` - Heating level (no index)
- `device.connection_status` - Connection status (no index)

## Which States Are Persisted?

The StatePropertyUpdater in `property_updater.py` determines which STATE properties are persisted based on:

### Critical Persistent Properties (MUST persist)
- `control.heatingLevel` - Required for operation during DSS connection loss
- `control.coolingLevel` - Required for operation during DSS connection loss
- `control.ventilationLevel` - Required for operation during DSS connection loss

### Recommended Persistent Properties (SHOULD persist)
- `sensor.value` - Avoids waiting for sensor updates after restart
- `channel.value` - Enables immediate state display after restart
- `binary.value` - Binary input states
- `connection_status` - Device connection state
- `system_status` - System state

### Non-Persisted Properties (transient)
- `button.value` - Transient button clicks
- `button.actionId` - Temporary action triggers
- `button.actionMode` - Temporary action modes

## Usage

### Automatic Restoration (Default)

State restoration is automatic during integration startup. No manual intervention required.

```python
# In __init__.py (already implemented)
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # ... device storage initialization ...
    
    # Restore persisted state values from YAML storage
    restore_stats = await restore_states_on_startup(
        hass=hass,
        device_storage=device_storage,
        property_updater=property_updater,
        push_to_entities=False,  # Don't push to entities on startup
    )
```

### Manual Restoration

For advanced use cases, you can manually trigger state restoration:

```python
from custom_components.virtual_digitalstrom_devices.state_restorer import StateRestorer

# Create restorer
restorer = StateRestorer(hass, device_storage, property_updater)

# Restore all devices
stats = await restorer.async_restore_all_devices(push_to_entities=False)

print(f"Restored {stats['total_properties_restored']} properties")
print(f"Across {stats['devices_with_state']} devices")

# Restore a single device
device = device_storage.get_device("device_id_here")
count = await restorer.async_restore_device_state(device, push_to_entities=False)
```

### Push to Entities Option

The `push_to_entities` parameter controls whether restored values are pushed to Home Assistant entities:

- `False` (default): Only restore internal state tracking
  - Faster startup
  - Avoids conflicts with HA entity states
  - Recommended for most use cases

- `True`: Push restored values to HA entities
  - Synchronizes HA entities with persisted values
  - May conflict with entity states if HA has different values
  - Use with caution

## Configuration

### Persistence Control

Control which properties are persisted by modifying `property_updater.py`:

```python
class StatePropertyUpdater:
    def __init__(self, hass, device_storage):
        # Properties that MUST be persisted
        self.critical_persistent_properties = {
            StatePropertyType.CONTROL_HEATING_LEVEL,
            StatePropertyType.CONTROL_COOLING_LEVEL,
            # Add more...
        }
        
        # Properties that SHOULD be persisted
        self.recommended_persistent_properties = {
            StatePropertyType.SENSOR_VALUE,
            StatePropertyType.CHANNEL_VALUE,
            # Add more...
        }
```

## Examples

See `example_state_restoration.py` for a complete demonstration of:
1. Creating devices with persisted STATE values
2. Saving devices to YAML storage
3. Loading devices from YAML (simulated restart)
4. Verifying STATE values were preserved

Run the example:
```bash
cd custom_components/virtual_digitalstrom_devices
python3 example_state_restoration.py
```

## Logging

The state restoration system provides comprehensive logging:

```
INFO: Restoring persisted state values from storage
INFO: Restored 5 state properties across 2 devices
DEBUG: Restoring channel.value[0] = 75.5 for device Living Room Light
DEBUG: Restoring control.heatingLevel = 21.5 for device Bedroom Radiator
```

## Error Handling

The system handles errors gracefully:

- **Missing state_values**: Silently skipped, no error
- **Invalid state keys**: Logged as warning, restoration continues
- **Unknown property types**: Logged as debug, restoration continues
- **Entity push failures**: Logged as warning, restoration continues
- **Device not found**: Logged as error, added to stats['errors']

## Performance

State restoration is designed for efficiency:

1. **Minimal overhead**: Only reads existing data from loaded devices
2. **No blocking**: All operations are async
3. **Selective restoration**: Only devices with state_values are processed
4. **Batch processing**: Restores all properties in a single pass

## Integration with Other Systems

### Property Updater
- `StatePropertyUpdater._store_state_value()` persists values
- `DeviceStorage.save_device()` saves to YAML
- Values automatically available for restoration

### State Listener Manager
- Restoration happens BEFORE listeners start
- Prevents duplicate state updates during startup
- Listeners track changes after restoration

### Device Storage
- Devices loaded with state_values intact
- No special handling needed
- Standard YAML serialization/deserialization

## Future Enhancements

Potential improvements:

1. **Selective Entity Push**: Push only to entities that don't have recent states
2. **State Validation**: Verify restored values are within valid ranges
3. **State Migration**: Handle schema changes in state_values format
4. **Compression**: Compress state_values for large installations
5. **State History**: Track state change history across restarts
6. **UI Configuration**: Allow users to control which properties are persisted

## Troubleshooting

### State values not being restored

1. Check that state_values exist in YAML:
   ```bash
   grep -A5 "state_values:" virtual_digitalstrom_devices.yaml
   ```

2. Check logs for restoration messages:
   ```
   grep "Restoring persisted state values" home-assistant.log
   ```

3. Verify property types are valid:
   ```python
   from state_listener import StatePropertyType
   StatePropertyType("channel.value")  # Should not raise error
   ```

### Restored values not matching expected

1. Check YAML for correct values:
   ```yaml
   state_values:
     channel.value[0]:
       value: 75.5  # Verify this is correct
   ```

2. Verify timestamp is recent:
   ```yaml
   timestamp: '2024-01-06T12:00:00'  # Check date
   ```

3. Check for override during startup:
   - HA entities may have different states
   - Listeners may update values immediately after restoration

## See Also

- [STATE_LISTENER_SYSTEM.md](STATE_LISTENER_SYSTEM.md) - State tracking and listeners
- [PROPERTY_UPDATE_SYSTEM.md](PROPERTY_UPDATE_SYSTEM.md) - Property updates and persistence
- [DEVICE_STORAGE.md](DEVICE_STORAGE.md) - Device YAML storage
- [COMPLETE_PROPERTY_CLASSIFICATION.md](COMPLETE_PROPERTY_CLASSIFICATION.md) - Property classifications
