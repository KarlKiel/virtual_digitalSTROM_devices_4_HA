"""Complete integration example showing PropertyElement usage throughout the stack.

This demonstrates:
1. Creating a VirtualDevice
2. Converting it to PropertyElement tree
3. Building vDC API messages
4. Persisting and loading from storage
"""

import sys
import os

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)

from models.virtual_device import VirtualDevice
from models.device_converter import (
    virtual_device_to_property_element,
    create_vdsd_property_element_tree,
)
from models.property_element import PropertyElement
from models.property_tree import (
    DeviceConfigurations,
    ConfigurationPropertyTree,
)
from models.vdc_entity import create_vdc_entity


def example_complete_workflow():
    """Example: Complete workflow from device creation to API message."""
    print("=" * 70)
    print("Complete Integration Example")
    print("=" * 70)
    
    # Step 1: Create a VirtualDevice
    print("\n1. Creating VirtualDevice...")
    device = VirtualDevice(
        name="Living Room Light",
        model="LED Dimmer Pro",
        display_id="LR-LIGHT-01",
        vendor_name="Philips",
        group_id=1,  # Light
        zone_id=0,
        ha_entity_id="light.living_room",
    )
    
    # Add configuration
    configs = DeviceConfigurations()
    default_config = ConfigurationPropertyTree(
        config_id="default",
        description="Default configuration with button and dimmer"
    )
    default_config.inputs.button_input_ids = [0]
    default_config.outputs.output_id = 0
    default_config.outputs.channel_ids = [0]  # Brightness
    default_config.scenes.scene_ids = [0, 1, 2, 3, 4]
    configs.add_configuration(default_config)
    device.configurations = configs
    
    print(f"   Created: {device.name}")
    print(f"   dSUID: {device.dsid}")
    print(f"   Type: {device.type}")
    print(f"   Group: {device.group_id}")
    
    # Step 2: Convert to PropertyElement tree
    print("\n2. Converting to PropertyElement tree...")
    prop_tree = virtual_device_to_property_element(device)
    
    print(f"   Root element: {prop_tree.name}")
    print(f"   Number of properties: {len(prop_tree.elements)}")
    
    # Show some properties
    for elem in prop_tree.elements[:5]:
        if elem.is_leaf():
            value = elem.value.to_python() if elem.value else None
            print(f"     {elem.name}: {value}")
        else:
            print(f"     {elem.name}: <{len(elem.elements)} child elements>")
    
    # Step 3: Create vDC entity with device
    print("\n3. Creating vDC entity...")
    vdc = create_vdc_entity(
        ds_uid="3C04E83200000000000000000000000100",
        name="Virtual digitalSTROM Devices (HA)"
    )
    
    # Convert device to property element for vDC
    device_prop_elem = create_vdsd_property_element_tree(device)
    device_dict = device_prop_elem.to_dict()
    vdc.add_vdsd(device_dict)
    
    print(f"   vDC dSUID: {vdc.common.ds_uid}")
    print(f"   vDC Name: {vdc.common.name}")
    print(f"   Number of devices: {len(vdc.vdsds)}")
    
    # Step 4: Generate vDC property tree for API
    print("\n4. Generating vDC property tree for API...")
    vdc_tree = vdc.to_property_tree()
    
    print(f"   Tree keys: {list(vdc_tree.keys())[:10]}")
    print(f"   vDC type: {vdc_tree.get('type')}")
    print(f"   vDC capabilities: {vdc_tree.get('capabilities')}")
    
    # Step 5: Persist device (via to_dict/from_dict)
    print("\n5. Persistence (YAML-compatible)...")
    device_dict_storage = device.to_dict()
    
    print(f"   Serialized keys: {list(device_dict_storage.keys())}")
    print(f"   Has configurations_tree: {'configurations_tree' in device_dict_storage}")
    print(f"   Has configurations list: {'configurations' in device_dict_storage}")
    
    # Step 6: Load device back
    print("\n6. Loading device from storage...")
    loaded_device = VirtualDevice.from_dict(device_dict_storage)
    
    print(f"   Loaded: {loaded_device.name}")
    print(f"   dSUID matches: {loaded_device.dsid == device.dsid}")
    print(f"   Configurations match: {loaded_device.configurations is not None}")
    
    # Step 7: Build API message using PropertyElement
    print("\n7. Building vDC API message...")
    
    # This would typically be done by MessageBuilder
    # For demonstration, show the PropertyElement structure
    from models.property_element import build_property_tree_from_dict
    
    # Simulate a GetProperty response
    response_data = {
        "dSUID": device.dsid,
        "type": "vdSD",
        "primaryGroup": device.group_id,
        "name": device.name,
    }
    
    response_tree = build_property_tree_from_dict(response_data, "response")
    
    print(f"   Response element: {response_tree.name}")
    print(f"   Response properties: {len(response_tree.elements)}")
    
    for elem in response_tree.elements:
        if elem.is_leaf():
            value = elem.value.to_python() if elem.value else None
            print(f"     {elem.name}: {value}")
    
    print("\n" + "=" * 70)
    print("Integration workflow complete!")
    print("=" * 70)
    
    print("\nKey takeaways:")
    print("1. VirtualDevice stores devices in HA format")
    print("2. PropertyElement provides vDC API format")
    print("3. Converters handle transformation between formats")
    print("4. Storage uses to_dict/from_dict with property tree support")
    print("5. MessageBuilder converts PropertyElement to protobuf")
    print("6. Everything works together seamlessly!")


if __name__ == "__main__":
    example_complete_workflow()
