# vDC Device Properties - Quick Reference Tree

This is a visual reference showing the complete hierarchical structure of all vDC device properties.

## Legend
- **[R]** = Required property
- **[O]** = Optional property
- **[0..N]** = Array/list of elements indexed 0 to N-1

---

## Complete Property Tree

```
VirtualDevice
│
├─ Common Properties for All Addressable Entities (vDC Spec Section 2)
│  ├─ dSUID [R] (string, 34 hex chars)
│  ├─ displayId [R] (string) - human-readable identification on physical device
│  ├─ type [R] (string) - "vdSD", "vDC", "vDChost", or "vdSM"
│  ├─ model [R] (string) - human-readable model string
│  ├─ modelVersion [R] (string) - model version (firmware version)
│  ├─ modelUID [R] (string) - digitalSTROM system unique ID for functional model
│  ├─ hardwareVersion [O] (string) - hardware version string
│  └─ hardwareGuid [O] (string) - hardware GUID in URN format
│
├─ General Device Properties (vDC Spec Section 4.1.1)
│  ├─ primaryGroup [R] (integer, dS class number)
│  ├─ zoneID [R] (integer, global dS Zone ID)
│  ├─ progMode [O] (boolean)
│  ├─ modelFeatures [R] (dict of feature_name: boolean)
│  ├─ currentConfigId [O] (string)
│  └─ configurations [R] (list of config IDs)
│
├─ Button Inputs [O] [0..N]
│  ├─ buttonInputDescriptions[i]
│  │  ├─ name [R] (string)
│  │  ├─ dsIndex [R] (integer, 0..N-1)
│  │  ├─ supportsLocalKeyMode [R] (boolean)
│  │  ├─ buttonID [O] (integer)
│  │  ├─ buttonType [R] (enum: 0-6)
│  │  └─ buttonElementID [R] (enum: 0-8)
│  │
│  ├─ buttonInputSettings[i]
│  │  ├─ group [R] (integer)
│  │  ├─ function [R] (integer, 0..15)
│  │  ├─ mode [R] (enum: 0,2,5-12,255)
│  │  ├─ channel [R] (integer, 0 or 1..239)
│  │  ├─ setsLocalPriority [R] (boolean)
│  │  └─ callsPresent [R] (boolean)
│  │
│  └─ buttonInputStates[i]
│     ├─ value [R] (boolean or null)
│     ├─ clickType [R] (enum: 0-14,255)
│     ├─ age [R] (float or null)
│     ├─ error [R] (enum: 0-6)
│     ├─ actionId [O] (integer) - alternative for scene calls
│     └─ actionMode [O] (enum: 0-2) - alternative for scene calls
│
├─ Binary Inputs [O] [0..N]
│  ├─ binaryInputDescriptions[i]
│  │  ├─ name [R] (string)
│  │  ├─ dsIndex [R] (integer, 0..N-1)
│  │  ├─ inputType [R] (enum: 0-1)
│  │  ├─ inputUsage [R] (enum: 0-3)
│  │  ├─ sensorFunction [R] (enum: 0,12)
│  │  └─ updateInterval [R] (float, seconds)
│  │
│  ├─ binaryInputSettings[i]
│  │  ├─ group [R] (integer)
│  │  └─ sensorFunction [R] (enum: 0-23)
│  │
│  └─ binaryInputStates[i]
│     ├─ value [R] (boolean or null)
│     ├─ extendedValue [O] (integer or null)
│     ├─ age [R] (float or null)
│     └─ error [R] (enum: 0-6)
│
├─ Sensor Inputs [O] [0..N]
│  ├─ sensorDescriptions[i]
│  │  ├─ name [R] (string)
│  │  ├─ dsIndex [R] (integer, 0..N-1)
│  │  ├─ sensorType [R] (enum: 0-28)
│  │  │  (0:none, 1:temp, 2:humidity, 3:lux, 14:power, 22:CO2, etc.)
│  │  ├─ sensorUsage [R] (enum: 0-6)
│  │  ├─ min [R] (float)
│  │  ├─ max [R] (float)
│  │  ├─ resolution [R] (float)
│  │  ├─ updateInterval [R] (float, seconds)
│  │  └─ aliveSignInterval [R] (float, seconds)
│  │
│  ├─ sensorSettings[i]
│  │  ├─ group [R] (integer)
│  │  ├─ minPushInterval [R] (float, default: 2.0)
│  │  └─ changesOnlyInterval [R] (float, default: 0.0)
│  │
│  └─ sensorStates[i]
│     ├─ value [R] (float or null)
│     ├─ age [R] (float or null)
│     ├─ contextId [O] (integer or null)
│     ├─ contextMsg [O] (string or null)
│     └─ error [R] (enum: 0-6)
│
├─ Device Actions [O]
│  ├─ deviceActionDescriptions [O] [by name]
│  │  ├─ name [R] (string)
│  │  ├─ params [O] (list of ParameterDescription)
│  │  │  ├─ type [R] (string: 'numeric'/'enumeration'/'string')
│  │  │  ├─ min [O] (float)
│  │  │  ├─ max [O] (float)
│  │  │  ├─ resolution [O] (float)
│  │  │  ├─ siunit [O] (string)
│  │  │  ├─ options [O] (dict)
│  │  │  └─ default [O] (float/string/int)
│  │  └─ description [O] (string)
│  │
│  ├─ standardActions [O] [by name with "std." prefix]
│  │  ├─ name [R] (string)
│  │  ├─ action [R] (string)
│  │  └─ params [O] (dict)
│  │
│  ├─ customActions [O] [by name with "custom." prefix]
│  │  ├─ name [R] (string)
│  │  ├─ action [R] (string)
│  │  ├─ title [R] (string)
│  │  └─ params [O] (dict)
│  │
│  └─ dynamicDeviceActions [O] [by name with "dynamic." prefix]
│     ├─ name [R] (string)
│     └─ title [R] (string)
│
├─ Device States [O]
│  ├─ deviceStateDescriptions [O] [by name]
│  │  ├─ name [R] (string)
│  │  ├─ options [R] (dict of id:value pairs)
│  │  └─ description [O] (string)
│  │
│  └─ deviceStates [O] [by name]
│     ├─ name [R] (string)
│     └─ value [R] (string)
│
├─ Device Properties [O]
│  ├─ devicePropertyDescriptions [O] [by name]
│  │  ├─ name [R] (string)
│  │  ├─ type [R] (string: 'numeric'/'enumeration'/'string')
│  │  ├─ min [O] (float)
│  │  ├─ max [O] (float)
│  │  ├─ resolution [O] (float)
│  │  ├─ siunit [O] (string)
│  │  ├─ options [O] (dict)
│  │  └─ default [O] (float/string/int)
│  │
│  └─ deviceProperties [O] [by name]
│     ├─ name [R] (string)
│     └─ value [R] (string/float/int/bool)
│
├─ Device Events [O]
│  └─ deviceEventDescriptions [O] [by name]
│     ├─ name [R] (string)
│     └─ description [O] (string)
│
├─ Output [O] (single output per device)
│  ├─ outputDescription [O]
│  │  ├─ defaultGroup [R] (integer)
│  │  ├─ name [R] (string)
│  │  ├─ function [R] (enum: 0-6)
│  │  │  (0:on/off, 1:dimmer, 2:positional, 3:dimmer+ct, 4:full color, 5:bipolar, 6:internal)
│  │  ├─ outputUsage [R] (enum: 0-3)
│  │  ├─ variableRamp [R] (boolean)
│  │  ├─ maxPower [O] (float, Watts)
│  │  └─ activeCoolingMode [O] (boolean)
│  │
│  ├─ outputSettings [O]
│  │  ├─ activeGroup [R] (integer)
│  │  ├─ groups [R] (dict of group_id:boolean, 1..63)
│  │  ├─ mode [R] (enum: 0,1,2,127)
│  │  ├─ pushChanges [R] (boolean)
│  │  ├─ onThreshold [O] (float, 0..100%, default: 50)
│  │  ├─ minBrightness [O] (float, 0..100%)
│  │  ├─ dimTimeUp [O] (integer, dS 8-bit format)
│  │  ├─ dimTimeDown [O] (integer, dS 8-bit format)
│  │  ├─ dimTimeUpAlt1 [O] (integer)
│  │  ├─ dimTimeDownAlt1 [O] (integer)
│  │  ├─ dimTimeUpAlt2 [O] (integer)
│  │  ├─ dimTimeDownAlt2 [O] (integer)
│  │  ├─ heatingSystemCapability [O] (enum: 1-3)
│  │  └─ heatingSystemType [O] (enum: 0-6)
│  │
│  └─ outputState [O]
│     ├─ localPriority [R] (boolean)
│     └─ error [R] (enum: 0-6)
│
├─ Channels [O] [0..N]
│  ├─ channelDescriptions[i]
│  │  ├─ name [R] (string)
│  │  ├─ channelType [R] (integer, channel type ID)
│  │  ├─ dsIndex [R] (integer, 0 is default channel)
│  │  ├─ min [R] (float)
│  │  ├─ max [R] (float)
│  │  └─ resolution [R] (float)
│  │
│  ├─ channelSettings[i]
│  │  └─ (no elements currently defined)
│  │
│  └─ channelStates[i]
│     ├─ value [R] (float)
│     └─ age [R] (float, null if not yet applied)
│
└─ Scenes [O] [0..127]
   └─ scenes[scene_number]
      ├─ channels [R] (dict of channel_type_id: SceneValue)
      │  └─ [channel_type_id]
      │     ├─ value [R] (float)
      │     ├─ dontCare [R] (boolean)
      │     └─ automatic [R] (boolean)
      ├─ effect [R] (enum: 0-4)
      │  (0:no effect, 1:smooth, 2:slow, 3:very slow, 4:blink)
      ├─ dontCare [R] (boolean, scene-global)
      └─ ignoreLocalPriority [R] (boolean)
```

