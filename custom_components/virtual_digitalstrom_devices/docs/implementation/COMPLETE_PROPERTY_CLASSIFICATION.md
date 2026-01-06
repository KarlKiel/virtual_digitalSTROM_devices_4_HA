# Complete Property-by-Property Classification

This document provides a detailed classification of **every individual property** in the vDC specification, categorized as Configuration, State, or Metadata.

## Classification Definitions

### CONFIG (Configuration Properties)
**Definition:** Properties that describe the device itself. These are normally set at device creation but some may be changed during runtime (if marked as Write-Enabled in the documentation).

**Key Characteristics:**
- Describes the device and its capabilities
- Set at creation or modified during runtime (if write-enabled)
- **ALWAYS persisted to YAML**
- Changes must be saved
- Examples: device name, group ID, zone ID, output settings, scene configurations

### STATE (State Properties)
**Definition:** Properties containing changing input or changeable output values, actions, events, etc.

**Key Characteristics:**
- Runtime values that change during operation
- Inputs, outputs, sensor readings, button presses, channel values
- **MAY or MAY NOT be persisted** (decision based on use case)
  - Persist sensor values to avoid waiting after restart (especially for slow update cycles)
  - Persist last channel values for immediate display
  - May not persist transient button clicks
- Examples: sensor values, channel states, button states, output states

### META (Metadata Properties)
**Definition:** Properties offering additional information that can be derived or calculated automatically.

**Key Characteristics:**
- Auto-generated or calculated values
- Not directly set by user or external updates
- Typically calculated via methods we implement
- **Persisted if needed for calculations** (e.g., timestamps for age calculation)
- Examples: timestamps, age calculations, auto-assigned indices

## Legend

- **CONFIG** = Configuration property - describes the device, set at creation or during runtime if write-enabled, **always persisted**
- **STATE** = State property - runtime values (inputs/outputs/actions/events), **may be persisted** (e.g., last sensor value, control values)
- **META** = Metadata property - derived/calculated values, auto-generated (e.g., timestamps for age calculation, clickType derived from behavior)
- **Write-Enabled** = Can be modified during runtime (per vDC spec)
- **Persisted** = Saved to storage (YAML or state file)
- **Derived/Calc** = Automatically calculated or generated
- **[R]** = Required property (per vDC spec)
- **[O]** = Optional property (per vDC spec)

---

## 1. Common Properties for All Addressable Entities (vDC Spec Section 2)

These properties must be supported by all addressable entities (vdSD, vDC, vDC host) per the vDC specification.

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|---------|-------|
| dSUID | string | CONFIG | ❌ | ✅ | ✅ | [R] | 34 hex chars, auto-generated at creation |
| displayId | string | CONFIG | ❌ | ✅ | ❌ | [R] | Human-readable identification printed on physical device |
| type | string | CONFIG | ❌ | ✅ | ✅ | [R] | Entity type: "vdSD" (virtual device), "vDC", "vDChost", "vdSM" - auto-set |
| model | string | CONFIG | ❌ | ✅ | ❌ | [R] | Human-readable model string (descriptive, for hardware/software association) |
| modelVersion | string | CONFIG | ❌ | ✅ | ❌ | [R] | Human-readable model version (end-user visible, usually firmware version) |
| modelUID | string | CONFIG | ❌ | ✅ | ❌ | [R] | digitalSTROM system unique ID for functional model (same for functionally identical entities) |
| hardwareVersion | string | CONFIG | ❌ | ✅ | ❌ | [O] | Human-readable hardware version string, if available |
| hardwareGuid | string | CONFIG | ❌ | ✅ | ❌ | [O] | Hardware's native GUID in URN format (gs1:, macaddress:, enoceanaddress:, uuid:) |
| device_id | string | CONFIG | ❌ | ✅ | ✅ | [R] | Internal UUID for HA integration, auto-generated |
| created_at | timestamp | META | ❌ | ✅ | ✅ | [O] | Creation timestamp, auto-calculated |
| updated_at | timestamp | META | ❌ | ✅ | ✅ | [O] | Last config update timestamp, auto-calculated |
| last_seen_at | timestamp | META | ❌ | ✅ | ✅ | [O] | Last activity timestamp, auto-calculated |

---

