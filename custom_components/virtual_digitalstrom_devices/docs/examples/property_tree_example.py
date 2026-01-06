"""Example: Creating devices with property tree configurations.

This example demonstrates the correct usage of the 'configurations' property
as a property tree structure (vDC spec sections 4.1.2-4.1.4).
"""

import sys
import os

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)

from models.virtual_device import VirtualDevice
from models.property_tree import (
    DeviceConfigurations,
    ConfigurationPropertyTree,
    ConfigurationInputDescriptions,
    ConfigurationOutputChannels,
    ConfigurationScenes,
)

def example_simple_light():
    """Create a simple light device with default configuration."""
    print("=" * 70)
    print("Example 1: Simple Light Device with Default Configuration")
    print("=" * 70)
    
    # Create a virtual device with default configuration
    device = VirtualDevice(
        name="Living Room Light",
        model="LED Dimmer",
        display_id="LR-LIGHT-01",
        vendor_name="Philips",
        group_id=1,  # Light group
        zone_id=0,
    )
    
    print(f"Device: {device.name}")
    print(f"dSUID: {device.dsid}")
    print(f"Configurations: {device.configurations}")
    
    if hasattr(device.configurations, 'configurations'):
        for config in device.configurations.configurations:
            print(f"  - Config ID: {config.config_id}")
            print(f"    Description: {config.description}")
    
    # Serialize to dict
    device_dict = device.to_dict()
    print(f"\nSerialized configurations: {device_dict.get('configurations')}")
    print(f"Property tree: {list(device_dict.get('configurations_tree', {}).keys())}")
    print()


def example_light_with_button():
    """Create a light device with button input in configuration."""
    print("=" * 70)
    print("Example 2: Light Device with Button Input Configuration")
    print("=" * 70)
    
    # Create configurations with input references
    configs = DeviceConfigurations()
    
    # Create a configuration that includes button input
    default_config = ConfigurationPropertyTree(
        config_id="default",
        description="Default configuration with wall switch",
    )
    
    # Add button input reference (button input 0)
    default_config.inputs.button_input_ids = [0]
    
    # Add output reference (output 0 - the dimmer)
    default_config.outputs.output_id = 0
    default_config.outputs.channel_ids = [0]  # Channel 0 is brightness
    
    # Add scene references (scenes 0-4)
    default_config.scenes.scene_ids = [0, 1, 2, 3, 4]  # Off, Preset1-4
    
    configs.add_configuration(default_config)
    configs.current_config_id = "default"
    
    # Create device
    device = VirtualDevice(
        name="Bedroom Light",
        model="LED Dimmer with Switch",
        display_id="BR-LIGHT-01",
        group_id=1,
        zone_id=0,
        configurations=configs,
    )
    
    print(f"Device: {device.name}")
    print(f"dSUID: {device.dsid}")
    print(f"Current config: {device.configurations.current_config_id}")
    
    # Show property tree structure
    config = device.configurations.get_configuration("default")
    if config:
        print(f"\nConfiguration '{config.config_id}':")
        print(f"  Button inputs: {config.inputs.button_input_ids}")
        print(f"  Output ID: {config.outputs.output_id}")
        print(f"  Channel IDs: {config.outputs.channel_ids}")
        print(f"  Scene IDs: {config.scenes.scene_ids}")
    
    # Show property elements structure
    prop_elements = configs.to_property_elements()
    print(f"\nProperty tree elements:")
    for config_id, elements in prop_elements.items():
        print(f"  Config '{config_id}':")
        for key, value in elements.items():
            print(f"    {key}: {value}")
    print()


def example_multi_configuration():
    """Create a device with multiple configurations."""
    print("=" * 70)
    print("Example 3: Device with Multiple Configurations")
    print("=" * 70)
    
    configs = DeviceConfigurations()
    
    # Configuration 1: Normal mode
    normal_config = ConfigurationPropertyTree(
        config_id="normal",
        description="Normal operation mode",
    )
    normal_config.inputs.button_input_ids = [0]  # Wall switch
    normal_config.outputs.output_id = 0
    normal_config.outputs.channel_ids = [0]  # Brightness only
    normal_config.scenes.scene_ids = [0, 1, 2, 3, 4]
    configs.add_configuration(normal_config)
    
    # Configuration 2: Party mode
    party_config = ConfigurationPropertyTree(
        config_id="party",
        description="Party mode with color effects",
    )
    party_config.inputs.button_input_ids = [0, 1]  # Wall switch + remote
    party_config.outputs.output_id = 0
    party_config.outputs.channel_ids = [0, 1, 2]  # Brightness, hue, saturation
    party_config.scenes.scene_ids = [0, 10, 11, 12, 13]  # Off + party scenes
    configs.add_configuration(party_config)
    
    configs.current_config_id = "normal"
    
    # Create device
    device = VirtualDevice(
        name="Party Room RGB Light",
        model="RGB LED Controller",
        display_id="PR-RGB-01",
        group_id=1,
        zone_id=0,
        configurations=configs,
    )
    
    print(f"Device: {device.name}")
    print(f"dSUID: {device.dsid}")
    print(f"Available configurations: {[c.config_id for c in device.configurations.configurations]}")
    print(f"Current config: {device.configurations.current_config_id}")
    
    for config in device.configurations.configurations:
        print(f"\nConfiguration '{config.config_id}': {config.description}")
        print(f"  Inputs: {len(config.inputs.button_input_ids)} button(s)")
        print(f"  Channels: {len(config.outputs.channel_ids)} channel(s)")
        print(f"  Scenes: {len(config.scenes.scene_ids)} scene(s)")
    print()


def example_serialization():
    """Example of saving and loading devices with property trees."""
    print("=" * 70)
    print("Example 4: Serialization and Deserialization")
    print("=" * 70)
    
    # Create a device with configuration
    original_device = VirtualDevice(
        name="Test Light",
        model="Test Dimmer",
        group_id=1,
    )
    
    print("Original device:")
    print(f"  Name: {original_device.name}")
    print(f"  dSUID: {original_device.dsid}")
    
    # Serialize to dictionary (YAML-compatible)
    device_dict = original_device.to_dict()
    print(f"\nSerialized keys: {list(device_dict.keys())}")
    
    # Deserialize back
    loaded_device = VirtualDevice.from_dict(device_dict)
    print(f"\nLoaded device:")
    print(f"  Name: {loaded_device.name}")
    print(f"  dSUID: {loaded_device.dsid}")
    print(f"  Configurations match: {loaded_device.configurations is not None}")
    print()


if __name__ == "__main__":
    example_simple_light()
    example_light_with_button()
    example_multi_configuration()
    example_serialization()
    
    print("=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)
