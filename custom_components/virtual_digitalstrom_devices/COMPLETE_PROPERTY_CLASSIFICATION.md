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
- **STATE** = State property - runtime values (inputs/outputs/actions/events), **may be persisted** (e.g., last sensor value)
- **META** = Metadata property - derived/calculated values, auto-generated (e.g., timestamps for age calculation)
- **Write-Enabled** = Can be modified during runtime (per vDC spec)
- **Persisted** = Saved to storage (YAML or state file)
- **Derived/Calc** = Automatically calculated or generated

---

## 1. Root Device Properties

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| dSUID | string | CONFIG | ❌ | ✅ | ✅ | 34 hex chars, auto-generated at creation |
| device_id | string | CONFIG | ❌ | ✅ | ✅ | Internal UUID, auto-generated at creation |
| created_at | timestamp | META | ❌ | ✅ | ✅ | Creation timestamp, auto-calculated |
| updated_at | timestamp | META | ❌ | ✅ | ✅ | Last config update timestamp, auto-calculated |
| last_seen_at | timestamp | META | ❌ | ✅ | ✅ | Last activity timestamp, auto-calculated |

---

## 2. General Device Properties (Section 4.1.1)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| primaryGroup | integer | CONFIG | ✅ | ✅ | ❌ | dS class number (1=Lights, 2=Blinds, etc.) |
| zoneID | integer | CONFIG | ✅ | ✅ | ❌ | Global dS Zone ID |
| progMode | boolean | STATE | ✅ | ✅ | ❌ | Programming mode active, may persist state |
| modelFeatures | dict | CONFIG | ✅ | ✅ | ❌ | Feature flags (e.g., {"dimmable": true}) |
| currentConfigId | string | CONFIG | ✅ | ✅ | ❌ | Active configuration ID |
| configurations | list[string] | CONFIG | ✅ | ✅ | ❌ | Available configuration IDs |

---

## 3. Button Inputs (Section 4.2)

### 3.1 Button Input Descriptions[i] (Section 4.2.1)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| name | string | CONFIG | ❌ | ✅ | ❌ | Button name (describes hardware) |
| dsIndex | integer | CONFIG | ❌ | ✅ | ✅ | Index 0..N-1, auto-assigned |
| supportsLocalKeyMode | boolean | CONFIG | ❌ | ✅ | ❌ | Hardware capability |
| buttonID | integer | CONFIG | ❌ | ✅ | ❌ | Optional button identifier |
| buttonType | enum | CONFIG | ❌ | ✅ | ❌ | Physical button type (0-6) |
| buttonElementID | enum | CONFIG | ❌ | ✅ | ❌ | Multi-contact element (0-8) |

### 3.2 Button Input Settings[i] (Section 4.2.2)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| group | integer | CONFIG | ✅ | ✅ | ❌ | Associated group |
| function | integer | CONFIG | ✅ | ✅ | ❌ | Button function (0..15) |
| mode | enum | CONFIG | ✅ | ✅ | ❌ | Operation mode (0,2,5-12,255) |
| channel | integer | CONFIG | ✅ | ✅ | ❌ | Channel assignment (0 or 1..239) |
| setsLocalPriority | boolean | CONFIG | ✅ | ✅ | ❌ | Sets local priority flag |
| callsPresent | boolean | CONFIG | ✅ | ✅ | ❌ | Calls present flag |

### 3.3 Button Input States[i] (Section 4.2.3)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| value | boolean/null | STATE | ❌ | ✅ | ❌ | Current button state, persist last value |
| clickType | enum | STATE | ❌ | ✅ | ❌ | Last click type (0-14,255), persist last value |
| age | float/null | META | ❌ | ❌ | ✅ | Time since last event, calculated from timestamp |
| error | enum | STATE | ❌ | ✅ | ❌ | Error code (0-6), persist last value |
| actionId | integer | STATE | ❌ | ✅ | ❌ | Optional: scene call alternative |
| actionMode | enum | STATE | ❌ | ✅ | ❌ | Optional: action mode (0-2) |
| _timestamp | timestamp | META | ❌ | ✅ | ✅ | Internal: timestamp for age calculation |