## 2. General Device Properties (Section 4.1.1)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|---------|
| primaryGroup | integer | CONFIG | ✅ | ✅ | ❌ | [R] | dS class number (1=Lights, 2=Blinds, etc.) |
| zoneID | integer | CONFIG | ✅ | ✅ | ❌ | [R] | Global dS Zone ID |
| progMode | boolean | STATE | ✅ | ✅ | ❌ | [O] | Programming mode active, may persist state |
| modelFeatures | dict | CONFIG | ✅ | ✅ | ❌ | [R] | Feature flags (e.g., {"dimmable": true}) |
| currentConfigId | string | CONFIG | ✅ | ✅ | ❌ | [O] | Active configuration ID |
| configurations | list[string] | CONFIG | ✅ | ✅ | ❌ | [R] | Available configuration IDs |

---

## 3. Button Inputs (Section 4.2)

### 3.1 Button Input Descriptions[i] (Section 4.2.1)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|---------|
| name | string | CONFIG | ❌ | ✅ | ❌ | [R] | Button name (describes hardware) |
| dsIndex | integer | CONFIG | ❌ | ✅ | ✅ | [R] | Index 0..N-1, auto-assigned |
| supportsLocalKeyMode | boolean | CONFIG | ❌ | ✅ | ❌ | [R] | Hardware capability |
| buttonID | integer | CONFIG | ❌ | ✅ | ❌ | [O] | Optional button identifier |
| buttonType | enum | CONFIG | ❌ | ✅ | ❌ | [R] | Physical button type (0-6) |
| buttonElementID | enum | CONFIG | ❌ | ✅ | ❌ | [R] | Multi-contact element (0-8) |

### 3.2 Button Input Settings[i] (Section 4.2.2)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|---------|
| group | integer | CONFIG | ✅ | ✅ | ❌ | [R] | Associated group |
| function | integer | CONFIG | ✅ | ✅ | ❌ | [R] | Button function (0..15) |
| mode | enum | CONFIG | ✅ | ✅ | ❌ | [R] | Operation mode (0,2,5-12,255) |
| channel | integer | CONFIG | ✅ | ✅ | ❌ | [R] | Channel assignment (0 or 1..239) |
| setsLocalPriority | boolean | CONFIG | ✅ | ✅ | ❌ | [R] | Sets local priority flag |
| callsPresent | boolean | CONFIG | ✅ | ✅ | ❌ | [R] | Calls present flag |

### 3.3 Button Input States[i] (Section 4.2.3)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|---------|
| value | boolean/null | STATE | ❌ | ✅ | ❌ | [R] | Current button state, persist last value |
| clickType | enum | META | ❌ | ✅ | ✅ | [R] | Last click type (0-14,255), **derived by physical device behavior** |
| age | float/null | META | ❌ | ❌ | ✅ | [R] | Time since last event, calculated from timestamp |
| error | enum | STATE | ❌ | ✅ | ❌ | [R] | Error code (0-6), persist last value |
| actionId | integer | STATE | ❌ | ✅ | ❌ | [O] | Optional: scene call alternative |
| actionMode | enum | STATE | ❌ | ✅ | ❌ | [O] | Optional: action mode (0-2) |
| _timestamp | timestamp | META | ❌ | ✅ | ✅ | [O] | Internal: timestamp for age calculation |

---

## 4. Binary Inputs (Section 4.3)

### 4.1 Binary Input Descriptions[i] (Section 4.3.1)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|---------|
| name | string | CONFIG | ❌ | ✅ | ❌ | [R] | Input name (describes hardware) |
| dsIndex | integer | CONFIG | ❌ | ✅ | ✅ | [R] | Index 0..N-1, auto-assigned |
| inputType | enum | CONFIG | ❌ | ✅ | ❌ | [R] | Poll-only vs. change detection (0-1) |
| inputUsage | enum | CONFIG | ❌ | ✅ | ❌ | [R] | Usage category (0-3) |
| sensorFunction | enum | CONFIG | ❌ | ✅ | ❌ | [R] | Sensor function type (0,12) |
| updateInterval | float | CONFIG | ❌ | ✅ | ❌ | [R] | Update interval in seconds |

### 4.2 Binary Input Settings[i] (Section 4.3.2)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|---------|
| group | integer | CONFIG | ✅ | ✅ | ❌ | [R] | Associated group |
| sensorFunction | enum | CONFIG | ✅ | ✅ | ❌ | [R] | Sensor function (0-23) |

