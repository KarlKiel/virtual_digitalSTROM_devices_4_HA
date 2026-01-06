# Virtual Device Creation UI Flow

This document describes the user interface flow for creating virtual digitalSTROM devices (vdsd) within the Home Assistant integration.

## Overview

The integration supports creating virtual devices through a multi-step configuration flow. The flow intelligently determines whether to set up the integration for the first time or to create a new virtual device.

## User Flow

### First-Time Setup

When adding the integration for the first time (clicking "Add Integration" in Home Assistant):

1. **Integration Setup Screen**
   - User is presented with basic integration configuration
   - Fields:
     - **Name**: Name for the integration (default: "Virtual digitalSTROM Devices")
     - **DSS Port**: TCP port for the digitalSTROM Server (default: 8440)
   - After completion, the integration is set up and ready to create devices

### Creating a New Virtual Device

When adding a new entry after the integration is already set up (clicking "Add Entry" button):

1. **Device Category Selection Screen**
   - Title: "Create Virtual digitalSTROM Device"
   - User selects the device category based on digitalSTROM color groups
   - Each category has a descriptive label explaining its purpose

## Color Group Categories

The following categories are available, based on the digitalSTROM specification:

| Color   | Category          | Description                                          |
|---------|-------------------|------------------------------------------------------|
| Yellow  | Lights            | All lighting devices                                 |
| Gray    | Blinds            | Shading and blind control                            |
| Blue    | Climate           | Heating, cooling, ventilation, windows               |
| Cyan    | Audio             | Audio playback devices                               |
| Magenta | Video             | TV and video devices                                 |
| Red     | Security          | Alarms, fire, panic systems                          |
| Green   | Access            | Doors, doorbells, access control                     |
| White   | Single Devices    | Individual appliances (fridge, coffee maker)         |
| Black   | Joker             | Configurable/customizable devices                    |

## Implementation Details

### Files Modified

1. **config_flow.py**
   - Added `COLOR_GROUP_OPTIONS` dictionary with all color group categories
   - Implemented `async_step_user()` to route between integration setup and device creation
   - Added `async_step_integration_setup()` for first-time integration configuration
   - Added `async_step_device_category()` for device category selection

2. **strings.json** and **translations/en.json**
   - Added UI strings for the device category selection step
   - Included detailed descriptions for each color group category
   - Maintained existing integration setup strings

### Logic Flow

```
User clicks "Add Entry"
       ↓
async_step_user()
       ↓
   [Check existing entries]
       ↓
   ┌────────────────────┐
   │                    │
   ▼                    ▼
No entries        Has entries
   │                    │
   ▼                    ▼
integration_setup  device_category
   │                    │
   ▼                    ▼
Create Integration  Create Device Entry
   Entry           (with category)
```

## Future Extensions

The current implementation stops at category selection. Future steps will include:

1. Device-specific configuration based on the selected category
2. Entity mapping to Home Assistant entities
3. Device naming and customization
4. Advanced property configuration

## Related Documentation

- [DEVICE_CLASSES.md](DEVICE_CLASSES.md) - Complete device class documentation
- [device_classes.py](device_classes.py) - Device class implementation
- [const.py](const.py) - Constants including DSColor enum

## Testing

To test the UI flow:

1. Install the integration in Home Assistant
2. Go to Settings → Devices & Services
3. Click "+ Add Integration"
4. Search for "Virtual digitalSTROM Devices"
5. Complete the integration setup
6. Click "Add Entry" on the integration card
7. Select a device category from the dropdown

The category selection screen should display all nine color group options with descriptive labels.