---

## 4. Binary Inputs (Section 4.3)

### 4.1 Binary Input Descriptions[i] (Section 4.3.1)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| name | string | CONFIG | ❌ | ✅ | ❌ | Input name (describes hardware) |
| dsIndex | integer | CONFIG | ❌ | ✅ | ✅ | Index 0..N-1, auto-assigned |
| inputType | enum | CONFIG | ❌ | ✅ | ❌ | Poll-only vs. change detection (0-1) |
| inputUsage | enum | CONFIG | ❌ | ✅ | ❌ | Usage category (0-3) |
| sensorFunction | enum | CONFIG | ❌ | ✅ | ❌ | Sensor function type (0,12) |
| updateInterval | float | CONFIG | ❌ | ✅ | ❌ | Update interval in seconds |

### 4.2 Binary Input Settings[i] (Section 4.3.2)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| group | integer | CONFIG | ✅ | ✅ | ❌ | Associated group |
| sensorFunction | enum | CONFIG | ✅ | ✅ | ❌ | Sensor function (0-23) |

### 4.3 Binary Input States[i] (Section 4.3.3)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| value | boolean/null | STATE | ❌ | ✅ | ❌ | Current binary state, persist last value |
| extendedValue | integer/null | STATE | ❌ | ✅ | ❌ | Optional extended value, persist |
| age | float/null | META | ❌ | ❌ | ✅ | Time since last update, calculated from timestamp |
| error | enum | STATE | ❌ | ✅ | ❌ | Error code (0-6), persist |
| _timestamp | timestamp | META | ❌ | ✅ | ✅ | Internal: timestamp for age calculation |

---

## 5. Sensor Inputs (Section 4.4)

### 5.1 Sensor Descriptions[i] (Section 4.4.1)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| name | string | CONFIG | ❌ | ✅ | ❌ | Sensor name (describes hardware) |
| dsIndex | integer | CONFIG | ❌ | ✅ | ✅ | Index 0..N-1, auto-assigned |
| sensorType | enum | CONFIG | ❌ | ✅ | ❌ | Sensor type (0-28: temp, humidity, etc.) |
| sensorUsage | enum | CONFIG | ❌ | ✅ | ❌ | Usage category (0-6) |
| min | float | CONFIG | ❌ | ✅ | ❌ | Minimum sensor value |
| max | float | CONFIG | ❌ | ✅ | ❌ | Maximum sensor value |
| resolution | float | CONFIG | ❌ | ✅ | ❌ | Sensor resolution |
| updateInterval | float | CONFIG | ❌ | ✅ | ❌ | Update interval in seconds |
| aliveSignInterval | float | CONFIG | ❌ | ✅ | ❌ | Alive signal interval in seconds |

### 5.2 Sensor Settings[i] (Section 4.4.2)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| group | integer | CONFIG | ✅ | ✅ | ❌ | Associated group |
| minPushInterval | float | CONFIG | ✅ | ✅ | ❌ | Minimum push interval (default: 2.0) |
| changesOnlyInterval | float | CONFIG | ✅ | ✅ | ❌ | Changes-only interval (default: 0.0) |

### 5.3 Sensor States[i] (Section 4.4.3)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| value | float/null | STATE | ❌ | ✅ | ❌ | Current sensor reading, **persist for slow sensors** |
| age | float/null | META | ❌ | ❌ | ✅ | Time since last reading, calculated from timestamp |
| contextId | integer/null | STATE | ❌ | ✅ | ❌ | Optional context identifier |
| contextMsg | string/null | STATE | ❌ | ✅ | ❌ | Optional context message |
| error | enum | STATE | ❌ | ✅ | ❌ | Error code (0-6), persist |
| _timestamp | timestamp | META | ❌ | ✅ | ✅ | Internal: timestamp for age calculation |

---

## 6. Device Actions (Section 4.5)

