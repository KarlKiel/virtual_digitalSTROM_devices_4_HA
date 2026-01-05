#!/usr/bin/env python3
"""Example usage of the device storage system.

This example demonstrates how to use the VirtualDevice and DeviceStorage
classes to manage digitalSTROM device configurations.

NOTE: To run this example standalone, execute it from within the integration directory:
cd custom_components/virtual_digitalstrom_devices && python3 example_device_storage.py
"""

import sys
from pathlib import Path

# For standalone execution, add current directory to path
if __name__ == "__main__":
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))

# Import modules directly (not through package __init__.py)
import virtual_device
import device_storage
import device_classes


def main():
    """Example usage of device storage."""
    
    # Initialize device storage
    storage_file = Path("example_devices.yaml")
    storage = device_storage.DeviceStorage(storage_file)
    
    print("=== Virtual digitalSTROM Device Storage Example ===\n")
    
    # Create and add devices
    print("Creating devices...")
    
    light = virtual_device.VirtualDevice(
        name="Living Room Light",
        group_id=device_classes.DSGroupID.LIGHTS,
        ha_entity_id="light.living_room",
        zone_id=1,
        attributes={"brightness": 255, "color_temp": 4000}
    )
    
    blind = virtual_device.VirtualDevice(
        name="Bedroom Blinds",
        group_id=device_classes.DSGroupID.BLINDS,
        ha_entity_id="cover.bedroom_blinds",
        zone_id=2,
        attributes={"position": 50, "tilt": 45}
    )
    
    # Add devices to storage
    storage.add_device(light)
    storage.add_device(blind)
    
    print(f"Added {len(storage.get_all_devices())} devices\n")
    
    # List all devices
    print("All devices:")
    for device in storage.get_all_devices():
        print(f"  - {device.name} (Group: {device.group_id}, Entity: {device.ha_entity_id})")
    
    print(f"\n✓ Devices saved to {storage_file}")
    
    # Update a device
    print(f"\nUpdating {light.name}...")
    storage.update_device(light.device_id, name="Main Living Room Light")
    
    # Get devices by group
    print("\nDevices in LIGHTS group:")
    for device in storage.get_devices_by_group(device_classes.DSGroupID.LIGHTS):
        print(f"  - {device.name}")
    
    print("\n✓ Example completed successfully!")
    print(f"\nYou can find the device configuration in: {storage_file.absolute()}")


if __name__ == "__main__":
    main()