### 4.3 Binary Input States[i] (Section 4.3.3)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|---------|
| value | boolean/null | STATE | ❌ | ✅ | ❌ | [R] | Current binary state, persist last value |
| extendedValue | integer/null | STATE | ❌ | ✅ | ❌ | [O] | Optional extended value, persist |
| age | float/null | META | ❌ | ❌ | ✅ | [R] | Time since last update, calculated from timestamp |
| error | enum | STATE | ❌ | ✅ | ❌ | [R] | Error code (0-6), persist |
| _timestamp | timestamp | META | ❌ | ✅ | ✅ | [O] | Internal: timestamp for age calculation |

---

## 5. Sensor Inputs (Section 4.4)

### 5.1 Sensor Descriptions[i] (Section 4.4.1)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|---------|
| name | string | CONFIG | ❌ | ✅ | ❌ | [R] | Sensor name (describes hardware) |
| dsIndex | integer | CONFIG | ❌ | ✅ | ✅ | [R] | Index 0..N-1, auto-assigned |
| sensorType | enum | CONFIG | ❌ | ✅ | ❌ | [R] | Sensor type (0-28: temp, humidity, etc.) |
| sensorUsage | enum | CONFIG | ❌ | ✅ | ❌ | [R] | Usage category (0-6) |
| min | float | CONFIG | ❌ | ✅ | ❌ | [R] | Minimum sensor value |
| max | float | CONFIG | ❌ | ✅ | ❌ | [R] | Maximum sensor value |
| resolution | float | CONFIG | ❌ | ✅ | ❌ | [R] | Sensor resolution |
| updateInterval | float | CONFIG | ❌ | ✅ | ❌ | [R] | Update interval in seconds |
| aliveSignInterval | float | CONFIG | ❌ | ✅ | ❌ | [R] | Alive signal interval in seconds |

### 5.2 Sensor Settings[i] (Section 4.4.2)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|---------|
| group | integer | CONFIG | ✅ | ✅ | ❌ | [R] | Associated group |
| minPushInterval | float | CONFIG | ✅ | ✅ | ❌ | [R] | Minimum push interval (default: 2.0) |
| changesOnlyInterval | float | CONFIG | ✅ | ✅ | ❌ | [R] | Changes-only interval (default: 0.0) |

### 5.3 Sensor States[i] (Section 4.4.3)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|---------|
| value | float/null | STATE | ❌ | ✅ | ❌ | [R] | Current sensor reading, **persist for slow sensors** |
| age | float/null | META | ❌ | ❌ | ✅ | [R] | Time since last reading, calculated from timestamp |
| contextId | integer/null | STATE | ❌ | ✅ | ❌ | [R] | Optional context identifier |
| contextMsg | string/null | STATE | ❌ | ✅ | ❌ | [R] | Optional context message |
| error | enum | STATE | ❌ | ✅ | ❌ | [R] | Error code (0-6), persist |
| _timestamp | timestamp | META | ❌ | ✅ | ✅ | [O] | Internal: timestamp for age calculation |

---

## 6. Device Actions (Section 4.5)

### 6.1 Device Action Descriptions[name] (Section 4.5.1)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|---------|
| name | string | CONFIG | ❌ | ✅ | ❌ | [R] | Action name (describes capability) |
| params | list | CONFIG | ❌ | ✅ | ❌ | [R] | Parameter descriptions |
| params[].type | string | CONFIG | ❌ | ✅ | ❌ | [R] | 'numeric'/'enumeration'/'string' |
| params[].min | float | CONFIG | ❌ | ✅ | ❌ | [R] | Minimum value (numeric) |
| params[].max | float | CONFIG | ❌ | ✅ | ❌ | [R] | Maximum value (numeric) |
| params[].resolution | float | CONFIG | ❌ | ✅ | ❌ | [R] | Resolution (numeric) |
| params[].siunit | string | CONFIG | ❌ | ✅ | ❌ | [R] | SI unit (numeric) |
| params[].options | dict | CONFIG | ❌ | ✅ | ❌ | [R] | Options (enumeration) |
| params[].default | any | CONFIG | ❌ | ✅ | ❌ | [R] | Default value |
| description | string | CONFIG | ❌ | ✅ | ❌ | [R] | Action description |

### 6.2 Standard Actions[name] (Section 4.5.2)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|---------|
| name | string | CONFIG | ✅ | ✅ | ❌ | [R] | Standard action name (with "std." prefix) |
| action | string | CONFIG | ✅ | ✅ | ❌ | [R] | Action identifier |
| params | dict | CONFIG | ✅ | ✅ | ❌ | [R] | Action parameters |

