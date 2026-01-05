#!/usr/bin/env python3
"""Example usage of the device storage system.

This example demonstrates how to use the VirtualDevice and DeviceStorage
classes to manage digitalSTROM device configurations.
"""

import sys
from pathlib import Path

# Add the current directory to the path for standalone execution
sys.path.insert(0, str(Path(__file__).parent))

from virtual_device import VirtualDevice
from device_storage import DeviceStorage
from device_classes import DSGroupID


def main():
    """Example usage of device storage."""
    
    # Initialize device storage
    storage_file = Path("example_devices.yaml")
    storage = DeviceStorage(storage_file)
    
    print("=== Virtual digitalSTROM Device Storage Example ===\n")
    
    # Create and add devices
    print("Creating devices...")
    
    light = VirtualDevice(
        name="Living Room Light",
        group_id=DSGroupID.LIGHTS,
        ha_entity_id="light.living_room",
        zone_id=1,
        attributes={"brightness": 255, "color_temp": 4000}
    )
    
    blind = VirtualDevice(
        name="Bedroom Blinds",
        group_id=DSGroupID.BLINDS,
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
    for device in storage.get_devices_by_group(DSGroupID.LIGHTS):
        print(f"  - {device.name}")
    
    print("\n✓ Example completed successfully!")
    print(f"\nYou can find the device configuration in: {storage_file.absolute()}")


if __name__ == "__main__":
    main()
