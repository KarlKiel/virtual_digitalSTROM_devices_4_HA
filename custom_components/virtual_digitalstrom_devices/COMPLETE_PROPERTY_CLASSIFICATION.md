# Complete Property-by-Property Classification

This document provides a detailed classification of **every individual property** in the vDC specification, categorized as Configuration, State, or Metadata.

## Legend

- **CONFIG** = Configuration property (user-editable, persisted to YAML)
- **STATE** = State property (runtime value, NOT persisted)
- **META** = Metadata property (system-managed, auto-assigned, persisted)

---

## 1. Root Device Properties

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| dSUID | string | META | ❌ | ✅ | ✅ | 34 hex chars, auto-generated |
| device_id | string | META | ❌ | ✅ | ✅ | Internal UUID, auto-generated |
| created_at | timestamp | META | ❌ | ✅ | ✅ | Creation timestamp |
| updated_at | timestamp | META | ❌ | ✅ | 🔧 | Last config update timestamp |
| last_seen_at | timestamp | META | ❌ | ✅ | 🔧 | Last activity timestamp |

---

## 2. General Device Properties (Section 4.1.1)

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| primaryGroup | integer | CONFIG | ✅ | ✅ | ❌ | dS class number (1=Lights, 2=Blinds, etc.) |
| zoneID | integer | CONFIG | ✅ | ✅ | ❌ | Global dS Zone ID |
| progMode | boolean | STATE | ❌ | ❌ | ❌ | Programming mode active |
| modelFeatures | dict | CONFIG | ✅ | ✅ | ❌ | Feature flags (e.g., {"dimmable": true}) |
| currentConfigId | string | CONFIG | ✅ | ✅ | ❌ | Active configuration ID |
| configurations | list[string] | CONFIG | ✅ | ✅ | ❌ | Available configuration IDs |

---

## 3. Button Inputs (Section 4.2)

### 3.1 Button Input Descriptions[i] (Section 4.2.1)

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| name | string | META | ❌ | ✅ | ❌ | Button name (describes hardware) |
| dsIndex | integer | META | ❌ | ✅ | ✅ | Index 0..N-1, auto-assigned |
| supportsLocalKeyMode | boolean | META | ❌ | ✅ | ❌ | Hardware capability |
| buttonID | integer | META | ❌ | ✅ | ❌ | Optional button identifier |
| buttonType | enum | META | ❌ | ✅ | ❌ | Physical button type (0-6) |
| buttonElementID | enum | META | ❌ | ✅ | ❌ | Multi-contact element (0-8) |

### 3.2 Button Input Settings[i] (Section 4.2.2)

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| group | integer | CONFIG | ✅ | ✅ | ❌ | Associated group |
| function | integer | CONFIG | ✅ | ✅ | ❌ | Button function (0..15) |
| mode | enum | CONFIG | ✅ | ✅ | ❌ | Operation mode (0,2,5-12,255) |
| channel | integer | CONFIG | ✅ | ✅ | ❌ | Channel assignment (0 or 1..239) |
| setsLocalPriority | boolean | CONFIG | ✅ | ✅ | ❌ | Sets local priority flag |
| callsPresent | boolean | CONFIG | ✅ | ✅ | ❌ | Calls present flag |

### 3.3 Button Input States[i] (Section 4.2.3)

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| value | boolean/null | STATE | ❌ | ❌ | ❌ | Current button state |
| clickType | enum | STATE | ❌ | ❌ | ❌ | Last click type (0-14,255) |
| age | float/null | STATE | ❌ | ❌ | ❌ | Time since last event (seconds) |
| error | enum | STATE | ❌ | ❌ | ❌ | Error code (0-6) |
| actionId | integer | STATE | ❌ | ❌ | ❌ | Optional: scene call alternative |
| actionMode | enum | STATE | ❌ | ❌ | ❌ | Optional: action mode (0-2) |

---

## 4. Binary Inputs (Section 4.3)

### 4.1 Binary Input Descriptions[i] (Section 4.3.1)

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| name | string | META | ❌ | ✅ | ❌ | Input name (describes hardware) |
| dsIndex | integer | META | ❌ | ✅ | ✅ | Index 0..N-1, auto-assigned |
| inputType | enum | META | ❌ | ✅ | ❌ | Poll-only vs. change detection (0-1) |
| inputUsage | enum | META | ❌ | ✅ | ❌ | Usage category (0-3) |
| sensorFunction | enum | META | ❌ | ✅ | ❌ | Sensor function type (0,12) |
| updateInterval | float | META | ❌ | ✅ | ❌ | Update interval in seconds |

