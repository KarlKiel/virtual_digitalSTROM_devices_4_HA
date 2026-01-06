"""Example demonstrating the state listener system with real-world scenarios."""

from pathlib import Path
from datetime import datetime

# This example demonstrates how to use the state listener system
# Run with: python3 example_state_listeners.py

from state_listener import (
    create_button_value_listener,
    create_sensor_value_listener,
    create_channel_value_listener,
    create_control_value_listener,
    create_connection_status_listener,
    StatePropertyType,
    StateUpdate,
)
from state_listener_manager import StateListenerManager


def example_basic_listener():
    """Example 1: Basic single listener for a sensor."""
    print("=" * 60)
    print("Example 1: Basic Sensor Value Listener")
    print("=" * 60)
    
    # Simulated Home Assistant instance (in real use, this would be hass)
    class MockHass:
        def __init__(self):
            self.states = MockStates()
    
    class MockStates:
        def get(self, entity_id):
            return None
    
    hass = MockHass()
    
    # Create a listener for a temperature sensor
    listener = create_sensor_value_listener(
        hass=hass,
        device_id="bedroom_climate_device",
        entity_id="sensor.bedroom_temperature",
        sensor_index=0,
    )
    
    # Add callback to handle updates
    def handle_temperature_update(update: StateUpdate):
        print(f"  Temperature update detected:")
        print(f"    Device: {update.device_id}")
        print(f"    Property: {update.property_type.value}")
        print(f"    Old value: {update.old_value}°C")
        print(f"    New value: {update.new_value}°C")
        print(f"    Timestamp: {update.timestamp}")
        print(f"  → Persisting to state storage...")
    
    listener.add_callback(handle_temperature_update)
    
    print(f"✓ Created listener for sensor.bedroom_temperature")
    print(f"  Tracking: {StatePropertyType.SENSOR_VALUE.value}")
    print(f"  Device: bedroom_climate_device")
    print()


def example_multiple_listeners():
    """Example 2: Multiple listeners for a dimmable light device."""
    print("=" * 60)
    print("Example 2: Dimmable Light with Multiple Listeners")
    print("=" * 60)
    
    class MockHass:
        def __init__(self):
            self.states = MockStates()
    
    class MockStates:
        def get(self, entity_id):
            return None
    
    hass = MockHass()
    device_id = "living_room_dimmable_light"
    
    # This device has multiple STATE properties to track
    listeners = []
    
    # 1. Channel value (brightness)
    brightness_listener = create_channel_value_listener(
        hass=hass,
        device_id=device_id,
        entity_id="light.living_room",
        channel_index=0,
    )
    listeners.append(("Brightness", brightness_listener))
    
    # 2. Power consumption sensor
    power_listener = create_sensor_value_listener(
        hass=hass,
        device_id=device_id,
        entity_id="sensor.living_room_light_power",
        sensor_index=0,
    )
    listeners.append(("Power", power_listener))
    
    # 3. Connection status
    conn_listener = create_connection_status_listener(
        hass=hass,
        device_id=device_id,
        entity_id="binary_sensor.living_room_light_connectivity",
    )
    listeners.append(("Connection", conn_listener))
    
    print(f"Device: {device_id}")
    print(f"Created {len(listeners)} listeners:")
    for name, listener in listeners:
        print(f"  • {name}: {listener.property_type.value} ← {listener.entity_id}")
    print()


def example_heating_radiator():
    """Example 3: Heating radiator with control value persistence."""
    print("=" * 60)
    print("Example 3: Heating Radiator (Critical Persistence)")
    print("=" * 60)
    
    class MockHass:
        def __init__(self):
            self.states = MockStates()
    
    class MockStates:
        def get(self, entity_id):
            return None
    
    hass = MockHass()
    device_id = "bedroom_radiator"
    
    # Control value listener for heating level
    # This MUST be persisted to handle DSS connection loss
    heating_listener = create_control_value_listener(
        hass=hass,
        device_id=device_id,
        entity_id="climate.bedroom",
        control_type="heating",
    )
    
    def handle_heating_level_change(update: StateUpdate):
        print(f"  ⚠️  CRITICAL: Heating level changed!")
        print(f"    Old target: {update.old_value}°C")
        print(f"    New target: {update.new_value}°C")
        print(f"  → MUST persist to state.yaml")
        print(f"  → Reason: If DSS connection breaks, radiator needs this value")
    
    heating_listener.add_callback(handle_heating_level_change)
    
    print(f"Device: {device_id}")
    print(f"Property: {StatePropertyType.CONTROL_HEATING_LEVEL.value}")
    print(f"Entity: climate.bedroom")
    print(f"Persistence: CRITICAL (for connection loss recovery)")
    print()


