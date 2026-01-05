# vDC Device Properties - Complete Property Subtrees List

This document lists all possible property subtrees with their respective elements for Virtual digitalSTROM Device (vdSD) properties as defined in Chapter 4 of the vDC-API-properties_JULY 2022.pdf document.

## Overview

The vDC (Virtual Device Connector) API defines a hierarchical property structure for virtual digitalSTROM devices (vdSD). All vdSDs must support the basic set of common properties, plus device-specific properties organized into various subtrees.

### Legend

- **[REQUIRED]**: Property must be supported by all implementations
- **[OPTIONAL]**: Property may or may not be available depending on implementation or device type
- **Access modes**: r = read-only, r/w = read/write, w = write-only

---

## 1. General Device Properties (Section 4.1.1)

### 1.1 `primaryGroup` **[REQUIRED]**
- **Access**: Read-only (r)
- **Type**: integer, dS class number
- **Description**: Basic class (color) of the device

### 1.2 `zoneID` **[REQUIRED]**
- **Access**: Read/Write (r/w)
- **Type**: integer, global dS Zone ID
- **Description**: Zone the device is in, updated by vdSM

### 1.3 `progMode` **[OPTIONAL]**
- **Access**: Read/Write (r/w)
- **Type**: boolean
- **Description**: Enables local programming mode (for devices that have it)

### 1.4 `modelFeatures` **[REQUIRED]**
- **Access**: Read-only (r)
- **Type**: list of property elements
- **Description**: Descriptions of device model features
- **Elements**: Each available feature is represented as a property element (key/value) with boolean true value
- **Purpose**: Represents the virtual device's row in the "visibility Matrix"

### 1.5 `currentConfigId` **[OPTIONAL]**
- **Access**: Read-only (r)
- **Type**: string
- **Description**: Configuration or profile ID currently active in the dS-Device

### 1.6 `configurations` **[REQUIRED]**
- **Access**: Read-only (r)
- **Type**: list of property elements
- **Description**: List of configuration or profile IDs supported by this device

---

## 2. Button Input Properties (Section 4.2)

### 2.1 `buttonInputDescriptions` **[OPTIONAL]**
- **Access**: Read-only (r)
- **Type**: list of property elements
- **Description**: Descriptions (invariable properties) of buttons in the device
- **Elements**: Named sequentially "0", "1", ...
- **Note**: Only present for devices with button inputs

#### 2.1.1 Button Input Description Elements (Section 4.2.1)
- **`name`** **[REQUIRED]** (r, string): Human readable name/number for the input
- **`dsIndex`** **[REQUIRED]** (r, integer): 0..N-1, where N=number of buttons
- **`supportsLocalKeyMode`** **[REQUIRED]** (r, boolean): Can be local button
- **`buttonID`** **[OPTIONAL]** (r, integer 0..n): ID of physical button
- **`buttonType`** **[REQUIRED]** (r, integer enum): Type of physical button
  - 0: undefined
  - 1: single pushbutton
  - 2: 2-way pushbutton
  - 3: 4-way navigation button
  - 4: 4-way navigation with center button
  - 5: 8-way navigation with center button
  - 6: on-off switch
- **`buttonElementID`** **[REQUIRED]** (r, integer): Element of multi-contact button
  - 0: center
  - 1: down
  - 2: up
  - 3: left
  - 4: right
  - 5: upper left
  - 6: lower left
  - 7: upper right
  - 8: lower right

### 2.2 `buttonInputSettings` **[OPTIONAL]**
- **Access**: Read/Write (r/w)
- **Type**: list of property elements
- **Description**: Settings (persistently stored) of buttons
- **Elements**: Named sequentially "0", "1", ...
- **Note**: Only present for devices with button inputs

#### 2.2.1 Button Input Settings Elements (Section 4.2.2)
- **`group`** **[REQUIRED]** (r/w, integer): dS group number
- **`function`** **[REQUIRED]** (r/w, integer 0..15): LTNUM descriptions (0: device, 5: room, ...)
- **`mode`** **[REQUIRED]** (r/w, integer): 
  - 255: inactive
  - 0: standard
  - 2: presence
  - 5..8: button1..4 down
  - 9..12: button1..4 up
- **`channel`** **[REQUIRED]** (r/w, integer enum): Channel this button should control
  - 0: default channel
  - 1..191: reserved for digitalSTROM standard channel types
  - 192..239: device specific channel types