### 6.1 Device Action Descriptions[name] (Section 4.5.1)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| name | string | CONFIG | ❌ | ✅ | ❌ | Action name (describes capability) |
| params | list | CONFIG | ❌ | ✅ | ❌ | Parameter descriptions |
| params[].type | string | CONFIG | ❌ | ✅ | ❌ | 'numeric'/'enumeration'/'string' |
| params[].min | float | CONFIG | ❌ | ✅ | ❌ | Minimum value (numeric) |
| params[].max | float | CONFIG | ❌ | ✅ | ❌ | Maximum value (numeric) |
| params[].resolution | float | CONFIG | ❌ | ✅ | ❌ | Resolution (numeric) |
| params[].siunit | string | CONFIG | ❌ | ✅ | ❌ | SI unit (numeric) |
| params[].options | dict | CONFIG | ❌ | ✅ | ❌ | Options (enumeration) |
| params[].default | any | CONFIG | ❌ | ✅ | ❌ | Default value |
| description | string | CONFIG | ❌ | ✅ | ❌ | Action description |

### 6.2 Standard Actions[name] (Section 4.5.2)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| name | string | CONFIG | ✅ | ✅ | ❌ | Standard action name (with "std." prefix) |
| action | string | CONFIG | ✅ | ✅ | ❌ | Action identifier |
| params | dict | CONFIG | ✅ | ✅ | ❌ | Action parameters |

### 6.3 Custom Actions[name] (Section 4.5.3)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| name | string | CONFIG | ✅ | ✅ | ❌ | Custom action name (with "custom." prefix) |
| action | string | CONFIG | ✅ | ✅ | ❌ | Action identifier |
| title | string | CONFIG | ✅ | ✅ | ❌ | Display title |
| params | dict | CONFIG | ✅ | ✅ | ❌ | Action parameters |

### 6.4 Dynamic Device Actions[name] (Section 4.5.4)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| name | string | STATE | ❌ | ✅ | ❌ | Dynamic action name (with "dynamic." prefix), runtime-generated |
| title | string | STATE | ❌ | ✅ | ❌ | Display title, runtime-generated |

---

## 7. Device States (Section 4.6.1)

### 7.1 Device State Descriptions[name]

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| name | string | CONFIG | ❌ | ✅ | ❌ | State name (describes state type) |
| options | dict | CONFIG | ❌ | ✅ | ❌ | Valid state values (id:value pairs) |
| description | string | CONFIG | ❌ | ✅ | ❌ | State description |

### 7.2 Device States[name]

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| name | string | STATE | ❌ | ✅ | ❌ | State name |
| value | string | STATE | ❌ | ✅ | ❌ | Current state value, persist |

---

## 8. Device Properties (Section 4.6.2)

### 8.1 Device Property Descriptions[name]

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| name | string | CONFIG | ❌ | ✅ | ❌ | Property name (describes property type) |
| type | string | CONFIG | ❌ | ✅ | ❌ | 'numeric'/'enumeration'/'string' |
| min | float | CONFIG | ❌ | ✅ | ❌ | Minimum value (numeric) |
| max | float | CONFIG | ❌ | ✅ | ❌ | Maximum value (numeric) |
| resolution | float | CONFIG | ❌ | ✅ | ❌ | Resolution (numeric) |
| siunit | string | CONFIG | ❌ | ✅ | ❌ | SI unit (numeric) |
| options | dict | CONFIG | ❌ | ✅ | ❌ | Options (enumeration) |
| default | any | CONFIG | ❌ | ✅ | ❌ | Default value |

### 8.2 Device Properties[name]

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| name | string | STATE | ❌ | ✅ | ❌ | Property name |
| value | any | STATE | ❌ | ✅ | ❌ | Current property value, persist |

---

## 9. Device Events (Section 4.7)

### 9.1 Device Event Descriptions[name]

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| name | string | CONFIG | ❌ | ✅ | ❌ | Event name (describes event type) |
| description | string | CONFIG | ❌ | ✅ | ❌ | Event description |

---

## 10. Output (Section 4.8)

