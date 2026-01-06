#!/usr/bin/env python3
"""Example demonstrating state restoration functionality.

This example shows how the state restoration system works by:
1. Creating devices with persisted STATE values
2. Saving them to YAML
3. Restoring the state values on "restart"
4. Verifying the restoration worked correctly

NOTE: This is a simplified demonstration without Home Assistant.
For actual HA integration testing, use Home Assistant's test framework.
"""

import sys
from pathlib import Path
import tempfile
import yaml

# For standalone execution, add current directory to path
if __name__ == "__main__":
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))

# Direct module imports for standalone execution
import virtual_device
import device_storage
import device_classes


def create_test_device_with_state():
    """Create a test device with persisted STATE values."""
    
    # Create a light device
    light = virtual_device.VirtualDevice(
        display_id="LIGHT-TEST-001",
        model="Virtual Dimmable Light",
        model_version="1.0.0",
        model_uid="vdSD-light-dimmer-v1",
        name="Test Living Room Light",
        group_id=device_classes.DSGroupID.LIGHTS,
        ha_entity_id="light.test_living_room",
        zone_id=1,
        attributes={
            "brightness": 255,
            "color_temp": 4000,
            "dimmable": True,
            "entity_mappings": {
                "channel[0].value": "light.test_living_room",
                "sensor[0].value": "sensor.test_power",
            },
            # Persisted STATE values (as they would be saved by property_updater)
            "state_values": {
                "channel.value[0]": {
                    "value": 75.5,
                    "timestamp": "2024-01-06T12:00:00",
                },
                "sensor.value[0]": {
                    "value": 42.3,
                    "timestamp": "2024-01-06T12:00:00",
                },
                "device.connection_status": {
                    "value": "connected",
                    "timestamp": "2024-01-06T12:00:00",
                },
            }
        }
    )
    
    return light


def create_test_climate_device_with_state():
    """Create a climate device with persisted control values."""
    
    climate = virtual_device.VirtualDevice(
        display_id="CLIMATE-TEST-001",
        model="Virtual Heating Control",
        model_version="1.0.0",
        model_uid="vdSD-climate-v1",
        name="Test Bedroom Radiator",
        group_id=device_classes.DSGroupID.HEATING,
        ha_entity_id="climate.test_bedroom",
        zone_id=2,
        attributes={
            "entity_mappings": {
                "control.heatingLevel": "climate.test_bedroom",
                "sensor[0].value": "sensor.test_temperature",
            },
            # Persisted STATE values for climate control
            "state_values": {
                "control.heatingLevel": {
                    "value": 21.5,
                    "timestamp": "2024-01-06T11:30:00",
                },
                "sensor.value[0]": {
                    "value": 20.2,
                    "timestamp": "2024-01-06T11:30:00",
                },
            }
        }
    )
    
    return climate


def main():
    """Example demonstrating state restoration."""
    
    print("=== Virtual digitalSTROM Device State Restoration Example ===\n")
    
    # Create temporary storage file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        storage_file = Path(f.name)
    
    try:
        # === STEP 1: Create and save devices with STATE values ===
        print("STEP 1: Creating devices with persisted STATE values...")
        storage = device_storage.DeviceStorage(storage_file)
        
        light = create_test_device_with_state()
        climate = create_test_climate_device_with_state()
        
        storage.add_device(light)
        storage.add_device(climate)
        
        print(f"✓ Created and saved 2 devices to {storage_file}\n")
        
        # Show what was saved
        print("Saved STATE values for light:")
        for key, data in light.attributes["state_values"].items():
            print(f"  {key}: {data['value']}")
        
        print("\nSaved STATE values for climate:")
        for key, data in climate.attributes["state_values"].items():
            print(f"  {key}: {data['value']}")
        
        # === STEP 2: Show YAML content ===
        print(f"\n{'='*60}")
        print("YAML Storage Content:")
        print(f"{'='*60}")
        with open(storage_file, 'r') as f:
            yaml_content = f.read()
            print(yaml_content)
        
        # === STEP 3: Simulate restart - load devices from YAML ===
        print(f"{'='*60}")
        print("\nSTEP 2: Simulating restart - loading devices from storage...")
        
        # Create new storage instance (simulates restart)
        storage2 = device_storage.DeviceStorage(storage_file)
        
        # Verify devices were loaded
        loaded_devices = storage2.get_all_devices()
        print(f"✓ Loaded {len(loaded_devices)} devices from storage\n")
        
        # === STEP 4: Verify STATE values were preserved ===
        print("STEP 3: Verifying STATE values were preserved in YAML...")
        
        for device in loaded_devices:
            print(f"\nDevice: {device.name}")
            state_values = device.attributes.get("state_values", {})
            
            if state_values:
                print(f"  Found {len(state_values)} persisted STATE values:")
                for key, data in state_values.items():
                    value = data.get("value") if isinstance(data, dict) else data
                    timestamp = data.get("timestamp", "N/A") if isinstance(data, dict) else "N/A"
                    print(f"    {key}: {value} (at {timestamp})")
            else:
                print("  No STATE values found")
        
        # === STEP 5: Demonstrate parsing state keys ===
        print(f"\n{'='*60}")
        print("STEP 4: Demonstrating state key parsing...")
        print(f"{'='*60}\n")
        
        import re
        
        def parse_state_key(key):
            """Parse a state key into property type and optional index."""
            pattern = r"^(.+?)(?:\[(\d+)\])?$"
            match = re.match(pattern, key)
            
            if not match:
                return None, None
            
            property_type_str, index_str = match.groups()
            index = int(index_str) if index_str else None
            
            return property_type_str, index
        
        test_keys = [
            "channel.value[0]",
            "sensor.value[0]",
            "control.heatingLevel",
            "device.connection_status",
        ]
        
        print("State key parsing examples:")
        for key in test_keys:
            prop_type, index = parse_state_key(key)
            print(f"  '{key}' -> property_type='{prop_type}', index={index}")
        
        # === SUCCESS ===
        print(f"\n{'='*60}")
        print("✓ Example completed successfully!")
        print(f"{'='*60}\n")
        
        print("Summary:")
        print("1. Created devices with persisted STATE values")
        print("2. Saved devices to YAML storage")
        print("3. Loaded devices from YAML (simulated restart)")
        print("4. Verified STATE values were preserved")
        print("\nIn the actual Home Assistant integration:")
        print("- StateRestorer reads these state_values during startup")
        print("- Optionally pushes them to HA entities")
        print("- State listeners then track new changes")
        
    finally:
        # Cleanup
        if storage_file.exists():
            storage_file.unlink()
            print(f"\n✓ Cleaned up temporary file: {storage_file}")


if __name__ == "__main__":
    main()