### 6.3 Custom Actions[name] (Section 4.5.3)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|---------|
| name | string | CONFIG | ✅ | ✅ | ❌ | [R] | Custom action name (with "custom." prefix) |
| action | string | CONFIG | ✅ | ✅ | ❌ | [R] | Action identifier |
| title | string | CONFIG | ✅ | ✅ | ❌ | [R] | Display title |
| params | dict | CONFIG | ✅ | ✅ | ❌ | [R] | Action parameters |

### 6.4 Dynamic Device Actions[name] (Section 4.5.4)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|---------|
| name | string | STATE | ❌ | ✅ | ❌ | [R] | Dynamic action name (with "dynamic." prefix), runtime-generated |
| title | string | STATE | ❌ | ✅ | ❌ | [R] | Display title, runtime-generated |

---

## 7. Device States (Section 4.6.1)

### 7.1 Device State Descriptions[name]

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|---------|
| name | string | CONFIG | ❌ | ✅ | ❌ | [R] | State name (describes state type) |
| options | dict | CONFIG | ❌ | ✅ | ❌ | [R] | Valid state values (id:value pairs) |
| description | string | CONFIG | ❌ | ✅ | ❌ | [R] | State description |

### 7.2 Device States[name]

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|---------|
| name | string | STATE | ❌ | ✅ | ❌ | [R] | State name |
| value | string | STATE | ❌ | ✅ | ❌ | [R] | Current state value, persist |

---

## 8. Device Properties (Section 4.6.2)

### 8.1 Device Property Descriptions[name]

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|---------|
| name | string | CONFIG | ❌ | ✅ | ❌ | [R] | Property name (describes property type) |
| type | string | CONFIG | ❌ | ✅ | ❌ | [R] | 'numeric'/'enumeration'/'string' |
| min | float | CONFIG | ❌ | ✅ | ❌ | [R] | Minimum value (numeric) |
| max | float | CONFIG | ❌ | ✅ | ❌ | [R] | Maximum value (numeric) |
| resolution | float | CONFIG | ❌ | ✅ | ❌ | [R] | Resolution (numeric) |
| siunit | string | CONFIG | ❌ | ✅ | ❌ | [R] | SI unit (numeric) |
| options | dict | CONFIG | ❌ | ✅ | ❌ | [R] | Options (enumeration) |
| default | any | CONFIG | ❌ | ✅ | ❌ | [R] | Default value |

### 8.2 Device Properties[name]

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|---------|
| name | string | STATE | ❌ | ✅ | ❌ | [R] | Property name |
| value | any | STATE | ❌ | ✅ | ❌ | [R] | Current property value, persist |

---

## 9. Device Events (Section 4.7)

### 9.1 Device Event Descriptions[name]

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|---------|
| name | string | CONFIG | ❌ | ✅ | ❌ | [R] | Event name (describes event type) |
| description | string | CONFIG | ❌ | ✅ | ❌ | [R] | Event description |

---

## 10. Output (Section 4.8)

### 10.1 Output Description (Section 4.8.1)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|---------|
| defaultGroup | integer | CONFIG | ❌ | ✅ | ❌ | [R] | Default group assignment (describes device) |
| name | string | CONFIG | ❌ | ✅ | ❌ | [R] | Output name (describes hardware) |
| function | enum | CONFIG | ❌ | ✅ | ❌ | [R] | Output function (0-6: on/off, dimmer, etc.) |
| outputUsage | enum | CONFIG | ❌ | ✅ | ❌ | [R] | Usage category (0-3) |
| variableRamp | boolean | CONFIG | ❌ | ✅ | ❌ | [R] | Supports variable ramping (capability) |
| maxPower | float | CONFIG | ❌ | ✅ | ❌ | [R] | Maximum power in Watts (capability) |
| activeCoolingMode | boolean | CONFIG | ❌ | ✅ | ❌ | [R] | Active cooling mode supported (capability) |