def example_manager_usage():
    """Example 4: Using StateListenerManager for centralized management."""
    print("=" * 60)
    print("Example 4: StateListenerManager with Multiple Devices")
    print("=" * 60)
    
    class MockHass:
        def __init__(self):
            self.states = MockStates()
            self.config = MockConfig()
    
    class MockStates:
        def get(self, entity_id):
            return None
    
    class MockConfig:
        def path(self, filename):
            return f"/config/{filename}"
    
    hass = MockHass()
    
    # Initialize manager
    manager = StateListenerManager(
        hass=hass,
        mapping_file=Path("/config/virtual_digitalstrom_listener_mappings.yaml"),
    )
    
    # Add global callback for all state updates
    update_count = {"count": 0}
    
    def persist_all_states(update: StateUpdate):
        update_count["count"] += 1
        print(f"  [{update_count['count']}] State update: {update.device_id} → {update.property_type.value}")
        print(f"      Value: {update.old_value} → {update.new_value}")
        # In real implementation: save to state.yaml
    
    manager.add_state_update_callback(persist_all_states)
    
    print("✓ Manager initialized")
    print("✓ Global persistence callback registered")
    print()
    
    # Simulate adding listeners that would be created from device configuration
    print("Simulating device setup with automatic listener creation:")
    print()
    
    # Device 1: Dimmable light
    print("  Device: living_room_light")
    print("    - Has channel[0] → create channel.value listener")
    print("    - Has sensor[0] → create sensor.value listener")
    print()
    
    # Device 2: Heating radiator
    print("  Device: bedroom_radiator")
    print("    - Has control.heatingLevel → create control listener")
    print("    - Has sensor[0] (temp) → create sensor.value listener")
    print()
    
    # Device 3: Blind/shade
    print("  Device: kitchen_blind")
    print("    - Has channel[0] (position) → create channel.value listener")
    print("    - Has channel[1] (tilt) → create channel.value listener")
    print()
    
    # Get statistics
    stats = {
        "total_listeners": 6,
        "total_mappings": 6,
        "listeners_by_type": {
            "channel.value": 3,
            "sensor.value": 2,
            "control.heatingLevel": 1,
        },
        "listeners_by_device": {
            "living_room_light": 2,
            "bedroom_radiator": 2,
            "kitchen_blind": 2,
        },
    }
    
    print("Manager Statistics:")
    print(f"  Total listeners: {stats['total_listeners']}")
    print(f"  By type:")
    for prop_type, count in stats['listeners_by_type'].items():
        print(f"    - {prop_type}: {count}")
    print(f"  By device:")
    for device, count in stats['listeners_by_device'].items():
        print(f"    - {device}: {count}")
    print()