### 4.2 Binary Input Settings[i] (Section 4.3.2)

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| group | integer | CONFIG | ✅ | ✅ | ❌ | Associated group |
| sensorFunction | enum | CONFIG | ✅ | ✅ | ❌ | Sensor function (0-23) |

### 4.3 Binary Input States[i] (Section 4.3.3)

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| value | boolean/null | STATE | ❌ | ❌ | ❌ | Current binary state |
| extendedValue | integer/null | STATE | ❌ | ❌ | ❌ | Optional extended value |
| age | float/null | STATE | ❌ | ❌ | ❌ | Time since last update (seconds) |
| error | enum | STATE | ❌ | ❌ | ❌ | Error code (0-6) |

---

## 5. Sensor Inputs (Section 4.4)

### 5.1 Sensor Descriptions[i] (Section 4.4.1)

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| name | string | META | ❌ | ✅ | ❌ | Sensor name (describes hardware) |
| dsIndex | integer | META | ❌ | ✅ | ✅ | Index 0..N-1, auto-assigned |
| sensorType | enum | META | ❌ | ✅ | ❌ | Sensor type (0-28: temp, humidity, etc.) |
| sensorUsage | enum | META | ❌ | ✅ | ❌ | Usage category (0-6) |
| min | float | META | ❌ | ✅ | ❌ | Minimum sensor value |
| max | float | META | ❌ | ✅ | ❌ | Maximum sensor value |
| resolution | float | META | ❌ | ✅ | ❌ | Sensor resolution |
| updateInterval | float | META | ❌ | ✅ | ❌ | Update interval in seconds |
| aliveSignInterval | float | META | ❌ | ✅ | ❌ | Alive signal interval in seconds |

### 5.2 Sensor Settings[i] (Section 4.4.2)

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| group | integer | CONFIG | ✅ | ✅ | ❌ | Associated group |
| minPushInterval | float | CONFIG | ✅ | ✅ | ❌ | Minimum push interval (default: 2.0) |
| changesOnlyInterval | float | CONFIG | ✅ | ✅ | ❌ | Changes-only interval (default: 0.0) |

### 5.3 Sensor States[i] (Section 4.4.3)

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| value | float/null | STATE | ❌ | ❌ | ❌ | Current sensor reading |
| age | float/null | STATE | ❌ | ❌ | ❌ | Time since last reading (seconds) |
| contextId | integer/null | STATE | ❌ | ❌ | ❌ | Optional context identifier |
| contextMsg | string/null | STATE | ❌ | ❌ | ❌ | Optional context message |
| error | enum | STATE | ❌ | ❌ | ❌ | Error code (0-6) |

---

## 6. Device Actions (Section 4.5)

### 6.1 Device Action Descriptions[name] (Section 4.5.1)

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| name | string | META | ❌ | ✅ | ❌ | Action name |
| params | list | META | ❌ | ✅ | ❌ | Parameter descriptions |
| params[].type | string | META | ❌ | ✅ | ❌ | 'numeric'/'enumeration'/'string' |
| params[].min | float | META | ❌ | ✅ | ❌ | Minimum value (numeric) |
| params[].max | float | META | ❌ | ✅ | ❌ | Maximum value (numeric) |
| params[].resolution | float | META | ❌ | ✅ | ❌ | Resolution (numeric) |
| params[].siunit | string | META | ❌ | ✅ | ❌ | SI unit (numeric) |
| params[].options | dict | META | ❌ | ✅ | ❌ | Options (enumeration) |
| params[].default | any | META | ❌ | ✅ | ❌ | Default value |
| description | string | META | ❌ | ✅ | ❌ | Action description |

### 6.2 Standard Actions[name] (Section 4.5.2)

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| name | string | CONFIG | ✅ | ✅ | ❌ | Standard action name (with "std." prefix) |
| action | string | CONFIG | ✅ | ✅ | ❌ | Action identifier |
| params | dict | CONFIG | ✅ | ✅ | ❌ | Action parameters |

### 6.3 Custom Actions[name] (Section 4.5.3)

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| name | string | CONFIG | ✅ | ✅ | ❌ | Custom action name (with "custom." prefix) |
| action | string | CONFIG | ✅ | ✅ | ❌ | Action identifier |
| title | string | CONFIG | ✅ | ✅ | ❌ | Display title |
| params | dict | CONFIG | ✅ | ✅ | ❌ | Action parameters |

