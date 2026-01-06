"""Data Models for Virtual digitalSTROM Devices.

This package contains all data models including device classes,
virtual devices, and DSUID generation.
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
]