- **`setsLocalPriority`** **[REQUIRED]** (r/w, boolean): Button should set local priority
- **`callsPresent`** **[REQUIRED]** (r/w, boolean): Button should call present (if system state is absent)

### 2.3 `buttonInputStates` **[OPTIONAL]**
- **Access**: Read/Write (r/w)
- **Type**: list of property elements
- **Description**: State (changing during operation, not persistently stored)
- **Elements**: Named sequentially "0", "1", ...
- **Note**: Only present for devices with button inputs

#### 2.3.1 Button Input State Elements (Section 4.2.3)
- **`value`** **[REQUIRED]** (r, boolean or NULL): false=inactive, true=active, NULL=unknown
- **`clickType`** **[REQUIRED]** (r, integer enum): Most recent click state
  - 0: tip_1x
  - 1: tip_2x
  - 2: tip_3x
  - 3: tip_4x
  - 4: hold_start
  - 5: hold_repeat
  - 6: hold_end
  - 7: click_1x
  - 8: click_2x
  - 9: click_3x
  - 10: short_long
  - 11: local_off
  - 12: local_on
  - 13: short_short_long
  - 14: local_stop
  - 255: idle (no recent click)
- **`age`** **[REQUIRED]** (r, double or NULL): Age of state in seconds
- **`error`** **[REQUIRED]** (r, integer enum): Error state
  - 0: ok
  - 1: open circuit
  - 2: short circuit
  - 4: bus connection problem
  - 5: low battery in device
  - 6: other device error

**Alternative state for direct scene calls:**
- **`actionId`** **[OPTIONAL]** (r, integer): Scene id
- **`actionMode`** **[OPTIONAL]** (r, integer enum):
  - 0: normal
  - 1: force
  - 2: undo

---

## 3. Binary Input Properties (Section 4.3)

### 3.1 `binaryInputDescriptions` **[OPTIONAL]**
- **Access**: Read-only (r)
- **Type**: list of property elements
- **Description**: Descriptions of binary inputs in the device
- **Elements**: Named sequentially "0", "1", ...
- **Note**: Only present for devices with binary inputs

#### 3.1.1 Binary Input Description Elements (Section 4.3.1)
- **`name`** **[REQUIRED]** (r, string): Human readable name/number for the input
- **`dsIndex`** **[REQUIRED]** (r, integer): 0..N-1, where N=number of binary inputs
- **`inputType`** **[REQUIRED]** (r, integer): 
  - 0: poll only
  - 1: detects changes
- **`inputUsage`** **[REQUIRED]** (r, integer enum): Usage field for the input
  - 0: undefined (generic usage or unknown)
  - 1: room climate
  - 2: outdoor climate
  - 3: climate setting (from user)
- **`sensorFunction`** **[REQUIRED]** (r, integer enum): Hardwired function
  - 0: generic input with no hardware-defined functionality
  - 12: Battery low status (set when battery is low)
- **`updateInterval`** **[REQUIRED]** (r, double): How fast the physical value is tracked, in seconds

### 3.2 `binaryInputSettings` **[OPTIONAL]**
- **Access**: Read/Write (r/w)
- **Type**: list of property elements
- **Description**: Settings (persistently stored) of binary inputs
- **Elements**: Named sequentially "0", "1", ...
- **Note**: Only present for devices with binary inputs

#### 3.2.1 Binary Input Settings Elements (Section 4.3.2)
- **`group`** **[REQUIRED]** (r/w, integer): dS group number
- **`sensorFunction`** **[REQUIRED]** (r/w, integer enum):
  - 0: App Mode (no system function)
  - 1: Presence
  - 2: Light – not yet in use
  - 3: Presence in darkness – not yet in use
  - 4: Twilight
  - 5: Motion detector
  - 6: Motion in darkness– not yet in use
  - 7: Smoke detector
  - 8: Wind monitor
  - 9: Rain monitor
  - 10: Sun radiation
  - 11: Thermostat
  - 12: Battery low status
  - 13: Window contact (set when window is open)
  - 14: Door contact (set when door is open)
  - 15: Window handle (close, open, or tilted)
  - 16: Garage door contact (set when garage door is open)
  - 17: Sun protection
  - 18: Frost detection
  - 19: Heating system enabled
  - 20: Heating change-over (heating/cooling mode)
  - 21: Initialization status
  - 22: Malfunction (device broken, requires maintenance)
  - 23: Service (device requires maintenance, operation still possible)