def example_yaml_mapping():
    """Example 5: YAML mapping file structure."""
    print("=" * 60)
    print("Example 5: YAML Mapping File")
    print("=" * 60)
    
    yaml_content = """# virtual_digitalstrom_listener_mappings.yaml
# Auto-generated listener mappings for STATE property tracking

listener_mappings:
  # Living Room Dimmable Light
  - device_id: living_room_light
    property_type: channel.value
    entity_id: light.living_room
    listener_class: NumericStateListener
    index: 0
    enabled: true

  - device_id: living_room_light
    property_type: sensor.value
    entity_id: sensor.living_room_light_power
    listener_class: NumericStateListener
    index: 0
    enabled: true

  # Bedroom Radiator (with critical control value)
  - device_id: bedroom_radiator
    property_type: control.heatingLevel
    entity_id: climate.bedroom
    listener_class: NumericStateListener
    enabled: true
    # Note: This MUST be persisted for DSS connection loss recovery

  - device_id: bedroom_radiator
    property_type: sensor.value
    entity_id: sensor.bedroom_temperature
    listener_class: NumericStateListener
    index: 0
    enabled: true

  # Kitchen Blind
  - device_id: kitchen_blind
    property_type: channel.value
    entity_id: cover.kitchen_blind
    listener_class: NumericStateListener
    index: 0  # Position channel
    enabled: true

  - device_id: kitchen_blind
    property_type: channel.value
    entity_id: cover.kitchen_blind
    listener_class: NumericStateListener
    index: 1  # Tilt channel
    attribute_name: current_tilt_position
    enabled: true

  # Main Door Button
  - device_id: main_door_button
    property_type: button.value
    entity_id: binary_sensor.door_button
    listener_class: BooleanStateListener
    index: 0
    enabled: true

  # Motion Sensor
  - device_id: motion_sensor_hallway
    property_type: binary.value
    entity_id: binary_sensor.hallway_motion
    listener_class: BooleanStateListener
    index: 0
    enabled: true
"""
    
    print(yaml_content)
    print("✓ This file is auto-generated when devices are configured")
    print("✓ Can be manually edited to enable/disable mappings")
    print("✓ Loaded automatically on integration startup")
    print()


def example_multiple_instances():
    """Example 7: Device with multiple instances of same property type."""
    print("=" * 60)
    print("Example 7: Complex Device with Multiple Instances")
    print("=" * 60)
    
    print("""
Scenario: RGB+W Dimmable Light with 3 buttons and power sensor
─────────────────────────────────────────────────────────────
Device Properties:
  • 4 channels: brightness, red, green, blue
  • 3 buttons: on/off, scene1, scene2
  • 1 sensor: power consumption
  • Connection status tracking

Required STATE Listeners:
─────────────────────────────────────────────────────────────
Property Path              Entity ID                   Type
─────────────────────────────────────────────────────────────
channel[0].value     →    light.rgb_light            Numeric
channel[1].value     →    light.rgb_light@red        Attribute
channel[2].value     →    light.rgb_light@green      Attribute
channel[3].value     →    light.rgb_light@blue       Attribute
button[0].value      →    binary_sensor.light_btn0   Boolean
button[1].value      →    binary_sensor.light_btn1   Boolean
button[2].value      →    binary_sensor.light_btn2   Boolean
sensor[0].value      →    sensor.rgb_light_power     Numeric
device.connection    →    binary_sensor.rgb_light    String
─────────────────────────────────────────────────────────────
Total: 9 listeners for 1 device
""")
    
    print("Entity Mappings Configuration:")
    mappings = {
        "channel[0].value": "light.rgb_light",
        "channel[1].value": "light.rgb_light@rgb_color[0]",
        "channel[2].value": "light.rgb_light@rgb_color[1]",
        "channel[3].value": "light.rgb_light@rgb_color[2]",
        "button[0].value": "binary_sensor.light_button_0",
        "button[1].value": "binary_sensor.light_button_1",
        "button[2].value": "binary_sensor.light_button_2",
        "sensor[0].value": "sensor.rgb_light_power",
        "device.connection_status": "binary_sensor.rgb_light_connectivity",
    }
    
    for prop_path, entity_id in mappings.items():
        print(f"  {prop_path:25} → {entity_id}")
    
    print()
    print("✓ All 9 STATE properties will be tracked independently")
    print("✓ Each property gets its own listener instance")
    print("✓ Index parameter ensures correct mapping")
    print()


