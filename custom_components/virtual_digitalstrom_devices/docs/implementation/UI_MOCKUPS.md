# UI Flow Mockups - Virtual Device Creation

This document provides visual mockups of the user interface flow for creating virtual digitalSTROM devices.

## Screen 1: Initial Integration Setup (First Time Only)

**Shown when:** User adds the integration for the first time

```
╔══════════════════════════════════════════════════════════════╗
║  Set up Virtual digitalSTROM Devices                         ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Configure the Virtual digitalSTROM Devices integration     ║
║                                                              ║
║  ┌────────────────────────────────────────────────────┐     ║
║  │ Name *                                             │     ║
║  │ ┌──────────────────────────────────────────────┐   │     ║
║  │ │ Virtual digitalSTROM Devices                 │   │     ║
║  │ └──────────────────────────────────────────────┘   │     ║
║  └────────────────────────────────────────────────────┘     ║
║                                                              ║
║  ┌────────────────────────────────────────────────────┐     ║
║  │ digitalSTROM Server TCP Port *                     │     ║
║  │ ┌──────────────────────────────────────────────┐   │     ║
║  │ │ 8440                                         │   │     ║
║  │ └──────────────────────────────────────────────┘   │     ║
║  └────────────────────────────────────────────────────┘     ║
║                                                              ║
║                                      ┌──────────┐            ║
║                                      │  SUBMIT  │            ║
║                                      └──────────┘            ║
╚══════════════════════════════════════════════════════════════╝
```

## Screen 2: Device Category Selection

**Shown when:** User clicks "Add Entry" after integration is already set up

```
╔══════════════════════════════════════════════════════════════╗
║  Create Virtual digitalSTROM Device                          ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Select the category for your new virtual device. Each      ║
║  category represents a different type of digitalSTROM       ║
║  device with specific functions and capabilities.           ║
║                                                              ║
║  ┌────────────────────────────────────────────────────┐     ║
║  │ Device Category *                                  │     ║
║  │ ┌──────────────────────────────────────────────┐   │     ║
║  │ │ Select category...                       ▼  │   │     ║
║  │ └──────────────────────────────────────────────┘   │     ║
║  └────────────────────────────────────────────────────┘     ║
║                                                              ║
║  Choose the color group that best matches your device type: ║
║                                                              ║
║  • Yellow (Lights) - All lighting devices                   ║
║  • Gray (Blinds) - Shading and blind control                ║
║  • Blue (Climate) - Heating, cooling, ventilation, windows  ║
║  • Cyan (Audio) - Audio playback devices                    ║
║  • Magenta (Video) - TV and video devices                   ║
║  • Red (Security) - Alarms, fire, panic systems             ║
║  • Green (Access) - Doors, doorbells, access control        ║
║  • White (Single Devices) - Individual appliances like      ║
║    fridges and coffee makers                                ║
║  • Black (Joker) - Configurable/customizable devices        ║
║                                                              ║
║                                      ┌──────────┐            ║
║                                      │  SUBMIT  │            ║
║                                      └──────────┘            ║
╚══════════════════════════════════════════════════════════════╝
```

## Screen 3: Category Dropdown Expanded

**Shown when:** User clicks on the category dropdown

```
╔══════════════════════════════════════════════════════════════╗
║  Create Virtual digitalSTROM Device                          ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Select the category for your new virtual device. Each      ║
║  category represents a different type of digitalSTROM       ║
║  device with specific functions and capabilities.           ║
║                                                              ║
║  ┌────────────────────────────────────────────────────┐     ║
║  │ Device Category *                                  │     ║
║  │ ┌──────────────────────────────────────────────┐   │     ║
║  │ │╔════════════════════════════════════════════╗│   │     ║
║  │ │║ yellow                                     ║│   │     ║
║  │ │╠────────────────────────────────────────────╣│   │     ║
║  │ │║ Lights - All lighting devices              ║│   │     ║
║  │ │╠────────────────────────────────────────────╣│   │     ║
║  │ │║ Blinds - Shading and blind control         ║│   │     ║
║  │ │╠────────────────────────────────────────────╣│   │     ║
║  │ │║ Climate - Heating, cooling, ventilation... ║│   │     ║
║  │ │╠────────────────────────────────────────────╣│   │     ║
║  │ │║ Audio - Audio playback devices             ║│   │     ║
║  │ │╠────────────────────────────────────────────╣│   │     ║
║  │ │║ Video - TV and video devices               ║│   │     ║
║  │ │╠────────────────────────────────────────────╣│   │     ║
║  │ │║ Security - Alarms, fire, panic systems     ║│   │     ║
║  │ │╠────────────────────────────────────────────╣│   │     ║
║  │ │║ Access - Doors, doorbells, access control  ║│   │     ║
║  │ │╠────────────────────────────────────────────╣│   │     ║
║  │ │║ Single Devices - Individual appliances...  ║│   │     ║
║  │ │╠────────────────────────────────────────────╣│   │     ║
║  │ │║ Joker - Configurable/customizable devices  ║│   │     ║
║  │ │╚════════════════════════════════════════════╝│   │     ║
║  │ └──────────────────────────────────────────────┘   │     ║
║  └────────────────────────────────────────────────────┘     ║
║                                                              ║
║                                      ┌──────────┐            ║
║                                      │  SUBMIT  │            ║
║                                      └──────────┘            ║
╚══════════════════════════════════════════════════════════════╝
```

