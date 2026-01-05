"""Constants for the Virtual digitalSTROM Devices integration."""

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

# Domain name for the integration
DOMAIN = "virtual_digitalstrom_devices"

# Default values
DEFAULT_NAME = "Virtual digitalSTROM Devices"

# Export device class information
__all__ = [
    "DOMAIN",
    "DEFAULT_NAME",
    "DEVICE_CLASSES",
    "ADDITIONAL_COLOR_GROUPS",
    "DSColor",
    "DSGroupID",
    "DSPrimaryChannel",
    "DeviceClass",
    "get_device_class",
    "get_device_classes_by_color",
    "get_all_device_classes",
]