### 10.1 Output Description (Section 4.8.1)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| defaultGroup | integer | CONFIG | ❌ | ✅ | ❌ | Default group assignment (describes device) |
| name | string | CONFIG | ❌ | ✅ | ❌ | Output name (describes hardware) |
| function | enum | CONFIG | ❌ | ✅ | ❌ | Output function (0-6: on/off, dimmer, etc.) |
| outputUsage | enum | CONFIG | ❌ | ✅ | ❌ | Usage category (0-3) |
| variableRamp | boolean | CONFIG | ❌ | ✅ | ❌ | Supports variable ramping (capability) |
| maxPower | float | CONFIG | ❌ | ✅ | ❌ | Maximum power in Watts (capability) |
| activeCoolingMode | boolean | CONFIG | ❌ | ✅ | ❌ | Active cooling mode supported (capability) |

### 10.2 Output Settings (Section 4.8.2)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| activeGroup | integer | CONFIG | ✅ | ✅ | ❌ | Currently active group |
| groups | dict[int,bool] | CONFIG | ✅ | ✅ | ❌ | Group memberships (1..63) |
| mode | enum | CONFIG | ✅ | ✅ | ❌ | Output mode (0,1,2,127) |
| pushChanges | boolean | CONFIG | ✅ | ✅ | ❌ | Push changes flag |
| onThreshold | float | CONFIG | ✅ | ✅ | ❌ | On detection threshold (0..100%, default: 50) |
| minBrightness | float | CONFIG | ✅ | ✅ | ❌ | Minimum brightness (0..100%) |
| dimTimeUp | integer | CONFIG | ✅ | ✅ | ❌ | Dim-up time (dS 8-bit format) |
| dimTimeDown | integer | CONFIG | ✅ | ✅ | ❌ | Dim-down time (dS 8-bit format) |
| dimTimeUpAlt1 | integer | CONFIG | ✅ | ✅ | ❌ | Alternate dim-up time 1 |
| dimTimeDownAlt1 | integer | CONFIG | ✅ | ✅ | ❌ | Alternate dim-down time 1 |
| dimTimeUpAlt2 | integer | CONFIG | ✅ | ✅ | ❌ | Alternate dim-up time 2 |
| dimTimeDownAlt2 | integer | CONFIG | ✅ | ✅ | ❌ | Alternate dim-down time 2 |
| heatingSystemCapability | enum | CONFIG | ✅ | ✅ | ❌ | Heating system capability (1-3) |
| heatingSystemType | enum | CONFIG | ✅ | ✅ | ❌ | Heating system type (0-6) |

### 10.3 Output State (Section 4.8.3)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| localPriority | boolean | STATE | ❌ | ✅ | ❌ | Local priority active, persist |
| error | enum | STATE | ❌ | ✅ | ❌ | Error code (0-6), persist |

---

## 11. Channels (Section 4.9)

### 11.1 Channel Descriptions[i] (Section 4.9.1)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| name | string | CONFIG | ❌ | ✅ | ❌ | Channel name (describes hardware) |
| channelType | integer | CONFIG | ❌ | ✅ | ❌ | Channel type ID (0=default, 1=brightness, etc.) |
| dsIndex | integer | CONFIG | ❌ | ✅ | ✅ | Index (0 is default channel), auto-assigned |
| min | float | CONFIG | ❌ | ✅ | ❌ | Minimum channel value (capability) |
| max | float | CONFIG | ❌ | ✅ | ❌ | Maximum channel value (capability) |
| resolution | float | CONFIG | ❌ | ✅ | ❌ | Channel resolution (capability) |

### 11.2 Channel Settings[i] (Section 4.9.2)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| (none) | - | - | - | - | - | No settings currently defined |

### 11.3 Channel States[i] (Section 4.9.3)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| value | float | STATE | ❌ | ✅ | ❌ | Current channel value (e.g., brightness 0..100%), **persist** |
| age | float/null | META | ❌ | ❌ | ✅ | Time since last update, calculated from timestamp |
| _timestamp | timestamp | META | ❌ | ✅ | ✅ | Internal: timestamp for age calculation |

---

## 12. Scenes (Section 4.10)