### 3.3 `binaryInputStates` **[OPTIONAL]**
- **Access**: Read/Write (r/w)
- **Type**: list of property elements
- **Description**: State (changing during operation, not persistently stored)
- **Elements**: Named sequentially "0", "1", ...
- **Note**: Only present for devices with binary inputs

#### 3.3.1 Binary Input State Elements (Section 4.3.3)
- **`value`** **[REQUIRED]** (r, boolean or NULL): false=inactive, true=active, NULL=unknown
- **`extendedValue`** **[OPTIONAL]** (r, integer or NULL): Replaces 'value' property if present
- **`age`** **[REQUIRED]** (r, double or NULL): Age of state in seconds
- **`error`** **[REQUIRED]** (r, integer enum):
  - 0: ok
  - 1: open circuit
  - 2: short circuit
  - 4: bus connection problem
  - 5: low battery in device
  - 6: other device error

---

## 4. Sensor Input Properties (Section 4.4)

### 4.1 `sensorDescriptions` **[OPTIONAL]**
- **Access**: Read-only (r)
- **Type**: list of property elements
- **Description**: Descriptions of sensors in the device
- **Elements**: Named sequentially "0", "1", ...
- **Note**: Only present for devices with sensors

#### 4.1.1 Sensor Input Description Elements (Section 4.4.1)
- **`name`** **[REQUIRED]** (r, string): Human readable name/number for the sensor
- **`dsIndex`** **[REQUIRED]** (r, integer): 0..N-1, where N=number of sensors
- **`sensorType`** **[REQUIRED]** (r, integer enum): Type of physical unit
  - 0: none
  - 1: Temperature in °C
  - 2: Relative humidity in %
  - 3: Illumination in lux
  - 4: Supply voltage level in V
  - 5: CO concentration in ppm
  - 6: Radon activity in Bq/m³
  - 7: Gas type sensor
  - 8: Particles <10µm in μg/m³
  - 9: Particles <2.5µm in μg/m³
  - 10: Particles <1µm in μg/m³
  - 11: Room operating panel set point, 0..100%
  - 12: Fan speed, 0..1 (0=off, <0=auto)
  - 13: Wind speed in m/s (average)
  - 14: Active Power in W
  - 15: Electric current in A
  - 16: Energy Meter in kWh
  - 17: Apparent Power in VA
  - 18: Air pressure in hPa
  - 19: Wind direction in degrees
  - 20: Sound pressure level in dB
  - 21: Precipitation intensity in mm/m² (sum of last hour)
  - 22: CO2 concentration in ppm
  - 23: Wind gust speed in m/s
  - 24: Wind gust direction in degrees
  - 25: Generated Active Power in W
  - 26: Generated Energy in kWh
  - 27: Water Quantity in l
  - 28: Water Flow Rate in l/s
- **`sensorUsage`** **[REQUIRED]** (r, integer enum): Usage field for the sensor
  - 0: undefined (generic usage or unknown)
  - 1: room
  - 2: outdoor
  - 3: user interaction (setting, dial)
  - 4: device level measurement (total, sum)
  - 5: device level last run
  - 6: device level average
- **`min`** **[REQUIRED]** (r, double): Minimum value
- **`max`** **[REQUIRED]** (r, double): Maximum value
- **`resolution`** **[REQUIRED]** (r, double): Resolution (size of LSB of actual HW sensor)
- **`updateInterval`** **[REQUIRED]** (r, double): How fast the physical value is tracked, in seconds
- **`aliveSignInterval`** **[REQUIRED]** (r, double): How fast sensor minimally sends an update

### 4.2 `sensorSettings` **[OPTIONAL]**
- **Access**: Read/Write (r/w)
- **Type**: list of property elements
- **Description**: Settings (persistently stored) of sensors
- **Elements**: Named sequentially "0", "1", ...
- **Note**: Only present for devices with sensors

#### 4.2.1 Sensor Input Settings Elements (Section 4.4.2)
- **`group`** **[REQUIRED]** (r/w, integer): dS group number
- **`minPushInterval`** **[REQUIRED]** (r/w, double): Minimum interval between pushes of changed state in seconds (default = 2)
- **`changesOnlyInterval`** **[REQUIRED]** (r/w, double): Minimum interval between pushes with same value (default = 0)