## Example: Category Selected (Yellow - Lights)

```
╔══════════════════════════════════════════════════════════════╗
║  Create Virtual digitalSTROM Device                          ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Select the category for your new virtual device. Each      ║
║  category represents a different type of digitalSTROM       ║
║  device with specific functions and capabilities.           ║
║                                                              ║
║  ┌────────────────────────────────────────────────────┐     ║
║  │ Device Category *                                  │     ║
║  │ ┌──────────────────────────────────────────────┐   │     ║
║  │ │ Lights - All lighting devices            ▼  │   │     ║
║  │ └──────────────────────────────────────────────┘   │     ║
║  └────────────────────────────────────────────────────┘     ║
║                                                              ║
║  Choose the color group that best matches your device type: ║
║                                                              ║
║  • Yellow (Lights) - All lighting devices                   ║
║  • Gray (Blinds) - Shading and blind control                ║
║  • Blue (Climate) - Heating, cooling, ventilation, windows  ║
║  • Cyan (Audio) - Audio playback devices                    ║
║  • Magenta (Video) - TV and video devices                   ║
║  • Red (Security) - Alarms, fire, panic systems             ║
║  • Green (Access) - Doors, doorbells, access control        ║
║  • White (Single Devices) - Individual appliances like      ║
║    fridges and coffee makers                                ║
║  • Black (Joker) - Configurable/customizable devices        ║
║                                                              ║
║                                      ┌──────────┐            ║
║                                      │  SUBMIT  │  ← Active  ║
║                                      └──────────┘            ║
╚══════════════════════════════════════════════════════════════╝
```

## Key UI Features

### Color Group Options

The dropdown presents all 9 digitalSTROM color groups:

1. **yellow** → "Lights - All lighting devices"
2. **gray** → "Blinds - Shading and blind control"
3. **blue** → "Climate - Heating, cooling, ventilation, windows"
4. **cyan** → "Audio - Audio playback devices"
5. **magenta** → "Video - TV and video devices"
6. **red** → "Security - Alarms, fire, panic systems"
7. **green** → "Access - Doors, doorbells, access control"
8. **white** → "Single Devices - Individual appliances (fridge, coffee maker)"
9. **black** → "Joker - Configurable/customizable devices"

### User Experience

1. **Clear category descriptions**: Each option in the dropdown includes both the category name and a brief description
2. **Helpful guidance**: The description text explains what each color group represents
3. **Simple selection**: Single dropdown makes it easy to choose the appropriate category
4. **Validation**: The category field is required (marked with *)

### Future Steps (Not Yet Implemented)

After category selection and submission, future steps will include:
- Device-specific configuration options based on selected category
- Device naming
- Entity mapping to Home Assistant entities
- Advanced property configuration

## Technical Implementation

The dropdown values come from the `COLOR_GROUP_OPTIONS` dictionary in `config_flow.py`:

```python
COLOR_GROUP_OPTIONS = {
    DSColor.YELLOW.value: "Lights - All lighting devices",
    DSColor.GRAY.value: "Blinds - Shading and blind control",
    DSColor.BLUE.value: "Climate - Heating, cooling, ventilation, windows",
    DSColor.CYAN.value: "Audio - Audio playback devices",
    DSColor.MAGENTA.value: "Video - TV and video devices",
    DSColor.RED.value: "Security - Alarms, fire, panic systems",
    DSColor.GREEN.value: "Access - Doors, doorbells, access control",
    DSColor.WHITE.value: "Single Devices - Individual appliances (fridge, coffee maker)",
    DSColor.BLACK.value: "Joker - Configurable/customizable devices",
}
```

The selected category value (e.g., "yellow", "blue") is stored in the config entry data for use in subsequent configuration steps.