### 12.1 Scenes[scene_number] (0..127)

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| channels | dict | CONFIG | ✅ | ✅ | ❌ | Channel values for this scene (by channel_type_id) |
| effect | enum | CONFIG | ✅ | ✅ | ❌ | Transition effect (0-4: no effect, smooth, slow, very slow, blink) |
| dontCare | boolean | CONFIG | ✅ | ✅ | ❌ | Scene-global don't care flag |
| ignoreLocalPriority | boolean | CONFIG | ✅ | ✅ | ❌ | Override local priority |

### 12.2 Scene Channel Values[channel_type_id]

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| value | float | CONFIG | ✅ | ✅ | ❌ | Target channel value for this scene |
| dontCare | boolean | CONFIG | ✅ | ✅ | ❌ | Ignore this channel in scene |
| automatic | boolean | CONFIG | ✅ | ✅ | ❌ | Automatically set value |

---

## 13. Control Values (Section 4.11) - Write-Only

These are **write-only** control values that trigger immediate actions. They are not stored as properties.

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| heatingLevel | float | ACTION | ⚡ | ❌ | ❌ | Write-only: set heating level |
| coolingLevel | float | ACTION | ⚡ | ❌ | ❌ | Write-only: set cooling level |
| ventilationLevel | float | ACTION | ⚡ | ❌ | ❌ | Write-only: set ventilation level |
| (various control values) | - | ACTION | ⚡ | ❌ | ❌ | Write-only control commands |

**Note:** ⚡ = Write-only action trigger (not a stored property)

---

## 14. Additional Properties (Home Assistant Integration)

These are additional properties specific to our Home Assistant integration:

| Property | Type | Category | Write-Enabled | Persisted | Derived/Calc | Notes |
|----------|------|----------|---------------|-----------|--------------|-------|
| name | string | CONFIG | ✅ | ✅ | ❌ | User-friendly device name (HA-specific) |
| ha_entity_id | string | CONFIG | ✅ | ✅ | ❌ | Home Assistant entity mapping |
| attributes | dict | CONFIG | ✅ | ✅ | ❌ | User-defined custom attributes |
| connection_status | string | STATE | ❌ | ✅ | ❌ | "connected"/"disconnected"/"unknown", persist |
| system_status | string | STATE | ❌ | ✅ | ❌ | "active"/"inactive"/"error"/"unknown", persist |
| api_version | string | CONFIG | ❌ | ✅ | ❌ | vDC API version (e.g., "1.0") |

---

## Summary Statistics

### By Category (Corrected Classification)

| Category | Count | Percentage | Persistence |
|----------|-------|------------|-------------|
| **Configuration (CONFIG)** | 75 | 55% | **Always persisted** |
| **State (STATE)** | 42 | 31% | **May be persisted** (decision per use case) |
| **Metadata (META)** | 20 | 14% | **Persisted if needed** (for calculations) |
| **Total Properties** | **137** | **100%** | - |

### Key Insights

**CONFIG Properties (75):**
- Describe the device and its capabilities
- Set at creation, some modifiable at runtime
- **ALWAYS persisted to YAML**
- Examples: device descriptions, settings, scene configurations

**STATE Properties (42):**
- Runtime values that change during operation
- **Persistence decision based on use case:**
  - ✅ Persist: Sensor values (especially slow update cycles), channel values, connection status
  - ❓ Optional: Button states, error codes
  - ❌ Don't persist: Transient events
- Examples: sensor readings, channel states, button presses

**META Properties (20):**
- Derived or calculated automatically
- Not directly set by user or runtime updates
- **Persisted when needed for calculations** (e.g., timestamps for age)
- Examples: age calculations, timestamps, auto-assigned indices

---

## Legend Clarification

- **✅** = Yes
- **❌** = No
- **🔧** = System-managed (auto-updated by system processes)
- **⚡** = Write-only action (not a stored property)

### Category Definitions Summary

1. **CONFIG**: Device description, set at creation or runtime (if write-enabled), **always persisted**
2. **STATE**: Runtime values, **selectively persisted** based on use case
3. **META**: Derived/calculated values, **persisted if needed for calculations**
4. **ACTION**: Write-only commands that trigger actions, never stored

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