def example_blind_with_tilt():
    """Example 8: Motorized blind with position and tilt."""
    print("=" * 60)
    print("Example 8: Motorized Blind with Position and Tilt")
    print("=" * 60)
    
    print("""
Scenario: Motorized blind with independent position and tilt control
─────────────────────────────────────────────────────────────
Device Properties:
  • 2 channels: position (up/down), tilt angle
  • 2 buttons: up button, down button
  • 1 binary input: obstruction sensor

Required STATE Listeners:
─────────────────────────────────────────────────────────────
Property Path              Entity ID                   Type
─────────────────────────────────────────────────────────────
channel[0].value     →    cover.bedroom_blind        Numeric
channel[1].value     →    cover.bedroom_blind@tilt   Attribute
button[0].value      →    binary_sensor.blind_up     Boolean
button[1].value      →    binary_sensor.blind_down   Boolean
binary[0].value      →    binary_sensor.obstruction  Boolean
─────────────────────────────────────────────────────────────
Total: 5 listeners for 1 device
""")
    
    print("✓ Two separate channel listeners track position and tilt independently")
    print("✓ Each button has its own listener (button[0] and button[1])")
    print("✓ Binary input listener tracks obstruction detection")
    print()


def example_climate_controller():
    """Example 9: Multi-zone climate controller."""
    print("=" * 60)
    print("Example 9: Multi-Zone Climate Controller")
    print("=" * 60)
    
    print("""
Scenario: Climate controller managing 3 zones with temperature sensors
─────────────────────────────────────────────────────────────
Device Properties:
  • 3 control values: zone1, zone2, zone3 heating levels
  • 3 sensors: zone1, zone2, zone3 temperature sensors
  • 3 channels: zone1, zone2, zone3 valve positions

Required STATE Listeners (CRITICAL - Must Persist):
─────────────────────────────────────────────────────────────
Property Path              Entity ID                   Type
─────────────────────────────────────────────────────────────
control.heatingLevel →    climate.zone1              Numeric
sensor[0].value      →    sensor.zone1_temperature   Numeric
channel[0].value     →    sensor.zone1_valve_pos     Numeric

control.coolingLevel →    climate.zone2              Numeric
sensor[1].value      →    sensor.zone2_temperature   Numeric
channel[1].value     →    sensor.zone2_valve_pos     Numeric

control.ventilationL →    climate.zone3              Numeric
sensor[2].value      →    sensor.zone3_temperature   Numeric
channel[2].value     →    sensor.zone3_valve_pos     Numeric
─────────────────────────────────────────────────────────────
Total: 9 listeners for 1 device
""")
    
    print("⚠️  CRITICAL: All control values MUST be persisted!")
    print("   Reason: If DSS connection breaks, each zone needs its target")
    print()
    print("✓ Each zone is independently tracked with 3 properties")
    print("✓ Sensor values persisted for slow update cycles (5 min intervals)")
    print("✓ Valve positions tracked for diagnostics")
    print()


def example_button_panel():
    """Example 10: Button panel with 8 buttons."""
    print("=" * 60)
    print("Example 10: 8-Button Control Panel")
    print("=" * 60)
    
    print("""
Scenario: Wall-mounted button panel with 8 programmable buttons
─────────────────────────────────────────────────────────────
Device Properties:
  • 8 buttons for different scenes/actions

Required STATE Listeners:
─────────────────────────────────────────────────────────────
Property Path              Entity ID                   Type
─────────────────────────────────────────────────────────────
button[0].value      →    binary_sensor.panel_btn0   Boolean
button[1].value      →    binary_sensor.panel_btn1   Boolean
button[2].value      →    binary_sensor.panel_btn2   Boolean
button[3].value      →    binary_sensor.panel_btn3   Boolean
button[4].value      →    binary_sensor.panel_btn4   Boolean
button[5].value      →    binary_sensor.panel_btn5   Boolean
button[6].value      →    binary_sensor.panel_btn6   Boolean
button[7].value      →    binary_sensor.panel_btn7   Boolean
─────────────────────────────────────────────────────────────
Total: 8 listeners for 1 device
""")
    
    print("✓ Each button gets independent tracking")
    print("✓ Button values typically NOT persisted (transient events)")
    print("✓ But button.actionId and button.actionMode MAY be persisted")
    print()


