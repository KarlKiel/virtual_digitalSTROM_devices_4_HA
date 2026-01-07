# vDC Property Element Hierarchy - Complete Structure

This document explains the complete hierarchical property element structure as defined in the vDC-API-properties specification (July 2022).

## Key Concept: Everything is Property Elements

The fundamental insight is that **everything** in the vDC specification is structured as property elements at every level. This creates a deeply nested hierarchy where:

- Each level contains property elements
- Property elements can contain lists of property elements
- This pattern repeats all the way down

## Complete Hierarchy

### Level 1: vDC (Integration)

The top level is the **Virtual Device Connector (vDC)**, which represents the integration in Home Assistant.

```
vDC
├── Common Properties (Chapter 2)
│   ├── dSUID (required)
│   ├── displayId (required)
│   ├── type = "vDC" (required)
│   ├── model (required)
│   ├── modelVersion (required)
│   ├── modelUID (required)
│   ├── hardwareVersion (optional)
│   ├── ... (other common properties)
│   └── name (optional)
│
└── vDC Properties (Chapter 3)
    ├── capabilities (property element)
    │   ├── metering (boolean)
    │   ├── identification (boolean)
    │   └── dynamicDefinitions (boolean)
    ├── zoneID (optional)
    ├── implementationId (optional)
    └── x-p44-vdcs: list[vdSD property elements] ← KEY: List of devices
```

**Important**: The `capabilities` or device list property contains **list[vdSD property elements]**, where each element is a complete vdSD property tree.

### Level 2: vdSD (Virtual Device)

Each vdSD (virtual digitalSTROM device) in the vDC's capabilities list is itself a property element tree:

```
vdSD (property element in vDC.capabilities)
├── Common Properties (Chapter 2)
│   ├── dSUID (required)
│   ├── displayId (required)
│   ├── type = "vdSD" (required)
│   ├── model (required)
│   ├── modelVersion (required)
│   ├── modelUID (required)
│   └── ... (other common properties)
│
└── vdSD Properties (Chapter 4)
    ├── General Device Properties (4.1.1)
    │   ├── primaryGroup (required)
    │   ├── zoneID (required)
    │   ├── progMode (optional)
    │   ├── modelFeatures: property element
    │   ├── currentConfigId (optional)
    │   └── configurations: list[configuration property elements] ← KEY
    │
    ├── Button Inputs (4.2): list[button input property elements]
    ├── Binary Inputs (4.3): list[binary input property elements]
    ├── Sensor Inputs (4.4): list[sensor input property elements]
    ├── Device Actions (4.5): list[action property elements]
    ├── Device States (4.6): list[state property elements]
    ├── Device Properties (4.6): list[device property elements]
    ├── Device Events (4.7): list[event property elements]
    ├── Output (4.8): output property element
    ├── Channels (4.9): list[channel property elements]
    ├── Scenes (4.10): list[scene property elements]
    └── Control Values (4.11): list[control value property elements]
```

**Important**: The `configurations` property contains **list[configuration property elements]**, where each configuration describes which inputs/outputs/scenes are active.

### Level 3: Configuration (Property Element)

Each configuration in `vdSD.configurations` is a property element that defines a device profile:

```
Configuration (property element in vdSD.configurations)
├── id (string) - configuration ID
├── description (string) - human-readable description
├── inputs (Section 4.1.2): property element
│   ├── buttonInputs: list[references to buttonInputDescriptions indices]
│   ├── binaryInputs: list[references to binaryInputDescriptions indices]
│   └── sensorInputs: list[references to sensorInputDescriptions indices]
├── outputs (Section 4.1.3): property element
│   ├── outputId: reference to output
│   └── channels: list[references to channel indices]
└── scenes (Section 4.1.4): property element
    └── sceneList: list[references to scene indices]
```

**Important**: The inputs, outputs, and scenes within a configuration are **references** to the actual property elements defined at the vdSD level (chapters 4.2-4.10).

### Level 4: Input/Output/Scene Property Elements

Each input, output, channel, or scene at the vdSD level is a complete property element with three parts:

#### Button Input (Chapter 4.2)
```
Button Input (property element in vdSD.buttonInputDescriptions)
├── descriptions (Section 4.2.1) - list[property elements]
│   ├── name (required, string)
│   ├── dsIndex (required, integer)
│   ├── supportsLocalKeyMode (required, boolean)
│   ├── buttonID (optional, integer)
│   ├── buttonType (required, enum)
│   └── buttonElementID (required, enum)
├── settings (Section 4.2.2) - list[property elements]
│   ├── group (required, integer)
│   ├── function (required, integer)
│   ├── mode (required, enum)
│   ├── channel (required, integer)
│   ├── setsLocalPriority (required, boolean)
│   └── callsPresent (required, boolean)
└── states (Section 4.2.3) - list[property elements]
    ├── value (required, boolean or null)
    ├── clickType (required, enum)
    ├── age (required, float or null)
    ├── error (required, enum)
    ├── actionId (optional, integer)
    └── actionMode (optional, enum)
```

Similar structures exist for:
- **Binary Inputs** (4.3): descriptions, settings, states
- **Sensor Inputs** (4.4): descriptions, settings, states
- **Channels** (4.9): descriptions, states
- **Scenes** (4.10): scene configurations with channel values
- **Output** (4.8): description, settings, state

## Property Element Structure

Every property element in the vDC hierarchy follows this pattern:

```json
{
  "propertyName": {
    "elementId1": {
      "property1": value,
      "property2": value,
      "nestedProperty": {
        "subElement1": { ... },
        "subElement2": { ... }
      }
    },
    "elementId2": { ... }
  }
}
```