### 4.3 `sensorStates` **[OPTIONAL]**
- **Access**: Read/Write (r/w)
- **Type**: list of property elements
- **Description**: Value of a sensor (changing during operation, not persistently stored)
- **Elements**: Named sequentially "0", "1", ...
- **Note**: Only present for devices with sensors

#### 4.3.1 Sensor Input State Elements (Section 4.4.3)
- **`value`** **[REQUIRED]** (r, double or NULL): Current sensor value in the unit according to sensorType
- **`age`** **[REQUIRED]** (r, double or NULL): Age of state in seconds
- **`contextId`** **[OPTIONAL]** (r, integer or NULL): Numerical ID of context data
- **`contextMsg`** **[OPTIONAL]** (r, string or NULL): Text message of context data
- **`error`** **[REQUIRED]** (r, integer enum):
  - 0: ok
  - 1: open circuit
  - 2: short circuit
  - 4: bus connection problem
  - 5: low battery in device
  - 6: other device error

---

## 5. Device Action Properties (Section 4.5)

### 5.1 `deviceActionDescriptions` **[OPTIONAL]**
- **Access**: Read-only (r), optional
- **Type**: list of property elements
- **Description**: Descriptions of available action methods in the device
- **Elements**: Named by action name

#### 5.1.1 Device Action Description Elements (Section 4.5.2)
- **`name`** **[REQUIRED]** (mandatory, string): Name of this action property entry
- **`params`** **[OPTIONAL]** (optional, list of Parameter Objects): Parameter list related to this action
- **`description`** **[OPTIONAL]** (optional, string): Description of this template action

#### 5.1.2 Parameter Object Structure (Section 4.5.1)
- **`type`** **[REQUIRED]** (mandatory, numeric enumeration string): Data type of the parameter value
- **`min`** **[OPTIONAL]** (optional, numeric only, double): Minimum value
- **`max`** **[OPTIONAL]** (optional, numeric only, double): Maximum value
- **`resolution`** **[OPTIONAL]** (optional, numeric only, double): Resolution
- **`siunit`** **[OPTIONAL]** (optional, numeric only, string): SI Unit as a string
- **`options`** **[OPTIONAL]** (optional, enumeration only, list of key:value pairs): Option values for enumeration
- **`default`** **[OPTIONAL]** (optional, all types, double/string/option): Default value

### 5.2 `customActions` **[OPTIONAL]**
- **Access**: Read/Write (r/w), optional
- **Type**: list of property elements
- **Description**: User-defined action methods in the device
- **Elements**: Named by custom action ID (with "custom." prefix)

#### 5.2.1 Custom Action Elements (Section 4.5.3)
- **`name`** (mandatory, string): Unique ID (always has prefix "custom.")
- **`action`** (mandatory, string): Reference ID of the template action
- **`title`** (mandatory, string): Human readable name given by user
- **`params`** (optional, list of Parameter Name:Value pairs): Parameter values different from template

### 5.3 Standard Actions **[OPTIONAL]** (Section 4.5.3)
- **Access**: Read-only (r), optional
- **Type**: list of property elements
- **Description**: Static, immutable actions implemented by device
- **Elements**: Named by action ID (with "std." prefix)

#### 5.3.1 Standard Action Elements
- **`name`** (mandatory, string): Unique ID (always has prefix "std.")
- **`action`** (mandatory, string): Name of the template action
- **`params`** (optional, list of Parameter Name:Value pairs): Parameter values different from template

### 5.4 Dynamic Device Actions **[OPTIONAL]** (Section 4.5.3)
- **Access**: Varies, optional
- **Type**: list of property elements
- **Description**: Actions created on native device side
- **Elements**: Named by action ID (with "dynamic." prefix)

#### 5.4.1 Dynamic Action Elements
- **`name`** (mandatory, string): Unique ID (always has prefix "dynamic.")
- **`title`** (mandatory, string): Human readable name

---

## 6. Device State Properties (Section 4.6)

### 6.1 `deviceStateDescriptions` **[OPTIONAL]**
- **Access**: Read-only (r), optional
- **Type**: list of property elements
- **Description**: Descriptions of available state objects in the device
- **Elements**: Named by state name

#### 6.1.1 Device State Description Elements (Section 4.6.1)
- **`name`** (mandatory, string): Name of this state property entry
- **`options`** (mandatory, list of Option Id:Value pairs): Option list related to this state
  - Example: 0: Off, 1: Initializing, 2: Running, 3: Shutdown
