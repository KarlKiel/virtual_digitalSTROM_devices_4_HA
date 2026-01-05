# digitalSTROM Device Classes

This document provides a comprehensive overview of all device classes supported by the digitalSTROM system, as extracted from the `ds-basics.pdf` specification.

## Overview

digitalSTROM organizes devices into **Application Groups** based on their function. Each group is identified by:
- A unique **Group ID**
- A **Color** for easy visual identification
- A **Primary Channel** type for control
- A set of **Applications** that belong to the group

## Color Groups

digitalSTROM uses colors to categorize different types of devices:

| Color   | Category          | Description                                  |
|---------|-------------------|----------------------------------------------|
| Yellow  | Lights            | All lighting devices                         |
| Gray    | Blinds            | Shading and blind control                    |
| Blue    | Climate           | Heating, cooling, ventilation, windows       |
| Cyan    | Audio             | Audio playback devices                       |
| Magenta | Video             | TV and video devices                         |
| Red     | Security          | Alarms, fire, panic systems                  |
| Green   | Access            | Doors, doorbells, access control             |
| White   | Single Devices    | Individual appliances (fridge, coffee maker) |
| Black   | Joker             | Configurable/customizable devices            |

## Device Classes

### 1. Lights (Yellow)
- **Group ID:** 1
- **Color:** Yellow
- **Primary Channel:** Brightness
- **Applications:**
  - Room lights
  - Garden lights
  - Building illuminations

### 2. Blinds (Gray)
- **Group ID:** 2
- **Color:** Gray
- **Primary Channel:** Shade Position Outside
- **Applications:**
  - Blinds
  - Shades
  - Awnings
  - Curtains

### 3. Heating (Blue)
- **Group ID:** 3
- **Color:** Blue
- **Primary Channel:** Heating Power
- **Applications:**
  - Heating systems

### 4. Audio (Cyan)
- **Group ID:** 4
- **Color:** Cyan
- **Primary Channel:** Audio Volume
- **Applications:**
  - Music players
  - Radio

### 5. Video (Magenta)
- **Group ID:** 5
- **Color:** Magenta
- **Primary Channel:** Audio Volume
- **Applications:**
  - TV
  - Video players

### 6. Joker (Black)
- **Group ID:** 8
- **Color:** Black
- **Primary Channel:** None (configurable)
- **Applications:**
  - Configurable devices
  
**Note:** Joker devices are customizable and can be assigned to different functions based on user needs.

### 7. Cooling (Blue)
- **Group ID:** 9
- **Color:** Blue
- **Primary Channel:** Cooling Power
- **Applications:**
  - Cooling systems
  - Air conditioning

### 8. Ventilation (Blue)
- **Group ID:** 10
- **Color:** Blue
- **Primary Channel:** Airflow Intensity
- **Applications:**
  - Ventilation systems

### 9. Window (Blue)
- **Group ID:** 11
- **Color:** Blue
- **Primary Channel:** None (binary: open/closed)
- **Applications:**
  - Windows
  - Window control

### 10. Recirculation (Blue)
- **Group ID:** 12
- **Color:** Blue
- **Primary Channel:** Airflow Intensity
- **Applications:**
  - Ceiling fans
  - Fan coil units

### 11. Temperature Control (Blue)
- **Group ID:** 48
- **Color:** Blue
- **Primary Channel:** None (special)
- **Applications:**
  - Single room temperature control

### 12. Apartment Ventilation (Blue)
- **Group ID:** 64
- **Color:** Blue
- **Primary Channel:** Airflow Intensity
- **Applications:**
  - Apartment-wide ventilation systems

## Additional Color Groups

These color groups are defined in the specification but don't have specific group IDs in the standard mapping:

### Security (Red)
- **Applications:**
  - Alarms
  - Fire detection
  - Panic systems

### Access (Green)
- **Applications:**
  - Doors
  - Door bells
  - Access control systems

### Single Devices (White)
- **Applications:**
  - Refrigerator
  - Vacuum cleaner
  - Coffee maker
  - Water kettle
  - Cooker hood
  - Other individual appliances

**Note:** Single devices typically don't fit into standard application categories and are used as individual appliances rather than room-wide applications.

## Primary Channels

Each device class (except configurable ones) has a primary channel type that defines the default control interface:

| Channel Type              | Description                           | Used By                                        |
|---------------------------|---------------------------------------|------------------------------------------------|
| Brightness                | Light intensity control               | Lights                                         |
| Shade Position Outside    | Blind/shade position                  | Blinds                                         |
| Heating Power             | Heating power level                   | Heating                                        |
| Cooling Power             | Cooling power level                   | Cooling                                        |
| Airflow Intensity         | Air circulation intensity             | Ventilation, Recirculation, Apartment Vent.    |
| Audio Volume              | Volume level                          | Audio, Video                                   |

## Usage in Code

The device classes are available in the `device_classes.py` module:

```python
from custom_components.virtual_digitalstrom_devices.const import (
    DEVICE_CLASSES,
    DSColor,
    DSGroupID,
    get_device_class,
    get_device_classes_by_color,
    get_all_device_classes,
)

# Get a specific device class
lights_class = get_device_class(DSGroupID.LIGHTS)
print(f"Name: {lights_class.name}")
print(f"Color: {lights_class.color.value}")
print(f"Applications: {', '.join(lights_class.applications)}")

# Get all climate (blue) device classes
climate_classes = get_device_classes_by_color(DSColor.BLUE)
for dc in climate_classes:
    print(f"- {dc.name} (ID: {dc.group_id})")

# Get all device classes
all_classes = get_all_device_classes()
print(f"Total device classes: {len(all_classes)}")
```

## References

All information in this document is extracted from the digitalSTROM specification:
- Source: `custom_components/ds-basics.pdf`
- Relevant sections:
  - Section 2.3: Application Types
  - Section 3.2: Groups
  - Table 1: digitalSTROM Colors
  - Table 2: digitalSTROM Application Groups
  - Table 7: Application types and the primary output channel