### 6.4 Dynamic Device Actions[name] (Section 4.5.4)

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| name | string | STATE | ❌ | ❌ | ❌ | Dynamic action name (with "dynamic." prefix) |
| title | string | STATE | ❌ | ❌ | ❌ | Display title |

---

## 7. Device States (Section 4.6.1)

### 7.1 Device State Descriptions[name]

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| name | string | META | ❌ | ✅ | ❌ | State name |
| options | dict | META | ❌ | ✅ | ❌ | Valid state values (id:value pairs) |
| description | string | META | ❌ | ✅ | ❌ | State description |

### 7.2 Device States[name]

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| name | string | STATE | ❌ | ❌ | ❌ | State name |
| value | string | STATE | ❌ | ❌ | ❌ | Current state value |

---

## 8. Device Properties (Section 4.6.2)

### 8.1 Device Property Descriptions[name]

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| name | string | META | ❌ | ✅ | ❌ | Property name |
| type | string | META | ❌ | ✅ | ❌ | 'numeric'/'enumeration'/'string' |
| min | float | META | ❌ | ✅ | ❌ | Minimum value (numeric) |
| max | float | META | ❌ | ✅ | ❌ | Maximum value (numeric) |
| resolution | float | META | ❌ | ✅ | ❌ | Resolution (numeric) |
| siunit | string | META | ❌ | ✅ | ❌ | SI unit (numeric) |
| options | dict | META | ❌ | ✅ | ❌ | Options (enumeration) |
| default | any | META | ❌ | ✅ | ❌ | Default value |

### 8.2 Device Properties[name]

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| name | string | STATE | ❌ | ❌ | ❌ | Property name |
| value | any | STATE | ❌ | ❌ | ❌ | Current property value |

---

## 9. Device Events (Section 4.7)

### 9.1 Device Event Descriptions[name]

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| name | string | META | ❌ | ✅ | ❌ | Event name |
| description | string | META | ❌ | ✅ | ❌ | Event description |

---

## 10. Output (Section 4.8)

### 10.1 Output Description (Section 4.8.1)

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| defaultGroup | integer | META | ❌ | ✅ | ❌ | Default group assignment |
| name | string | META | ❌ | ✅ | ❌ | Output name (describes hardware) |
| function | enum | META | ❌ | ✅ | ❌ | Output function (0-6: on/off, dimmer, etc.) |
| outputUsage | enum | META | ❌ | ✅ | ❌ | Usage category (0-3) |
| variableRamp | boolean | META | ❌ | ✅ | ❌ | Supports variable ramping |
| maxPower | float | META | ❌ | ✅ | ❌ | Maximum power in Watts |
| activeCoolingMode | boolean | META | ❌ | ✅ | ❌ | Active cooling mode supported |

### 10.2 Output Settings (Section 4.8.2)

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
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

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| localPriority | boolean | STATE | ❌ | ❌ | ❌ | Local priority active |
| error | enum | STATE | ❌ | ❌ | ❌ | Error code (0-6) |

---

## 11. Channels (Section 4.9)

### 11.1 Channel Descriptions[i] (Section 4.9.1)

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| name | string | META | ❌ | ✅ | ❌ | Channel name (describes hardware) |
| channelType | integer | META | ❌ | ✅ | ❌ | Channel type ID (0=default, 1=brightness, etc.) |
| dsIndex | integer | META | ❌ | ✅ | ✅ | Index (0 is default channel), auto-assigned |
| min | float | META | ❌ | ✅ | ❌ | Minimum channel value |
| max | float | META | ❌ | ✅ | ❌ | Maximum channel value |
| resolution | float | META | ❌ | ✅ | ❌ | Channel resolution |

### 11.2 Channel Settings[i] (Section 4.9.2)

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| (none) | - | - | - | - | - | No settings currently defined |

### 11.3 Channel States[i] (Section 4.9.3)

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| value | float | STATE | ❌ | ❌ | ❌ | Current channel value (e.g., brightness 0..100%) |
| age | float/null | STATE | ❌ | ❌ | ❌ | Time since last update (null if not yet applied) |

---

## 12. Scenes (Section 4.10)