- **`description`** (optional, string): Description of this state

### 6.2 `deviceStates` **[OPTIONAL]**
- **Access**: Read/Write (r/w), optional
- **Type**: list of property elements
- **Description**: Value of the state objects
- **Elements**: Named by state name

#### 6.2.1 Device State Value Elements (Section 4.6.2)
- **`name`** (mandatory, string): Name of this state property entry
- **`value`** (mandatory, string): Option value

---

## 7. Device Property Descriptions and Values (Section 4.6)

### 7.1 `devicePropertyDescriptions` **[OPTIONAL]**
- **Access**: Read-only (r), optional
- **Type**: list of property elements
- **Description**: Descriptions of available property objects in the device
- **Elements**: Named by property name

#### 7.1.1 Device Property Description Elements (Section 4.6.3)
- **`name`** (mandatory, string): Name of this property entry
- **`type`** (mandatory, numeric/enumeration/string): Data type of the property value
- **`min`** (optional, numeric only, double): Minimum value
- **`max`** (optional, numeric only, double): Maximum value
- **`resolution`** (optional, numeric only, double): Resolution
- **`siunit`** (optional, numeric only, string): SI Unit as a string
- **`options`** (optional, enumeration only, list of key:value pairs): Option values
- **`default`** (optional, all types, double/string/option): Default value

### 7.2 `deviceProperties` **[OPTIONAL]**
- **Access**: Read/Write (r/w), optional
- **Type**: list of property elements
- **Description**: Value of the property objects
- **Elements**: Named by property name

#### 7.2.1 Device Property Value Elements (Section 4.6.4)
- **`name`** (mandatory, string): Name of this property entry
- **`value`** (mandatory, string): Property value

---

## 8. Device Event Properties (Section 4.7)

### 8.1 `deviceEventDescriptions` **[OPTIONAL]**
- **Access**: Read-only (r), optional
- **Type**: list of property elements
- **Description**: Descriptions of available events in the device
- **Elements**: Named by event name

#### 8.1.1 Device Event Description Elements (Section 4.7.1)
- **`name`** (mandatory, string): Name of this event property entry
- **`description`** (optional, string): Description of this event

---

## 9. Output Properties (Section 4.8)

### 9.1 `outputDescription` **[OPTIONAL]**
- **Access**: Read-only (r), optional
- **Type**: list of output description properties
- **Description**: Descriptions (invariable properties) of device's output
- **Note**: Devices with no output don't have this property

#### 9.1.1 Output Description Elements (Section 4.8.1)
- **`defaultGroup`** (r, integer): dS Application ID of the device
- **`name`** (r, string): Human readable name/number for the output
- **`function`** (r, integer enum): Output function type
  - 0: on/off only
  - 1: dimmer (with channel 1, "brightness")
  - 2: positional (e.g., valves, blinds)
  - 3: dimmer with color temperature (channels 1 and 4)
  - 4: full color dimmer (channels 1-6)
  - 5: bipolar (negative and positive values)
  - 6: internally controlled
- **`outputUsage`** (r, integer enum): Usage field for the output
  - 0: undefined (generic usage or unknown)
  - 1: room
  - 2: outdoors
  - 3: user (display/indicator)
- **`variableRamp`** (r, boolean): Supports variable ramps
- **`maxPower`** (r, optional double): Max output power in Watts
- **`activeCoolingMode`** (r, optional boolean): Device can actively cool

### 9.2 `outputSettings` **[OPTIONAL]**
- **Access**: Read/Write (r/w), optional
- **Type**: list of output settings properties
- **Description**: Settings (persistently stored) of device's output
- **Note**: Devices with no output don't have this property

#### 9.2.1 Output Settings Elements (Section 4.8.2)
- **`activeGroup`** (r/w, integer): dS Application ID of the device
- **`groups`** (r/w, list of boolean property elements): Output's membership in groups
  - Named by dS group number ("1" to "63")
  - Only "true" values returned
  - NULL if not member when querying single group
