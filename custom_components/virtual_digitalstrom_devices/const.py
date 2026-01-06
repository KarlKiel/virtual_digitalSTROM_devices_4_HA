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

# Storage
STORAGE_FILE = "virtual_digitalstrom_devices.yaml"
STATE_LISTENER_MAPPINGS_FILE = "virtual_digitalstrom_listener_mappings.yaml"
VDC_CONFIG_FILE = "virtual_digitalstrom_vdc_config.yaml"

# Configuration keys
CONF_DSS_PORT = "dss_port"
DEFAULT_DSS_PORT = 8440

# Export device class information
__all__ = [
    "DOMAIN",
    "DEFAULT_NAME",
    "STORAGE_FILE",
    "STATE_LISTENER_MAPPINGS_FILE",
    "VDC_CONFIG_FILE",
    "CONF_DSS_PORT",
    "DEFAULT_DSS_PORT",
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