---

## Common Channel Types

Standard output channel types (from ds-basics.pdf):

```
Channel Type ID | Name              | Used For
----------------|-------------------|----------------------------------
0               | Default/Generic   | Generic devices
1               | Brightness        | Lights (0..100%)
2               | Hue               | Color lights (0..360°)
3               | Saturation        | Color lights (0..100%)
4               | Color Temperature | CT lights (0..100% or Kelvin)
5               | CIE X             | Color lights (CIE color space)
6               | CIE Y             | Color lights (CIE color space)
7               | Shade Position    | Blinds/shades (0..100%)
8               | Shade Angle       | Blinds/shades (0..100%)
```

---

## Common Sensor Types

```
Type ID | Sensor Type         | Unit       | Common Usage
--------|---------------------|------------|-------------------------
1       | Temperature         | °C         | Room/outdoor temp
2       | Humidity            | %          | Relative humidity
3       | Illumination        | lux        | Light level
14      | Active Power        | W          | Power consumption
16      | Energy Meter        | kWh        | Energy consumed
18      | Air Pressure        | hPa        | Barometric pressure
22      | CO2                 | ppm        | Air quality
```

---

## Common Scene Numbers

Standard digitalSTROM scene numbers:

```
Scene # | Name            | Description
--------|-----------------|----------------------------------------
0       | Off             | Turn off
1       | Preset 1        | User preset 1 (typically 75%)
2       | Preset 2        | User preset 2 (typically 50%)
3       | Preset 3        | User preset 3 (typically 25%)
4       | Preset 4        | User preset 4 (typically 10%)
5       | Deep Off        | Deep off with transition
17      | Auto Standby    | Automatic standby mode
18      | Standby         | Standby mode
69      | Panic           | Panic/alarm state
72      | Energy          | Energy saving preset
```

