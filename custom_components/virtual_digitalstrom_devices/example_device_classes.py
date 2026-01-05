#!/usr/bin/env python3
"""Example script demonstrating digitalSTROM device classes.

This script shows how to use the device_classes module to work with
digitalSTROM device classifications.
"""

import sys
from pathlib import Path

# Add the custom_components directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from device_classes import (
    ADDITIONAL_COLOR_GROUPS,
    DEVICE_CLASSES,
    DSColor,
    DSGroupID,
    get_all_device_classes,
    get_device_class,
    get_device_classes_by_color,
)


def print_separator(title: str = "", char: str = "=", width: int = 80) -> None:
    """Print a separator line with optional title."""
    if title:
        padding = (width - len(title) - 2) // 2
        print(f"{char * padding} {title} {char * padding}")
    else:
        print(char * width)


def main():
    """Run examples demonstrating device class usage."""
    
    print_separator("digitalSTROM Device Classes Example")
    print()
    
    # Example 1: Get all device classes
    print_separator("Example 1: All Device Classes", "-")
    all_classes = get_all_device_classes()
    print(f"Total device classes: {len(all_classes)}")
    print()
    
    for dc in sorted(all_classes, key=lambda x: x.group_id):
        channel = dc.primary_channel.value if dc.primary_channel else "None"
        print(f"ID {dc.group_id:2d}: {dc.name:25s} [{dc.color.value:8s}] → {channel}")
    print()
    
    # Example 2: Get a specific device class
    print_separator("Example 2: Specific Device Class (Lights)", "-")
    lights = get_device_class(DSGroupID.LIGHTS)
    if lights:
        print(f"Name:            {lights.name}")
        print(f"Group ID:        {lights.group_id}")
        print(f"Color:           {lights.color.value}")
        print(f"Primary Channel: {lights.primary_channel.value if lights.primary_channel else 'None'}")
        print(f"Applications:    {', '.join(lights.applications)}")
        print(f"Description:     {lights.description}")
    print()
    
    # Example 3: Get device classes by color
    print_separator("Example 3: Climate Devices (Blue)", "-")
    blue_classes = get_device_classes_by_color(DSColor.BLUE)
    print(f"Found {len(blue_classes)} climate device classes:")
    print()
    
    for dc in sorted(blue_classes, key=lambda x: x.group_id):
        print(f"  {dc.name:25s} (ID: {dc.group_id:2d})")
        print(f"    Applications: {', '.join(dc.applications)}")
        if dc.primary_channel:
            print(f"    Primary Channel: {dc.primary_channel.value}")
        print()
    
    # Example 4: Query by group ID
    print_separator("Example 4: Query by Group ID", "-")
    test_ids = [1, 2, 8, 64, 999]
    
    for group_id in test_ids:
        dc = get_device_class(group_id)
        if dc:
            print(f"✓ Group ID {group_id:3d}: {dc.name} ({dc.color.value})")
        else:
            print(f"✗ Group ID {group_id:3d}: Not found")
    print()
    
    # Example 5: Color group summary
    print_separator("Example 5: Color Group Summary", "-")
    color_counts = {}
    for dc in all_classes:
        color_counts[dc.color] = color_counts.get(dc.color, 0) + 1
    
    print(f"Device classes by color:")
    for color in DSColor:
        count = color_counts.get(color, 0)
        if count > 0:
            print(f"  {color.value:10s}: {count:2d} device class(es)")
    print()
    
    # Example 6: Additional color groups
    print_separator("Example 6: Additional Color Groups", "-")
    print("These colors are defined but not mapped to specific group IDs:")
    print()
    
    for color, info in ADDITIONAL_COLOR_GROUPS.items():
        print(f"{color.value.upper()}: {info['name']}")
        print(f"  Description: {info['description']}")
        print(f"  Applications: {', '.join(info['applications'])}")
        print()
    
    # Example 7: Device class usage scenario
    print_separator("Example 7: Usage Scenario", "-")
    print("Scenario: Setting up a smart home with different zones")
    print()
    
    zones = {
        "Living Room": [DSGroupID.LIGHTS, DSGroupID.BLINDS, DSGroupID.HEATING, DSGroupID.AUDIO],
        "Bedroom": [DSGroupID.LIGHTS, DSGroupID.BLINDS, DSGroupID.TEMPERATURE_CONTROL],
        "Kitchen": [DSGroupID.LIGHTS, DSGroupID.VENTILATION],
    }
    
    for zone_name, group_ids in zones.items():
        print(f"{zone_name}:")
        for gid in group_ids:
            dc = get_device_class(gid)
            if dc:
                print(f"  - {dc.name:20s} ({dc.color.value})")
        print()
    
    print_separator()


if __name__ == "__main__":
    main()