def example_auto_configuration():
    """Example 11: Automatic listener creation from device attributes."""
    print("=" * 60)
    print("Example 11: Automatic Listener Configuration")
    print("=" * 60)
    
    print("""
When a device is created/loaded, the system automatically:

1. Reads device attributes to determine property counts:
   {
     "num_buttons": 3,
     "num_sensors": 2,
     "num_channels": 4,
     "group_id": 1  # Light
   }

2. Checks for entity_mappings in attributes:
   {
     "entity_mappings": {
       "channel[0].value": "light.living_room",
       "channel[1].value": "light.living_room@red",
       "channel[2].value": "light.living_room@green",
       "channel[3].value": "light.living_room@blue",
       "button[0].value": "binary_sensor.btn0",
       "button[1].value": "binary_sensor.btn1",
       "button[2].value": "binary_sensor.btn2",
       "sensor[0].value": "sensor.power",
       "sensor[1].value": "sensor.energy"
     }
   }

3. Auto-creates 9 listeners (4 channels + 3 buttons + 2 sensors)

4. Saves mappings to virtual_digitalstrom_listener_mappings.yaml

5. Starts all listeners to begin tracking

Result:
  ✓ Zero manual configuration required
  ✓ All STATE properties automatically tracked
  ✓ Proper indexing for multiple instances
  ✓ Persistence configured per property type
""")
    print()


def example_state_persistence():
    """Example 12: State persistence strategy."""
    print("=" * 60)
    print("Example 12: State Persistence Strategy")
    print("=" * 60)
    
    print("""
State Persistence Decision Matrix:
─────────────────────────────────────────────────────────────
Property Type               | Persist? | Reason
─────────────────────────────────────────────────────────────
sensor.value                | ✅ YES   | Slow update cycles
channel.value               | ✅ YES   | Immediate display
control.heatingLevel        | ✅ YES   | CRITICAL for connection loss
control.coolingLevel        | ✅ YES   | CRITICAL for connection loss
control.ventilationLevel    | ✅ YES   | CRITICAL for connection loss
connection_status           | ✅ YES   | System state
system_status               | ✅ YES   | System state
output.localPriority        | ✅ YES   | Operating mode
output.error                | ✅ YES   | Error tracking
button.value                | ❌ NO    | Transient event
button.actionId             | ❓ MAYBE | Scene recall history
binary.value                | ✅ YES   | Last known state
binary.extendedValue        | ✅ YES   | Additional context
dynamicAction.name          | ❌ NO    | Runtime generated
deviceState.value           | ✅ YES   | Device state tracking
deviceProperty.value        | ✅ YES   | Property tracking
─────────────────────────────────────────────────────────────

Implementation:
  • Always persist: Stored in state.yaml
  • Never persist: Callback receives update but doesn't save
  • Maybe persist: Configuration option per device

Multiple Instances Persistence:
  • button[0].value - NOT persisted (transient)
  • button[1].value - NOT persisted (transient)
  • button[2].value - NOT persisted (transient)
  • sensor[0].value - Persisted (temp sensor, slow updates)
  • sensor[1].value - Persisted (humidity sensor, slow updates)
  • channel[0].value - Persisted (brightness)
  • channel[1].value - Persisted (color red)
  • channel[2].value - Persisted (color green)
  • channel[3].value - Persisted (color blue)

Each instance is tracked and persisted independently!
""")
    print()


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  STATE LISTENER SYSTEM - USAGE EXAMPLES".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    example_basic_listener()
    example_multiple_listeners()
    example_heating_radiator()
    example_manager_usage()
    example_yaml_mapping()
    example_multiple_instances()
    example_blind_with_tilt()
    example_climate_controller()
    example_button_panel()
    example_auto_configuration()
    example_state_persistence()
    
    print("=" * 60)
    print("✓ All examples completed")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("  • Devices can have MULTIPLE instances of same property type")
    print("  • Each instance gets its own listener with unique index")
    print("  • Auto-configuration detects all instances from device attributes")
    print("  • YAML mappings file preserves all listener configurations")
    print("  • Critical properties (control values) MUST be persisted")
    print("\nNext Steps:")
    print("  1. Integrate StateListenerManager into __init__.py ✓")
    print("  2. Auto-create listeners during device setup ✓")
    print("  3. Add UI for mapping configuration")
    print("  4. Implement state.yaml persistence layer")
    print()


if __name__ == "__main__":
    main()