## Serialization for vDC API Messages

When communicating with the digitalSTROM Server (DSS), the entire property tree must be serialized with all levels:

```python
vdc_message = {
    # Common properties (Chapter 2)
    "dSUID": "...",
    "type": "vDC",
    # ... other common props
    
    # vDC properties (Chapter 3)
    "capabilities": { ... },
    "x-p44-vdcs": {
        "0": {  # First vdSD
            # Common properties
            "dSUID": "...",
            "type": "vdSD",
            
            # vdSD properties (Chapter 4)
            "primaryGroup": 1,
            "zoneID": 0,
            "configurations": {
                "default": {  # Configuration property element
                    "id": "default",
                    "inputs": { ... },
                    "outputs": { ... },
                    "scenes": { ... }
                }
            },
            "buttonInputDescriptions": {
                "0": {  # Button input 0
                    "name": "Switch",
                    "dsIndex": 0,
                    # ... other description properties
                }
            },
            "buttonInputSettings": {
                "0": {  # Settings for button 0
                    "group": 1,
                    "function": 0,
                    # ... other setting properties
                }
            },
            "buttonInputStates": {
                "0": {  # States for button 0
                    "value": false,
                    "clickType": 255,
                    # ... other state properties
                }
            },
            # ... other inputs, output, channels, scenes
        },
        "1": { ... }  # Second vdSD
    }
}
```

## Implementation Strategy

### Current State
- `models/vdc_entity.py`: vDC level structure (Chapter 2 + 3)
- `models/property_tree.py`: Configuration level (Sections 4.1.2-4.1.4) - simplified
- `models/virtual_device.py`: Simplified vdSD for HA storage
- `docs/external/vdc_properties.py`: Complete property definitions

### Required for Full Compliance
1. **vdSD Property Element Builder**: Convert VirtualDevice to complete property element tree
2. **Input/Output/Scene Builders**: Create proper property elements for chapters 4.2-4.10
3. **Message Serializer**: Convert entire vDC tree to vDC API format
4. **Property Tree Navigator**: Query and update nested properties
5. **Validation**: Ensure all required properties are present at each level

## Example: Complete Property Tree

For a simple light device with one button:

```python
vdc = {
    "dSUID": "vDC_dSUID_here",
    "type": "vDC",
    "model": "HA Virtual vDC",
    "modelVersion": "1.0",
    "modelUID": "homeassistant.vdc.1.0",
    "name": "Virtual digitalSTROM Devices",
    "capabilities": {
        "metering": False,
        "identification": True,
        "dynamicDefinitions": True
    },
    "x-p44-vdcs": {
        "0": {  # Light device
            "dSUID": "device_dSUID_here",
            "type": "vdSD",
            "model": "LED Dimmer",
            "modelVersion": "1.0",
            "modelUID": "led.dimmer.1.0",
            "name": "Living Room Light",
            "primaryGroup": 1,
            "zoneID": 0,
            "modelFeatures": {
                "dimmable": True
            },
            "configurations": {
                "default": {
                    "id": "default",
                    "description": "Default configuration",
                    "inputs": {
                        "buttonInputs": {"0": 0}  # References buttonInputDescriptions[0]
                    },
                    "outputs": {
                        "outputId": 0,
                        "channels": {"0": 0}  # References channels[0]
                    },
                    "scenes": {
                        "0": 0, "1": 1, "2": 2, "3": 3, "4": 4  # Scene references
                    }
                }
            },
            "buttonInputDescriptions": {
                "0": {
                    "name": "Wall Switch",
                    "dsIndex": 0,
                    "supportsLocalKeyMode": True,
                    "buttonType": 1,  # single pushbutton
                    "buttonElementID": 0
                }
            },
            "buttonInputSettings": {
                "0": {
                    "group": 1,
                    "function": 0,
                    "mode": 0,
                    "channel": 0,
                    "setsLocalPriority": False,
                    "callsPresent": False
                }
            },
            "buttonInputStates": {
                "0": {
                    "value": False,
                    "clickType": 255,
                    "age": 0.0,
                    "error": 0
                }
            },
            "outputDescription": {
                "outputFunction": 1,  # dimmer
                "outputUsage": 0,
                "variableRamp": True,
                "maxPower": 60.0
            },
            "outputSettings": {
                "mode": 0,
                "pushChangesToDevice": True
            },
            "outputState": {
                "value": 0.0,
                "targetValue": 0.0
            },
            "channelDescriptions": {
                "0": {
                    "channelType": 0,  # brightness
                    "dsIndex": 0,
                    "siunit": "percent",
                    "min": 0.0,
                    "max": 100.0,
                    "resolution": 1.0
                }
            },
            "channelStates": {
                "0": {
                    "value": 0.0,
                    "age": 0.0
                }
            },
            "scenes": {
                "0": {  # Off scene
                    "sceneNo": 0,
                    "sceneName": "Off",
                    "sceneChannels": {
                        "0": {"value": 0.0}
                    }
                },
                "1": {  # Preset 1
                    "sceneNo": 1,
                    "sceneName": "Preset 1",
                    "sceneChannels": {
                        "0": {"value": 100.0}
                    }
                }
                # ... more scenes
            }
        }
    }
}
```

## Summary

The vDC specification defines a completely hierarchical structure where:
1. vDC contains list[vdSD property elements]
2. Each vdSD contains list[configuration property elements] + list[input/output/scene property elements]
3. Each configuration references which inputs/outputs/scenes are active
4. Each input/output/scene has descriptions, settings, and states as property elements

This structure allows flexible device profiles and dynamic reconfiguration while maintaining a consistent property element pattern throughout.
