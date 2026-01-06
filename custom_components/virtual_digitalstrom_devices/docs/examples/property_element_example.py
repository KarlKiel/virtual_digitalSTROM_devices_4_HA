"""Example: Using PropertyElement for vDC API messages.

This demonstrates how to use the PropertyElement structure to build
vDC API messages that can be serialized to protobuf format.
"""

import sys
import os

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)

from models.property_element import (
    PropertyElement,
    PropertyValue,
    build_property_tree_from_dict,
    property_tree_to_dict,
)


def example_simple_property():
    """Example 1: Simple leaf property."""
    print("=" * 70)
    print("Example 1: Simple Leaf Property")
    print("=" * 70)
    
    # Create a simple property: dSUID = "ABC123..."
    prop = PropertyElement.create_leaf("dSUID", "3C04E83200A1B2C3D4E5F6789ABCDEF012")
    
    print(f"Property: {prop.name}")
    print(f"Is leaf: {prop.is_leaf()}")
    print(f"Value: {prop.value.to_python() if prop.value else None}")
    print(f"Dict: {prop.to_dict()}")
    print()


def example_nested_properties():
    """Example 2: Nested properties (branch with leaves)."""
    print("=" * 70)
    print("Example 2: Nested Properties")
    print("=" * 70)
    
    # Build a button input description
    button_desc = PropertyElement.create_branch(
        name="0",  # Index 0
        children=[
            PropertyElement.create_leaf("name", "Wall Switch"),
            PropertyElement.create_leaf("dsIndex", 0),
            PropertyElement.create_leaf("supportsLocalKeyMode", True),
            PropertyElement.create_leaf("buttonType", 1),
            PropertyElement.create_leaf("buttonElementID", 0),
        ]
    )
    
    print(f"Button description: {button_desc.name}")
    print(f"Is branch: {button_desc.is_branch()}")
    print(f"Number of children: {len(button_desc.elements)}")
    
    for child in button_desc.elements:
        value = child.value.to_python() if child.value else None
        print(f"  {child.name}: {value}")
    
    print(f"\nSerialized: {button_desc.to_dict()}")
    print()


def example_complete_device_tree():
    """Example 3: Complete device property tree."""
    print("=" * 70)
    print("Example 3: Complete Device Property Tree")
    print("=" * 70)
    
    # Build from dictionary (simpler)
    device_data = {
        "dSUID": "3C04E83200A1B2C3D4E5F6789ABCDEF012",
        "type": "vdSD",
        "model": "LED Dimmer",
        "modelVersion": "1.0",
        "name": "Living Room Light",
        "primaryGroup": 1,
        "zoneID": 0,
        "configurations": {
            "default": {
                "id": "default",
                "description": "Default configuration",
            }
        },
        "buttonInputDescriptions": {
            "0": {
                "name": "Wall Switch",
                "dsIndex": 0,
                "supportsLocalKeyMode": True,
                "buttonType": 1,
                "buttonElementID": 0,
            }
        },
        "outputDescription": {
            "outputFunction": 1,
            "maxPower": 60.0,
        },
    }
    
    # Build PropertyElement tree
    device_tree = build_property_tree_from_dict(device_data, "device")
    
    print(f"Device tree: {device_tree.name}")
    print(f"Number of top-level properties: {len(device_tree.elements)}")
    
    # Show some properties
    for elem in device_tree.elements[:5]:
        if elem.is_leaf():
            print(f"  {elem.name}: {elem.value.to_python() if elem.value else None}")
        else:
            print(f"  {elem.name}: <{len(elem.elements)} child elements>")
    
    print("\n... (more properties)")
    
    # Convert back to dict
    recovered = property_tree_to_dict(device_tree)
    print(f"\nRecovered dictionary keys: {list(recovered.keys())}")
    print()


def example_vdc_api_message():
    """Example 4: Building a vDC API GetProperty response."""
    print("=" * 70)
    print("Example 4: vDC API GetProperty Response")
    print("=" * 70)
    
    # Build response for vdc_ResponseGetProperty
    # This would contain the requested properties
    
    # Example: Response with dSUID and type
    response_elements = [
        PropertyElement.create_leaf("dSUID", "3C04E83200A1B2C3D4E5F6789ABCDEF012"),
        PropertyElement.create_leaf("type", "vdSD"),
        PropertyElement.create_leaf("primaryGroup", 1),
    ]
    
    print("Response properties:")
    for elem in response_elements:
        print(f"  {elem.name}: {elem.value.to_python() if elem.value else None}")
    
    # In actual usage, these would be serialized to protobuf:
    # message = vdc_ResponseGetProperty()
    # for elem in response_elements:
    #     prop = message.properties.add()
    #     prop.name = elem.name
    #     if elem.value.v_string:
    #         prop.value.v_string = elem.value.v_string
    #     # etc.
    
    print("\nThese PropertyElements would be serialized to protobuf messages")
    print()


def example_property_tree_query():
    """Example 5: Querying a property tree."""
    print("=" * 70)
    print("Example 5: Querying Property Tree")
    print("=" * 70)
    
    # Build a tree
    device_data = {
        "dSUID": "ABC123",
        "primaryGroup": 1,
        "buttonInputDescriptions": {
            "0": {"name": "Switch 1", "dsIndex": 0},
            "1": {"name": "Switch 2", "dsIndex": 1},
        },
    }
    
    tree = build_property_tree_from_dict(device_data, "device")
    
    # Query specific elements
    print("Querying property tree:")
    
    # Find buttonInputDescriptions
    button_elem = tree.get_element("buttonInputDescriptions")
    if button_elem:
        print(f"  Found: {button_elem.name} with {len(button_elem.elements)} buttons")
        
        # Get button 0
        button_0 = button_elem.get_element("0")
        if button_0:
            name_elem = button_0.get_element("name")
            if name_elem and name_elem.value:
                print(f"    Button 0 name: {name_elem.value.to_python()}")
    
    print()


def example_persistence():
    """Example 6: Persisting and loading property trees."""
    print("=" * 70)
    print("Example 6: Persistence (to/from dict)")
    print("=" * 70)
    
    # Create a property tree
    original = PropertyElement.create_branch(
        "device",
        [
            PropertyElement.create_leaf("dSUID", "ABC123"),
            PropertyElement.create_leaf("name", "Test Device"),
            PropertyElement.create_branch(
                "settings",
                [
                    PropertyElement.create_leaf("brightness", 75.0),
                    PropertyElement.create_leaf("enabled", True),
                ]
            ),
        ]
    )
    
    print("Original tree:")
    print(f"  {original.to_dict()}")
    
    # Serialize to dict (can be saved as JSON/YAML)
    serialized = original.to_dict()
    
    # Deserialize back
    restored = PropertyElement.from_dict(serialized)
    
    print("\nRestored tree:")
    print(f"  {restored.to_dict()}")
    
    print(f"\nTrees match: {original.to_dict() == restored.to_dict()}")
    print()


if __name__ == "__main__":
    example_simple_property()
    example_nested_properties()
    example_complete_device_tree()
    example_vdc_api_message()
    example_property_tree_query()
    example_persistence()
    
    print("=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)
    print("\nKey takeaways:")
    print("1. PropertyElement mirrors the protobuf definition")
    print("2. Leaf nodes have name + value")
    print("3. Branch nodes have name + list of child elements")
    print("4. Can build trees from Python dicts for convenience")
    print("5. Trees can be serialized/deserialized for persistence")
    print("6. Ready for protobuf message generation")