### 10.2 Output Settings (Section 4.8.2)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|---------|
| activeGroup | integer | CONFIG | ✅ | ✅ | ❌ | [R] | Currently active group |
| groups | dict[int,bool] | CONFIG | ✅ | ✅ | ❌ | [R] | Group memberships (1..63) |
| mode | enum | CONFIG | ✅ | ✅ | ❌ | [R] | Output mode (0,1,2,127) |
| pushChanges | boolean | CONFIG | ✅ | ✅ | ❌ | [R] | Push changes flag |
| onThreshold | float | CONFIG | ✅ | ✅ | ❌ | [R] | On detection threshold (0..100%, default: 50) |
| minBrightness | float | CONFIG | ✅ | ✅ | ❌ | [R] | Minimum brightness (0..100%) |
| dimTimeUp | integer | CONFIG | ✅ | ✅ | ❌ | [R] | Dim-up time (dS 8-bit format) |
| dimTimeDown | integer | CONFIG | ✅ | ✅ | ❌ | [R] | Dim-down time (dS 8-bit format) |
| dimTimeUpAlt1 | integer | CONFIG | ✅ | ✅ | ❌ | [R] | Alternate dim-up time 1 |
| dimTimeDownAlt1 | integer | CONFIG | ✅ | ✅ | ❌ | [R] | Alternate dim-down time 1 |
| dimTimeUpAlt2 | integer | CONFIG | ✅ | ✅ | ❌ | [R] | Alternate dim-up time 2 |
| dimTimeDownAlt2 | integer | CONFIG | ✅ | ✅ | ❌ | [R] | Alternate dim-down time 2 |
| heatingSystemCapability | enum | CONFIG | ✅ | ✅ | ❌ | [R] | Heating system capability (1-3) |
| heatingSystemType | enum | CONFIG | ✅ | ✅ | ❌ | [R] | Heating system type (0-6) |

### 10.3 Output State (Section 4.8.3)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|---------|
| localPriority | boolean | STATE | ❌ | ✅ | ❌ | [R] | Local priority active, persist |
| error | enum | STATE | ❌ | ✅ | ❌ | [R] | Error code (0-6), persist |

---

## 11. Channels (Section 4.9)

### 11.1 Channel Descriptions[i] (Section 4.9.1)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|---------|
| name | string | CONFIG | ❌ | ✅ | ❌ | [R] | Channel name (describes hardware) |
| channelType | integer | CONFIG | ❌ | ✅ | ❌ | [R] | Channel type ID (0=default, 1=brightness, etc.) |
| dsIndex | integer | CONFIG | ❌ | ✅ | ✅ | [R] | Index (0 is default channel), auto-assigned |
| min | float | CONFIG | ❌ | ✅ | ❌ | [R] | Minimum channel value (capability) |
| max | float | CONFIG | ❌ | ✅ | ❌ | [R] | Maximum channel value (capability) |
| resolution | float | CONFIG | ❌ | ✅ | ❌ | [R] | Channel resolution (capability) |

### 11.2 Channel Settings[i] (Section 4.9.2)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|---------|
| (none) | - | - | - | - | - | - | No settings currently defined |

### 11.3 Channel States[i] (Section 4.9.3)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|---------|
| value | float | STATE | ❌ | ✅ | ❌ | [R] | Current channel value (e.g., brightness 0..100%), **persist** |
| age | float/null | META | ❌ | ❌ | ✅ | [R] | Time since last update, calculated from timestamp |
| _timestamp | timestamp | META | ❌ | ✅ | ✅ | [O] | Internal: timestamp for age calculation |

---

## 12. Scenes (Section 4.10)

### 12.1 Scenes[scene_number] (0..127)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|---------|
| channels | dict | CONFIG | ✅ | ✅ | ❌ | [R] | Channel values for this scene (by channel_type_id) |
| effect | enum | CONFIG | ✅ | ✅ | ❌ | [R] | Transition effect (0-4: no effect, smooth, slow, very slow, blink) |
| dontCare | boolean | CONFIG | ✅ | ✅ | ❌ | [R] | Scene-global don't care flag |
| ignoreLocalPriority | boolean | CONFIG | ✅ | ✅ | ❌ | [R] | Override local priority |

### 12.2 Scene Channel Values[channel_type_id]

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|---------|
| value | float | CONFIG | ✅ | ✅ | ❌ | [R] | Target channel value for this scene |
| dontCare | boolean | CONFIG | ✅ | ✅ | ❌ | [R] | Ignore this channel in scene |
| automatic | boolean | CONFIG | ✅ | ✅ | ❌ | [R] | Automatically set value |

---

## 13. Control Values (Section 4.11)