- **`mode`** (r/w, integer enum): Output mode
  - 0: disabled, inactive
  - 1: binary
  - 2: gradual
  - 127: default (generically enabled using device's default mode)
- **`pushChanges`** (r/w, boolean): Locally generated changes will be pushed
- **`onThreshold`** (r/w, optional double): Minimum brightness level for non-dimmable lamps (0..100%, defaults to 50%)
- **`minBrightness`** (r/w, optional double): Minimum brightness hardware supports (0..100%)
- **`dimTimeUp`** (r/w, optional integer): Dim up time in dS 8-bit dim time format
- **`dimTimeDown`** (r/w, optional integer): Dim down time in dS 8-bit dim time format
- **`dimTimeUpAlt1`** (r/w, optional integer): Alternate 1 dim up time
- **`dimTimeDownAlt1`** (r/w, optional integer): Alternate 1 dim down time
- **`dimTimeUpAlt2`** (r/w, optional integer): Alternate 2 dim up time
- **`dimTimeDownAlt2`** (r/w, optional integer): Alternate 2 dim down time
- **`heatingSystemCapability`** (r/w, optional integer enum): How "heatingLevel" controlValue is applied
  - 1: heating only
  - 2: cooling only
  - 3: heating and cooling
- **`heatingSystemType`** (r/w, optional integer enum): Valve/actuator type attached
  - 0: undefined
  - 1: floor heating (valve)
  - 2: radiator (valve)
  - 3: wall heating (valve)
  - 4: convector passive
  - 5: convector active
  - 6: floor heating low energy (valve)

### 9.3 `outputState` **[OPTIONAL]**
- **Access**: Read/Write (r/w), optional
- **Type**: list of output state properties
- **Description**: State (changing during operation, not persistently stored)
- **Note**: Devices with no output don't have this property

#### 9.3.1 Output State Elements (Section 4.8.3)
- **`localPriority`** (r/w, boolean): Enables local priority of device's output
- **`error`** (r, integer enum): Error state
  - 0: ok
  - 1: open circuit / lamp broken
  - 2: short circuit
  - 3: overload
  - 4: bus connection problem
  - 5: low battery in device
  - 6: other device error

---

## 10. Output Channel Properties (Section 4.9)

### 10.1 `channelDescriptions` **[OPTIONAL]**
- **Access**: Read-only (r), optional
- **Type**: list of property elements
- **Description**: Descriptions (invariable properties) of channels
- **Elements**: Named sequentially "0", "1", ...

#### 10.1.1 Output Channel Description Elements (Section 4.9.1)
- **`name`** (r, string): Human readable name/number for the channel
- **`channelType`** (r, integer): Numerical Type ID of the channel
- **`dsIndex`** (r, integer): 0..N-1, where N=number of channels (index "0" is default output channel)
- **`min`** (r, double): Minimum value
- **`max`** (r, double): Maximum value
- **`resolution`** (r, double): Resolution
- **`channelIndex`** (r, integer, deprecated): 0..N-1 (no longer used as of Version 1.0.2)

### 10.2 `channelSettings` **[OPTIONAL]**
- **Access**: Read/Write (r/w), optional
- **Type**: list of property elements
- **Description**: Settings (persistently stored) of channels
- **Elements**: Named sequentially "0", "1", ...
- **Note**: Currently no per-channel settings defined

#### 10.2.1 Output Channel Settings Elements (Section 4.9.2)
- No elements currently defined

### 10.3 `channelStates` **[OPTIONAL]**
- **Access**: Read/Write (r/w), optional (Read-only in practice - use setOutputChannelValue to write)
- **Type**: list of property elements
- **Description**: Current state of channels
- **Elements**: Named sequentially "0", "1", ...
- **Note**: Channel State must not be written to directly; use setOutputChannelValue notification instead

#### 10.3.1 Output Channel State Elements (Section 4.9.3)
- **`value`** (r, double): Current channel value (brightness, blind position, power on/off)
- **`age`** (r, double): Age of state in seconds (NULL when new value set but not yet applied)

---

## 11. Scene Properties (Section 4.10)

### 11.1 `scenes` **[OPTIONAL]**
- **Access**: Read/Write (r/w), optional
- **Type**: list of property elements
- **Description**: Scene table of the device
- **Elements**: Named by scene number, starting with "0"
- **Note**: Available on devices with at least one output with standard behavior

#### 11.1.1 Scene Elements (Section 4.10)
- **`channels`** (r/w, list of property elements): Scene value for each channel
  - Elements named by channel type id
  - Each channel contains a scene value (value and dontCare flag)
- **`effect`** (r/w, integer enum): Effect applied when scene is invoked
  - 0: no effect, immediate transition
  - 1: smooth normal transition
  - 2: slow transition
  - 3: very slow transition
  - 4: blink/alerting effect
- **`dontCare`** (r/w, boolean): Scene-global dontCare flag
- **`ignoreLocalPriority`** (r/w, boolean): Calling this scene overrides local priority

#### 11.1.2 Scene Value Elements (Section 4.10.1)
For each channel in the `channels` property:
- **`value`** (r/w, double): Value for the related channel
- **`dontCare`** (r/w, boolean): Channel-specific dontCare flag
- **`automatic`** (r/w, boolean): Channel-specific automatic flag

---

## 12. Control Values (Section 4.11)

### 12.1 Control Values (Write-only)
Control values are not regular properties but named values similar to properties. They can only be written using setControlValue call, not read.

#### 12.1.1 Available Control Values
- **`heatingLevel`** (w, double): Level of heating intensity
  - Range: -100..100
  - 0 = no heating or cooling
  - 100 = max heating
  - -100 = max cooling
  - Corresponds to dS Sensortype 50

---

## Property Tree Structure Summary

```
vdSD (Virtual digitalSTROM Device)
├── General Device Properties
│   ├── primaryGroup
│   ├── zoneID
│   ├── progMode
│   ├── modelFeatures
│   ├── currentConfigId
│   └── configurations
│
├── Input Properties
│   ├── buttonInputDescriptions[]
│   │   ├── [0..N].name
│   │   ├── [0..N].dsIndex
│   │   ├── [0..N].supportsLocalKeyMode
│   │   ├── [0..N].buttonID
│   │   ├── [0..N].buttonType
│   │   └── [0..N].buttonElementID
│   │
│   ├── buttonInputSettings[]
│   │   ├── [0..N].group
│   │   ├── [0..N].function
│   │   ├── [0..N].mode
│   │   ├── [0..N].channel
│   │   ├── [0..N].setsLocalPriority
│   │   └── [0..N].callsPresent
│   │
│   ├── buttonInputStates[]
│   │   ├── [0..N].value
│   │   ├── [0..N].clickType
│   │   ├── [0..N].age
│   │   ├── [0..N].error
│   │   ├── [0..N].actionId (alternative)
│   │   └── [0..N].actionMode (alternative)
│   │
│   ├── binaryInputDescriptions[]
│   │   ├── [0..N].name
│   │   ├── [0..N].dsIndex
│   │   ├── [0..N].inputType
│   │   ├── [0..N].inputUsage
│   │   ├── [0..N].sensorFunction
│   │   └── [0..N].updateInterval
│   │
│   ├── binaryInputSettings[]
│   │   ├── [0..N].group
│   │   └── [0..N].sensorFunction
│   │
│   ├── binaryInputStates[]
│   │   ├── [0..N].value
│   │   ├── [0..N].extendedValue
│   │   ├── [0..N].age
│   │   └── [0..N].error
│   │
│   ├── sensorDescriptions[]
│   │   ├── [0..N].name
│   │   ├── [0..N].dsIndex
│   │   ├── [0..N].sensorType
│   │   ├── [0..N].sensorUsage
│   │   ├── [0..N].min
│   │   ├── [0..N].max
│   │   ├── [0..N].resolution
│   │   ├── [0..N].updateInterval
│   │   └── [0..N].aliveSignInterval
│   │
│   ├── sensorSettings[]
│   │   ├── [0..N].group
│   │   ├── [0..N].minPushInterval
│   │   └── [0..N].changesOnlyInterval
│   │
│   └── sensorStates[]
│       ├── [0..N].value
│       ├── [0..N].age
│       ├── [0..N].contextId
│       ├── [0..N].contextMsg
│       └── [0..N].error
│
├── Action Properties
│   ├── deviceActionDescriptions[]
│   │   ├── [actionName].name
│   │   ├── [actionName].params[]
│   │   │   ├── type
│   │   │   ├── min
│   │   │   ├── max
│   │   │   ├── resolution
│   │   │   ├── siunit
│   │   │   ├── options
│   │   │   └── default
│   │   └── [actionName].description
│   │
│   ├── customActions[]
│   │   ├── [custom.actionId].name
│   │   ├── [custom.actionId].action
│   │   ├── [custom.actionId].title
│   │   └── [custom.actionId].params[]
│   │
│   ├── standardActions[]
│   │   ├── [std.actionId].name
│   │   ├── [std.actionId].action
│   │   └── [std.actionId].params[]
│   │
│   └── dynamicDeviceActions[]
│       ├── [dynamic.actionId].name
│       └── [dynamic.actionId].title
│
├── State and Property Objects
│   ├── deviceStateDescriptions[]
│   │   ├── [stateName].name
│   │   ├── [stateName].options[]
│   │   └── [stateName].description
│   │
│   ├── deviceStates[]
│   │   ├── [stateName].name
│   │   └── [stateName].value
│   │
│   ├── devicePropertyDescriptions[]
│   │   ├── [propertyName].name
│   │   ├── [propertyName].type
│   │   ├── [propertyName].min
│   │   ├── [propertyName].max
│   │   ├── [propertyName].resolution
│   │   ├── [propertyName].siunit
│   │   ├── [propertyName].options
│   │   └── [propertyName].default
│   │
│   └── deviceProperties[]
│       ├── [propertyName].name
│       └── [propertyName].value
│
├── Event Properties
│   └── deviceEventDescriptions[]
│       ├── [eventName].name
│       └── [eventName].description
│
├── Output Properties
│   ├── outputDescription
│   │   ├── defaultGroup
│   │   ├── name
│   │   ├── function
│   │   ├── outputUsage
│   │   ├── variableRamp
│   │   ├── maxPower
│   │   └── activeCoolingMode
│   │
│   ├── outputSettings
│   │   ├── activeGroup
│   │   ├── groups[]
│   │   │   └── [1..63] (boolean)
│   │   ├── mode
│   │   ├── pushChanges
│   │   ├── onThreshold
│   │   ├── minBrightness
│   │   ├── dimTimeUp
│   │   ├── dimTimeDown
│   │   ├── dimTimeUpAlt1
│   │   ├── dimTimeDownAlt1
│   │   ├── dimTimeUpAlt2
│   │   ├── dimTimeDownAlt2
│   │   ├── heatingSystemCapability
│   │   └── heatingSystemType
│   │
│   └── outputState
│       ├── localPriority
│       └── error
│
├── Channel Properties
│   ├── channelDescriptions[]
│   │   ├── [0..N].name
│   │   ├── [0..N].channelType
│   │   ├── [0..N].dsIndex
│   │   ├── [0..N].min
│   │   ├── [0..N].max
│   │   └── [0..N].resolution
│   │
│   ├── channelSettings[]
│   │   └── (currently no elements defined)
│   │
│   └── channelStates[]
│       ├── [0..N].value
│       └── [0..N].age
│
├── Scene Properties
│   └── scenes[]
│       ├── [sceneNumber].channels[]
│       │   └── [channelTypeId].value
│       │   └── [channelTypeId].dontCare
│       │   └── [channelTypeId].automatic
│       ├── [sceneNumber].effect
│       ├── [sceneNumber].dontCare
│       └── [sceneNumber].ignoreLocalPriority
│
└── Control Values (write-only)
    └── heatingLevel
```

---

## Notes

1. **Property Access Modes**:
   - **r**: Read-only
   - **r/w**: Read and write
   - **w**: Write-only

2. **Optional vs. Mandatory**:
   - Properties marked "optional" may not be available in all implementations
   - getProperty will not return them if not available (no error)
   - setProperty will return error if trying to set a non-implemented property

3. **Array Notation**:
   - Properties ending with `[]` are arrays/lists of property elements
   - Elements are typically named sequentially "0", "1", "2", ... or by specific identifiers

4. **Common Properties**:
   - All vdSD entities must also support the basic set of common properties defined in Section 2 of the vDC-API-properties document (not listed here)

5. **Device Type Dependencies**:
   - Not all devices have all properties
   - Input-only devices don't have output/channel/scene properties
   - Output-only devices may not have input properties
   - Property availability depends on device functionality

6. **Hierarchical Structure**:
   - Properties can be nested indefinitely
   - It's recommended to keep nesting levels as low as possible
   - Property elements can contain name (key) and value, or another level of property elements

---

## Document Information

- **Source**: vDC-API-properties_JULY 2022.pdf, Chapter 4
- **Version**: Based on document dated July 5, 2022
- **Related Documents**: 
  - vDC-overview.pdf
  - vDC-API.pdf
  - ds-basics.pdf (referenced for output channel types)

---

*This document provides a comprehensive reference for all property subtrees defined in the vDC specification. It should be used in conjunction with the complete vDC API documentation for implementation details.*
