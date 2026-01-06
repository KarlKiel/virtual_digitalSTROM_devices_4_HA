"""Device classes for digitalSTROM system.

This module defines all device classes, color groups, and application types
as specified in the digitalSTROM specification (ds-basics.pdf).

digitalSTROM associates each Application Type with well-defined behavior that
reflects the common expectations of residents and users. Applications are
aggregated into color groups for easy identification and control.
"""

from enum import Enum
from typing import NamedTuple


class DSColor(str, Enum):
    """digitalSTROM color groups."""
    
    YELLOW = "yellow"  # Lights
    GRAY = "gray"      # Blinds
    BLUE = "blue"      # Climate
    CYAN = "cyan"      # Audio
    MAGENTA = "magenta"  # Video
    RED = "red"        # Security
    GREEN = "green"    # Access
    WHITE = "white"    # Single Devices
    BLACK = "black"    # Joker (configurable)


class DSGroupID(int, Enum):
    """digitalSTROM group IDs."""
    
    LIGHTS = 1
    BLINDS = 2
    HEATING = 3
    AUDIO = 4
    VIDEO = 5
    JOKER = 8
    COOLING = 9
    VENTILATION = 10
    WINDOW = 11
    RECIRCULATION = 12
    TEMPERATURE_CONTROL = 48
    APARTMENT_VENTILATION = 64


class DSPrimaryChannel(str, Enum):
    """Primary channel types for digitalSTROM device groups."""
    
    BRIGHTNESS = "brightness"
    SHADE_POSITION_OUTSIDE = "shade_position_outside"
    HEATING_POWER = "heating_power"
    COOLING_POWER = "cooling_power"
    AIRFLOW_INTENSITY = "airflow_intensity"
    AUDIO_VOLUME = "audio_volume"


class DeviceClass(NamedTuple):
    """Device class definition for digitalSTROM."""
    
    group_id: int
    name: str
    color: DSColor
    applications: tuple[str, ...]
    primary_channel: DSPrimaryChannel | None
    description: str


# Complete list of digitalSTROM device classes
DEVICE_CLASSES = {
    DSGroupID.LIGHTS: DeviceClass(
        group_id=1,
        name="Lights",
        color=DSColor.YELLOW,
        applications=(
            "Room lights",
            "Garden lights",
            "Building illuminations",
        ),
        primary_channel=DSPrimaryChannel.BRIGHTNESS,
        description="Lighting devices including room lights, garden lights, and building illuminations",
    ),
    DSGroupID.BLINDS: DeviceClass(
        group_id=2,
        name="Blinds",
        color=DSColor.GRAY,
        applications=(
            "Blinds",
            "Shades",
            "Awnings",
            "Curtains",
        ),
        primary_channel=DSPrimaryChannel.SHADE_POSITION_OUTSIDE,
        description="Shade and blind control devices",
    ),
    DSGroupID.HEATING: DeviceClass(
        group_id=3,
        name="Heating",
        color=DSColor.BLUE,
        applications=("Heating",),
        primary_channel=DSPrimaryChannel.HEATING_POWER,
        description="Heating devices and controls",
    ),
    DSGroupID.AUDIO: DeviceClass(
        group_id=4,
        name="Audio",
        color=DSColor.CYAN,
        applications=(
            "Music",
            "Radio",
        ),
        primary_channel=DSPrimaryChannel.AUDIO_VOLUME,
        description="Audio playback devices",
    ),
    DSGroupID.VIDEO: DeviceClass(
        group_id=5,
        name="Video",
        color=DSColor.MAGENTA,
        applications=(
            "TV",
            "Video",
        ),
        # Video devices use AUDIO_VOLUME per digitalSTROM spec
        primary_channel=DSPrimaryChannel.AUDIO_VOLUME,
        description="Video and TV devices",
    ),
    DSGroupID.JOKER: DeviceClass(
        group_id=8,
        name="Joker",
        color=DSColor.BLACK,
        applications=("Configurable",),
        primary_channel=None,  # No primary channel - configurable
        description="Configurable devices that can be assigned to different functions",
    ),
    DSGroupID.COOLING: DeviceClass(
        group_id=9,
        name="Cooling",
        color=DSColor.BLUE,
        applications=("Cooling",),
        primary_channel=DSPrimaryChannel.COOLING_POWER,
        description="Cooling and air conditioning devices",
    ),
    DSGroupID.VENTILATION: DeviceClass(
        group_id=10,
        name="Ventilation",
        color=DSColor.BLUE,
        applications=("Ventilation",),
        primary_channel=DSPrimaryChannel.AIRFLOW_INTENSITY,
        description="Ventilation and air circulation devices",
    ),
    DSGroupID.WINDOW: DeviceClass(
        group_id=11,
        name="Window",
        color=DSColor.BLUE,
        applications=("Windows", "Window control"),
        primary_channel=None,  # Windows are typically binary (open/closed)
        description="Window control and monitoring devices",
    ),
    DSGroupID.RECIRCULATION: DeviceClass(
        group_id=12,
        name="Recirculation",
        color=DSColor.BLUE,
        applications=(
            "Ceiling fan",
            "Fan coil units",
        ),
        primary_channel=DSPrimaryChannel.AIRFLOW_INTENSITY,
        description="Recirculation fans and fan coil units",
    ),
    DSGroupID.TEMPERATURE_CONTROL: DeviceClass(
        group_id=48,
        name="Temperature Control",
        color=DSColor.BLUE,
        applications=("Single room temperature control",),
        primary_channel=None,  # Temperature control is special
        description="Single room temperature control devices",
    ),
    DSGroupID.APARTMENT_VENTILATION: DeviceClass(
        group_id=64,
        name="Apartment Ventilation",
        color=DSColor.BLUE,
        applications=("Ventilation system",),
        primary_channel=DSPrimaryChannel.AIRFLOW_INTENSITY,
        description="Apartment-wide ventilation system",
    ),
}


# Additional color groups defined in the specification but not mapped to specific group IDs
ADDITIONAL_COLOR_GROUPS = {
    DSColor.RED: {
        "name": "Security",
        "applications": ("Alarms", "Fire", "Panic"),
        "description": "Security-related functions and alarms",
    },
    DSColor.GREEN: {
        "name": "Access",
        "applications": ("Doors", "Door bells", "Access control"),
        "description": "Access control and door management",
    },
    DSColor.WHITE: {
        "name": "Single Devices",
        "applications": (
            "Refrigerator",
            "Vacuum cleaner",
            "Coffee maker",
            "Water kettle",
            "Cooker hood",
        ),
        "description": "Single devices that don't fit into standard application categories",
    },
}


def get_device_class(group_id: int) -> DeviceClass | None:
    """Get device class by group ID.
    
    Args:
        group_id: The digitalSTROM group ID
        
    Returns:
        DeviceClass if found, None otherwise
    """
    try:
        return DEVICE_CLASSES.get(DSGroupID(group_id))
    except ValueError:
        return None


def get_device_classes_by_color(color: DSColor) -> list[DeviceClass]:
    """Get all device classes for a specific color group.
    
    Args:
        color: The digitalSTROM color
        
    Returns:
        List of device classes matching the color
    """
    return [dc for dc in DEVICE_CLASSES.values() if dc.color == color]


def get_all_device_classes() -> list[DeviceClass]:
    """Get all device classes.
    
    Returns:
        List of all device classes
    """
    return list(DEVICE_CLASSES.values())