---

## Common dS Groups (Primary Groups)

```
Group # | Name       | Color  | Typical Devices
--------|------------|--------|--------------------------------
0       | Generic    | Black  | Sensors, switches
1       | Light      | Yellow | Lights, dimmers
2       | Climate    | Blue   | Heating, cooling, ventilation
3       | Audio      | Cyan   | Audio devices
4       | Video      | Magenta| TV, projectors
5       | Security   | Red    | Security, access control
8       | Joker      | White  | Multi-function devices
9       | Cooling    | Blue   | Air conditioning
10      | Ventilation| Blue   | Fans, ventilation
11      | Window     | Blue   | Window controls
12      | Recirculation| Blue | Recirculation systems
48      | Temperature Control | Blue | Temperature controllers
```

---

## Property Access Modes

```
r    = Read-only (can be queried via getProperty)
r/w  = Read/Write (can be queried and modified via getProperty/setProperty)
w    = Write-only (can only be set via setControlValue)
```

---

## Error Codes (Common to all inputs/outputs)

```
Code | Name                      | Description
-----|---------------------------|----------------------------------
0    | OK                        | No error
1    | OPEN_CIRCUIT             | Open circuit / lamp broken
2    | SHORT_CIRCUIT            | Short circuit
3    | OVERLOAD                 | Overload
4    | BUS_CONNECTION_PROBLEM   | Bus connection problem
5    | LOW_BATTERY              | Low battery in device
6    | OTHER_DEVICE_ERROR       | Other device error
```

---

## Python Class Mapping

```
Python Class                    → Property Tree Location
--------------------------------|----------------------------------
VirtualDevice                   | Root device object
DeviceProperties                | General device properties
ButtonInput                     | buttonInputDescriptions/Settings/States[i]
  ├─ ButtonInputDescription     |   ├─ Descriptions
  ├─ ButtonInputSettings        |   ├─ Settings
  └─ ButtonInputState           |   └─ States
BinaryInput                     | binaryInputDescriptions/Settings/States[i]
SensorInput                     | sensorDescriptions/Settings/States[i]
Output                          | outputDescription/Settings/State
  ├─ OutputDescription          |   ├─ Description
  ├─ OutputSettings             |   ├─ Settings
  └─ OutputState                |   └─ State
Channel                         | channelDescriptions/States[i]
Scene                           | scenes[scene_number]
  └─ SceneValue                 |   └─ channels[channel_type_id]
```

---

## Usage Example (Minimal)

```python
from vdc_properties import *

# Create device
device = VirtualDevice(
    ds_uid="0123456789ABCDEF0123456789ABCDEF01",
    properties=DeviceProperties(
        primary_group=1,  # Light
        zone_id=0,
        model_features={"dimmable": True},
        configurations=["default"],
    ),
)

# Add button
device.add_button_input(create_pushbutton("Switch", 0, 1))

# Add output with channel
device.output = create_dimmer_output("Light", 1)
device.add_channel(create_brightness_channel(0, 0.0))

# Add scene
device.add_scene(Scene(1, {1: SceneValue(75.0)}))

# Convert to dict for JSON
data = device.to_dict()
```

---

For complete examples and detailed usage, see **VDC_PROPERTIES_USAGE.md**
