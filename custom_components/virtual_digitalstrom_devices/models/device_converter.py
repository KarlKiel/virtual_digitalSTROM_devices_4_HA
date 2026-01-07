"""VirtualDevice to PropertyElement converter.

This module provides functions to convert VirtualDevice instances to complete
PropertyElement trees suitable for vDC API communication.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

try:
    from .virtual_device import VirtualDevice
    from .property_element import PropertyElement, PropertyValue, build_property_tree_from_dict
    from .property_tree import DeviceConfigurations
except ImportError:
    # Fallback for standalone usage
    from virtual_device import VirtualDevice  # type: ignore
    from property_element import PropertyElement, PropertyValue, build_property_tree_from_dict  # type: ignore
    from property_tree import DeviceConfigurations  # type: ignore


def virtual_device_to_property_element(device: VirtualDevice, name: str = "device") -> PropertyElement:
    """Convert a VirtualDevice to a complete PropertyElement tree.
    
    This creates the full property tree structure needed for vDC API messages,
    including all common properties, device properties, and configurations.
    
    Args:
        device: VirtualDevice instance
        name: Root element name (default: "device")
        
    Returns:
        PropertyElement tree representing the complete device
    """
    # Build dictionary representation
    device_dict = {}
    
    # Common properties (Chapter 2)
    device_dict["dSUID"] = device.dsid
    device_dict["displayId"] = device.display_id
    device_dict["type"] = device.type
    device_dict["model"] = device.model
    device_dict["modelVersion"] = device.model_version
    device_dict["modelUID"] = device.model_uid
    
    # Optional common properties
    if device.hardware_version:
        device_dict["hardwareVersion"] = device.hardware_version
    if device.hardware_guid:
        device_dict["hardwareGuid"] = device.hardware_guid
    if device.hardware_model_guid:
        device_dict["hardwareModelGuid"] = device.hardware_model_guid
    if device.vendor_name:
        device_dict["vendorName"] = device.vendor_name
    if device.vendor_guid:
        device_dict["vendorGuid"] = device.vendor_guid
    if device.oem_guid:
        device_dict["oemGuid"] = device.oem_guid
    if device.oem_model_guid:
        device_dict["oemModelGuid"] = device.oem_model_guid
    if device.device_class:
        device_dict["deviceClass"] = device.device_class
    if device.device_class_version:
        device_dict["deviceClassVersion"] = device.device_class_version
    if device.active is not None:
        device_dict["active"] = device.active
    if device.name:
        device_dict["name"] = device.name
    
    # Device-specific properties (Chapter 4.1.1)
    device_dict["primaryGroup"] = device.group_id
    device_dict["zoneID"] = device.zone_id
    
    # Model features
    device_dict["modelFeatures"] = device.attributes.get("modelFeatures", {})
    
    # Configurations as property tree
    if device.configurations and isinstance(device.configurations, DeviceConfigurations):
        device_dict["configurations"] = device.configurations.to_property_elements()
    elif device.configurations and isinstance(device.configurations, list):
        # Legacy format - convert to simple structure
        device_dict["configurations"] = {
            config_id: {"id": config_id}
            for config_id in device.configurations
        }
    
    # Build PropertyElement tree from dictionary
    return build_property_tree_from_dict(device_dict, name)


def property_element_to_virtual_device(element: PropertyElement) -> VirtualDevice:
    """Convert a PropertyElement tree back to a VirtualDevice.
    
    Args:
        element: PropertyElement tree representing a device
        
    Returns:
        VirtualDevice instance
    """
    # This would require implementing the reverse conversion
    # For now, we use the existing from_dict method
    from .property_element import property_tree_to_dict
    
    device_dict = property_tree_to_dict(element)
    
    # Extract from nested structure if needed
    if element.name in device_dict:
        device_dict = device_dict[element.name]
    
    # Convert property tree format to VirtualDevice format
    converted = {
        "device_id": device_dict.get("deviceId", device_dict.get("dSUID", "")),
        "dsid": device_dict.get("dSUID", ""),
        "display_id": device_dict.get("displayId", ""),
        "type": device_dict.get("type", "vdSD"),
        "model": device_dict.get("model", ""),
        "model_version": device_dict.get("modelVersion", ""),
        "model_uid": device_dict.get("modelUID", ""),
        "hardware_version": device_dict.get("hardwareVersion", ""),
        "hardware_guid": device_dict.get("hardwareGuid", ""),
        "hardware_model_guid": device_dict.get("hardwareModelGuid", ""),
        "vendor_name": device_dict.get("vendorName", ""),
        "vendor_guid": device_dict.get("vendorGuid", ""),
        "oem_guid": device_dict.get("oemGuid", ""),
        "oem_model_guid": device_dict.get("oemModelGuid", ""),
        "device_class": device_dict.get("deviceClass", ""),
        "device_class_version": device_dict.get("deviceClassVersion", ""),
        "active": device_dict.get("active"),
        "name": device_dict.get("name", ""),
        "group_id": device_dict.get("primaryGroup", 0),
        "zone_id": device_dict.get("zoneID", 0),
        "ha_entity_id": device_dict.get("haEntityId", ""),
        "attributes": {"modelFeatures": device_dict.get("modelFeatures", {})},
    }
    
    return VirtualDevice.from_dict(converted)


def create_vdsd_property_element_tree(device: VirtualDevice) -> PropertyElement:
    """Create a complete vdSD property element tree for API messages.
    
    This creates the full hierarchical structure including:
    - Common properties (Chapter 2)
    - General device properties (Chapter 4.1.1)
    - Configurations with nested inputs/outputs/scenes
    - Button/Binary/Sensor input descriptions, settings, states
    - Output description, settings, state
    - Channel descriptions and states
    - Scene configurations
    
    Args:
        device: VirtualDevice instance
        
    Returns:
        Complete PropertyElement tree for vDC API
    """
    # Start with basic device property element
    device_elem = virtual_device_to_property_element(device, "vdSD")
    
    # TODO: Add input/output/scene property elements when those are implemented
    # For now, return basic structure
    
    return device_elem


def extract_property_subtree(
    root: PropertyElement,
    path: List[str]
) -> Optional[PropertyElement]:
    """Extract a property subtree from a PropertyElement tree.
    
    This is useful for vDC API GetProperty requests where only a portion
    of the property tree is requested.
    
    Args:
        root: Root PropertyElement
        path: List of property names forming the path
        
    Returns:
        PropertyElement subtree if found, None otherwise
        
    Example:
        # Get buttonInputDescriptions.0.name
        subtree = extract_property_subtree(
            device_tree,
            ["buttonInputDescriptions", "0", "name"]
        )
    """
    current = root
    
    for name in path:
        if not current.elements:
            return None
        
        found = False
        for elem in current.elements:
            if elem.name == name:
                current = elem
                found = True
                break
        
        if not found:
            return None
    
    return current


def merge_property_updates(
    target: PropertyElement,
    updates: PropertyElement
) -> PropertyElement:
    """Merge property updates into a target PropertyElement tree.
    
    This is used for vDC API SetProperty requests to update specific
    properties while preserving the rest of the tree.
    
    Args:
        target: Target PropertyElement tree
        updates: PropertyElement with updates to apply
        
    Returns:
        Updated PropertyElement tree
    """
    # For now, simple implementation
    # TODO: Implement proper recursive merge
    return updates
