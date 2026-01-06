"""Data Models for Virtual digitalSTROM Devices.

This package contains all data models including device classes,
virtual devices, property elements, property trees, and DSUID generation.
"""

from .device_classes import (
    ADDITIONAL_COLOR_GROUPS,
    DEVICE_CLASSES,
    DSColor,
    DSGroupID,
    DSPrimaryChannel,
    DeviceClass,
    get_all_device_classes,
    get_device_class,
    get_device_classes_by_color,
)
from .dsuid_generator import *
from .virtual_device import *
from .property_element import PropertyElement, PropertyValue, build_property_tree_from_dict, property_tree_to_dict
from .property_tree import (
    DeviceConfigurations,
    ConfigurationPropertyTree,
    ConfigurationInputDescriptions,
    ConfigurationOutputChannels,
    ConfigurationScenes,
)
from .vdc_entity import VDCEntity, CommonEntityProperties, VDCCapabilities, create_vdc_entity
from .device_converter import (
    virtual_device_to_property_element,
    property_element_to_virtual_device,
    create_vdsd_property_element_tree,
    extract_property_subtree,
    merge_property_updates,
)

__all__ = [
    "DEVICE_CLASSES",
    "ADDITIONAL_COLOR_GROUPS",
    "DSColor",
    "DSGroupID",
    "DSPrimaryChannel",
    "DeviceClass",
    "get_device_class",
    "get_device_classes_by_color",
    "get_all_device_classes",
    "dsuid_generator",
    "virtual_device",
    "PropertyElement",
    "PropertyValue",
    "build_property_tree_from_dict",
    "property_tree_to_dict",
    "DeviceConfigurations",
    "ConfigurationPropertyTree",
    "ConfigurationInputDescriptions",
    "ConfigurationOutputChannels",
    "ConfigurationScenes",
    "VDCEntity",
    "CommonEntityProperties",
    "VDCCapabilities",
    "create_vdc_entity",
    "virtual_device_to_property_element",
    "property_element_to_virtual_device",
    "create_vdsd_property_element_tree",
    "extract_property_subtree",
    "merge_property_updates",
]