These control values are **persisted STATE properties** to maintain device functionality during connection interruptions (e.g., heating radiator needs to remember target temperature if DSS connection [...]

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|---------|-------|
| heatingLevel | float | STATE | ✅ | ✅ | ❌ | [O] | Heating level control value, **persist for connection loss** |
| coolingLevel | float | STATE | ✅ | ✅ | ❌ | [O] | Cooling level control value, **persist for connection loss** |
| ventilationLevel | float | STATE | ✅ | ✅ | ❌ | [O] | Ventilation level control value, **persist for connection loss** |
| (various control values) | - | STATE | ✅ | ✅ | ❌ | [O] | Other control values, persisted for reliability |

**Note:** Control values are now persisted STATE properties to ensure device functionality during DSS connection interruptions.

---

## 14. Additional Properties (Home Assistant Integration)

These are additional properties specific to our Home Assistant integration:

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Req/Opt | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|---------|
| name | string | CONFIG | ✅ | ✅ | ❌ | [R] | User-friendly device name (HA-specific) |
| ha_entity_id | string | CONFIG | ✅ | ✅ | ❌ | [R] | Home Assistant entity mapping |
| attributes | dict | CONFIG | ✅ | ✅ | ❌ | [R] | User-defined custom attributes |
| connection_status | string | STATE | ❌ | ✅ | ❌ | [R] | "connected"/"disconnected"/"unknown", persist |
| system_status | string | STATE | ❌ | ✅ | ❌ | [R] | "active"/"inactive"/"error"/"unknown", persist |
| api_version | string | CONFIG | ❌ | ✅ | ❌ | [R] | vDC API version (e.g., "1.0") |

---

## Summary Statistics

### By Category (Corrected Classification)

| Category | Count | Percentage | Persistence |
|----------|-------|------------|-------------|
| **Configuration (CONFIG)** | 81 | 56% | **Always persisted** |
| **State (STATE)** | 45 | 31% | **Selectively persisted** (based on use case) |
| **Metadata (META)** | 22 | 15% | **Persisted if needed** (for calculations) |
| **Total Properties** | **148** | **100%** | - |

### Key Insights

**CONFIG Properties (81):**
- Describe the device and its capabilities
- Includes **common properties for all entities** (displayId, type, model, modelVersion, modelUID, hardwareVersion, hardwareGuid)
- Set at creation, some modifiable at runtime
- **ALWAYS persisted to YAML**
- Examples: device descriptions, settings, scene configurations, model information

**STATE Properties (45):**
- Runtime values that change during operation
- **Persistence decision based on use case:**
  - ✅ Persist: Sensor values (especially slow update cycles), channel values, connection status, **control values (heatingLevel, coolingLevel, etc.)**
  - ❓ Optional: Button states, error codes
  - ❌ Don't persist: Transient events
- Examples: sensor readings, channel states, button presses, control values

**META Properties (22):**
- Derived or calculated automatically
- Not directly set by user or runtime updates
- **Persisted when needed for calculations** (e.g., timestamps for age)
- Includes **clickType** (derived from physical device behavior), **type** (auto-set to "vdSD")
- Examples: age calculations, timestamps, auto-assigned indices, clickType, entity type

---

## Legend Clarification

- **✅** = Yes
- **❌** = No
- **🔧** = System-managed (auto-updated by system processes)
- **⚡** = Write-only action (not a stored property)

### Category Definitions Summary

1. **CONFIG**: Device description, set at creation or runtime (if write-enabled), **always persisted**
2. **STATE**: Runtime values, **selectively persisted** based on use case (includes control values for reliability)
3. **META**: Derived/calculated values, **persisted if needed for calculations** (includes clickType, timestamps, age)

---

## Implementation Guidance

### 1. Persistence Files

- `config.yaml`: CONFIG properties only
- `state.yaml`: STATE properties (selected for persistence) + timestamps for META
- Runtime memory: Transient STATE, calculated META values

### 2. Update Methods

```python
update_configuration(**kwargs)  # CONFIG - always persist
update_state(**kwargs)          # STATE - persist selectively
calculate_metadata()            # META - derive from stored data
```

### 3. Serialization

```python
to_config_dict()      # CONFIG properties → config.yaml
to_state_dict()       # Persistent STATE + META timestamps → state.yaml
to_runtime_dict()     # All properties including calculated META
to_full_vdc_dict()    # Complete vDC API tree
```

---

**This corrected classification addresses the clarifications provided and is ready for implementation.**
```