### 12.1 Scenes[scene_number] (0..127)

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| channels | dict | CONFIG | ✅ | ✅ | ❌ | Channel values for this scene (by channel_type_id) |
| effect | enum | CONFIG | ✅ | ✅ | ❌ | Transition effect (0-4: no effect, smooth, slow, very slow, blink) |
| dontCare | boolean | CONFIG | ✅ | ✅ | ❌ | Scene-global don't care flag |
| ignoreLocalPriority | boolean | CONFIG | ✅ | ✅ | ❌ | Override local priority |

### 12.2 Scene Channel Values[channel_type_id]

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| value | float | CONFIG | ✅ | ✅ | ❌ | Target channel value for this scene |
| dontCare | boolean | CONFIG | ✅ | ✅ | ❌ | Ignore this channel in scene |
| automatic | boolean | CONFIG | ✅ | ✅ | ❌ | Automatically set value |

---

## 13. Control Values (Section 4.11) - Write-Only

These are **write-only** control values that trigger immediate actions. They are not stored as properties.

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| heatingLevel | float | ACTION | ⚡ | ❌ | ❌ | Write-only: set heating level |
| coolingLevel | float | ACTION | ⚡ | ❌ | ❌ | Write-only: set cooling level |
| ventilationLevel | float | ACTION | ⚡ | ❌ | ❌ | Write-only: set ventilation level |
| (various control values) | - | ACTION | ⚡ | ❌ | ❌ | Write-only control commands |

**Note:** ⚡ = Write-only action trigger (not a stored property)

---

## 14. Additional Properties (Home Assistant Integration)

These are additional properties specific to our Home Assistant integration:

| Property | Type | Category | Editable | Persisted | Auto-Gen | Notes |
|----------|------|----------|----------|-----------|----------|-------|
| name | string | CONFIG | ✅ | ✅ | ❌ | User-friendly device name (HA-specific) |
| ha_entity_id | string | CONFIG | ✅ | ✅ | ❌ | Home Assistant entity mapping |
| attributes | dict | CONFIG | ✅ | ✅ | ❌ | User-defined custom attributes |
| connection_status | string | META | ❌ | ✅ | 🔧 | "connected"/"disconnected"/"unknown" |
| system_status | string | META | ❌ | ✅ | 🔧 | "active"/"inactive"/"error"/"unknown" |
| api_version | string | META | ❌ | ✅ | ✅ | vDC API version (e.g., "1.0") |

---

## Summary Statistics

### By Category

| Category | Count | Percentage |
|----------|-------|------------|
| **Configuration (CONFIG)** | 52 | 38% |
| **State (STATE)** | 32 | 23% |
| **Metadata (META)** | 53 | 39% |
| **Total Properties** | **137** | **100%** |

### By Persistence

| Persistence | Count | Percentage |
|-------------|-------|------------|
| **Persisted to YAML** | 105 | 77% |
| **NOT Persisted (Ephemeral)** | 32 | 23% |

### By Editability

| Editability | Count | Percentage |
|-------------|-------|------------|
| **User Editable** | 52 | 38% |
| **NOT User Editable** | 85 | 62% |

### By Auto-Generation

| Auto-Generation | Count | Percentage |
|-----------------|-------|------------|
| **Auto-Generated** | 18 | 13% |
| **System-Managed** | 8 | 6% |
| **User/Runtime Set** | 111 | 81% |

---

## Legend Clarification

- **✅** = Yes
- **❌** = No
- **🔧** = System-managed (auto-updated by system processes)
- **⚡** = Write-only action (not stored)

### Category Definitions

1. **CONFIG**: User-editable configuration properties that are persisted to YAML
2. **STATE**: Runtime state values that are NOT persisted (ephemeral)
3. **META**: System-managed metadata that is auto-assigned or describes hardware capabilities
4. **ACTION**: Write-only control values that trigger immediate actions

---

## Implementation Notes

### Serialization Methods

Based on this classification, the implementation should provide:

1. **`to_config_dict()`**: Serialize only CONFIG + META properties → YAML persistence
2. **`to_state_dict()`**: Serialize only STATE properties → Home Assistant state updates
3. **`to_full_vdc_dict()`**: Serialize ALL properties → Complete vDC API tree

### Update Methods

Based on this classification, the implementation should provide:

1. **`update_configuration(**kwargs)`**: Update CONFIG properties only
2. **`update_state(**kwargs)`**: Update STATE properties only
3. **`update_metadata(**kwargs)`**: Update META properties (system-managed only)
4. **`invoke_action(name, **params)`**: Execute ACTION control values

---

**This complete property-by-property classification should be reviewed before proceeding with implementation.**
