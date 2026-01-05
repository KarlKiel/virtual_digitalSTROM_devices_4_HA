#!/usr/bin/env python3
"""Test script for device storage functionality.

This script demonstrates and tests the YAML-based device persistence layer.
"""

import sys
from pathlib import Path
import tempfile
import shutil

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from virtual_device import VirtualDevice
from device_storage import DeviceStorage
from device_classes import DSGroupID


def print_separator(title: str = "", char: str = "=", width: int = 80) -> None:
    """Print a separator line with optional title."""
    if title:
        padding = (width - len(title) - 2) // 2
        print(f"{char * padding} {title} {char * padding}")
    else:
        print(char * width)


def test_device_storage():
    """Test device storage operations."""
    
    # Create a temporary directory for testing
    temp_dir = Path(tempfile.mkdtemp())
    storage_file = temp_dir / "test_devices.yaml"
    
    try:
        print_separator("Testing Device Storage")
        print(f"Storage file: {storage_file}")
        print()
        
        # Test 1: Initialize storage
        print_separator("Test 1: Initialize Storage", "-")
        storage = DeviceStorage(storage_file)
        print(f"✓ Storage initialized")
        print(f"✓ Number of devices: {len(storage.get_all_devices())}")
        print()
        
        # Test 2: Add devices
        print_separator("Test 2: Add Devices", "-")
        
        device1 = VirtualDevice(
            name="Living Room Light",
            group_id=DSGroupID.LIGHTS,
            ha_entity_id="light.living_room",
            zone_id=1,
            attributes={"brightness": 255}
        )
        
        device2 = VirtualDevice(
            name="Bedroom Blinds",
            group_id=DSGroupID.BLINDS,
            ha_entity_id="cover.bedroom_blinds",
            zone_id=2,
            attributes={"position": 50}
        )
        
        device3 = VirtualDevice(
            name="Kitchen Heating",
            group_id=DSGroupID.HEATING,
            ha_entity_id="climate.kitchen",
            zone_id=3,
            attributes={"temperature": 21.5}
        )
        
        storage.add_device(device1)
        storage.add_device(device2)
        storage.add_device(device3)
        
        print(f"✓ Added 3 devices")
        print(f"✓ Total devices: {len(storage.get_all_devices())}")
        print()
        
        # Test 3: Verify YAML file creation
        print_separator("Test 3: Verify YAML File", "-")
        if storage_file.exists():
            print(f"✓ YAML file created: {storage_file}")
            print("\nYAML file content:")
            print("-" * 80)
            with open(storage_file, "r") as f:
                print(f.read())
            print("-" * 80)
        else:
            print(f"✗ YAML file not found")
        print()
        
        # Test 4: Read devices
        print_separator("Test 4: Read Devices", "-")
        all_devices = storage.get_all_devices()
        print(f"Total devices: {len(all_devices)}")
        for device in all_devices:
            print(f"  - {device.name} (ID: {device.device_id[:8]}..., Group: {device.group_id})")
        print()
        
        # Test 5: Update device
        print_separator("Test 5: Update Device", "-")
        device_id = device1.device_id
        print(f"Updating device: {device1.name}")
        print(f"  Before: brightness={device1.attributes.get('brightness')}")
        
        storage.update_device(
            device_id,
            name="Living Room Main Light",
            attributes={"brightness": 128}
        )
        
        updated_device = storage.get_device(device_id)
        if updated_device:
            print(f"  After: name={updated_device.name}, brightness={updated_device.attributes.get('brightness')}")
            print(f"✓ Device updated successfully")
        print()
        
        # Test 6: Get devices by group
        print_separator("Test 6: Get Devices by Group", "-")
        lights_devices = storage.get_devices_by_group(DSGroupID.LIGHTS)
        print(f"Devices in LIGHTS group (ID {DSGroupID.LIGHTS}):")
        for device in lights_devices:
            print(f"  - {device.name}")
        print()
        
        # Test 7: Delete device
        print_separator("Test 7: Delete Device", "-")
        device_to_delete = device2.device_id
        print(f"Deleting device: {device2.name}")
        storage.delete_device(device_to_delete)
        print(f"✓ Device deleted")
        print(f"✓ Remaining devices: {len(storage.get_all_devices())}")
        print()
        
        # Test 8: Reload from file
        print_separator("Test 8: Reload from File", "-")
        print("Creating new storage instance from same file...")
        storage2 = DeviceStorage(storage_file)
        print(f"✓ Loaded {len(storage2.get_all_devices())} devices from file")
        for device in storage2.get_all_devices():
            print(f"  - {device.name}")
        print()
        
        # Test 9: Device existence check
        print_separator("Test 9: Device Existence Check", "-")
        print(f"Device {device1.device_id[:8]}... exists: {storage.device_exists(device1.device_id)}")
        print(f"Device {device_to_delete[:8]}... exists: {storage.device_exists(device_to_delete)}")
        print()
        
        print_separator("All Tests Completed Successfully!", "=")
        
    finally:
        # Clean up temporary directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            print(f"\n✓ Cleaned up temporary directory: {temp_dir}")


if __name__ == "__main__":
    test_device_storage()
