# Property Classification Proposal for Virtual digitalSTROM Devices

## Executive Summary

This document proposes a clear distinction between three types of properties in the virtual digitalSTROM device system:

1. **Configuration Properties** - User-managed, persistent settings
2. **State Properties** - Runtime values reflecting current device state
3. **Metadata Properties** - System-managed, auto-assigned values

---

## 1. Configuration Properties

**Definition:** Properties that are set by the user through a UI and persist across restarts. These define how the device should behave and what it represents.

**Characteristics:**
- ✅ User-editable (via UI)
- ✅ Persisted to YAML configuration file
- ✅ Rarely change during normal operation
- ✅ Validated before saving
- ❌ Not updated by runtime processes

### 1.1 Device Configuration

**From VirtualDevice class:**
```python
# Basic Identity
- name: str                    # User-friendly device name
- ha_entity_id: str           # Home Assistant entity mapping
- zone_id: int                # Room/zone assignment

# Device Class Configuration
- group_id: int               # digitalSTROM group/class (Yellow/Lights, Gray/Blinds, etc.)
```

**From vDC Properties:**
```python
# General Device Properties (Section 4.1.1)
- primaryGroup: int           # dS class number (1=Lights, 2=Blinds, etc.)
- zoneID: int                 # Global dS Zone ID
- modelFeatures: dict         # Feature flags (e.g., {"dimmable": true})
- configurations: list[str]   # Available configuration IDs
- currentConfigId: str        # Active configuration

# Custom Attributes
- attributes: dict            # User-defined key-value pairs
```

### 1.2 Output Configuration

**Output Settings (Section 4.8.2):**
```python
- activeGroup: int                    # Currently active group
- groups: dict[int, bool]            # Group memberships (1..63)
- mode: int                          # Output mode (0,1,2,127)
- onThreshold: float                 # On detection threshold (0..100%)
- minBrightness: float               # Minimum brightness (0..100%)
- dimTimeUp: int                     # Dim-up timing
- dimTimeDown: int                   # Dim-down timing
- dimTimeUpAlt1/2: int              # Alternate dim timings
- dimTimeDownAlt1/2: int
- heatingSystemCapability: int       # For heating devices
- heatingSystemType: int
```

### 1.3 Input Configuration

**Button Input Settings (Section 4.2.2):**
```python
- group: int                         # Associated group
- function: int                      # Button function (0..15)
- mode: int                          # Operation mode
- channel: int                       # Channel assignment
- setsLocalPriority: bool
- callsPresent: bool
```

**Sensor Settings (Section 4.4.2):**
```python
- group: int                         # Associated group
- minPushInterval: float            # Minimum push interval (default: 2.0)
- changesOnlyInterval: float        # Changes-only interval (default: 0.0)
```

### 1.4 Scene Configuration

**Scene Definitions (Section 4.10):**
```python
# Per scene (0..127)
- channels: dict[int, SceneValue]   # Channel values for this scene
  - value: float                     # Target value
  - dontCare: bool                   # Ignore this channel
  - automatic: bool                  # Automatically set value
- effect: int                        # Transition effect (0-4)
- dontCare: bool                     # Scene-global don't care
- ignoreLocalPriority: bool         # Override local priority
```

---

## 2. State Properties

**Definition:** Properties that reflect the current runtime state of the device. These change frequently during operation and are not persisted to configuration.

**Characteristics:**
- ❌ Not directly user-editable
- ❌ Not persisted to YAML (ephemeral)
- ✅ Updated frequently at runtime
- ✅ Reflect current device status
- ✅ May trigger Home Assistant state updates

### 2.1 Output State

**Output State (Section 4.8.3):**
```python
- localPriority: bool               # Local priority active
- error: int                        # Error code (0-6)
```

### 2.2 Channel States

**Channel States (Section 4.9.2):**
```python
# Per channel (0..N)
- value: float                      # Current channel value
- age: float                        # Time since last update (null if not applied)
```

**Common channel values:**
- Brightness (channel 1): 0..100%
- Hue (channel 2): 0..360°
- Saturation (channel 3): 0..100%
- Color Temperature (channel 4): Kelvin or 0..100%
- Shade Position (channel 7): 0..100%
- Shade Angle (channel 8): 0..100%

### 2.3 Input States

**Button Input States (Section 4.2.3):**
```python
- value: bool | null                # Current button state
- clickType: int                    # Last click type (0-14, 255)
- age: float | null                 # Time since last event
- error: int                        # Error code (0-6)
- actionId: int (optional)          # Alternative scene call
- actionMode: int (optional)        # Alternative action mode
```

**Binary Input States (Section 4.3.3):**
```python
- value: bool | null                # Current binary state
- extendedValue: int | null         # Extended value if supported
- age: float | null                 # Time since last update
- error: int                        # Error code (0-6)
```

**Sensor States (Section 4.4.3):**
```python
- value: float | null               # Current sensor reading
- age: float | null                 # Time since last reading
- contextId: int | null             # Context identifier
- contextMsg: str | null            # Context message
- error: int                        # Error code (0-6)
```

### 2.4 Device States

**Custom Device States (Section 4.6.2):**
```python
# By name (user-defined)
- name: str                         # State name
- value: str                        # State value (from options)
```

### 2.5 Device Properties

**Custom Device Properties (Section 4.6.1):**
```python
# By name (user-defined runtime properties)
- name: str                         # Property name
- value: str | float | int | bool   # Current value
```

---

## 3. Metadata Properties

**Definition:** System-managed properties that are automatically assigned and maintained. These are not directly editable by users or runtime processes.

**Characteristics:**
- ❌ Not user-editable
- ✅ Auto-generated/assigned by system
- ✅ Persisted to YAML
- ✅ Read-only for display purposes
- ✅ May be updated by system events

### 3.1 Device Identifiers

**From VirtualDevice:**
```python
- device_id: str                    # Auto-generated UUID (unique device identifier)
- dsid: str                         # Auto-generated dSUID (34 hex chars in vDC spec)
```

### 3.2 Timestamps and Lifecycle

**Proposed additions:**
```python
- created_at: str                   # ISO timestamp when device was created
- updated_at: str                   # ISO timestamp of last configuration update
- last_seen_at: str                 # ISO timestamp of last activity
```

### 3.3 System Status

**Proposed additions:**
```python
- system_status: str                # "active", "inactive", "error", "unknown"
- connection_status: str            # "connected", "disconnected", "unknown"
- api_version: str                  # vDC API version (e.g., "1.0")
```

### 3.4 Descriptions (Read-only Metadata)

**Button Input Descriptions (Section 4.2.1):**
```python
- name: str                         # Button name
- dsIndex: int                      # Index (0..N-1)
- supportsLocalKeyMode: bool
- buttonID: int
- buttonType: int                   # ButtonType enum
- buttonElementID: int              # ButtonElementID enum
```

**Binary Input Descriptions (Section 4.3.1):**
```python
- name: str                         # Input name
- dsIndex: int                      # Index (0..N-1)
- inputType: int                    # Poll/change detection
- inputUsage: int                   # Usage field
- sensorFunction: int               # Sensor function type
- updateInterval: float             # Update interval in seconds
```

**Sensor Descriptions (Section 4.4.1):**
```python
- name: str                         # Sensor name
- dsIndex: int                      # Index (0..N-1)
- sensorType: int                   # Type (temp, humidity, etc.)
- sensorUsage: int                  # Usage field
- min: float                        # Minimum value
- max: float                        # Maximum value
- resolution: float                 # Resolution
- updateInterval: float             # Update interval in seconds
- aliveSignInterval: float          # Alive signal interval
```

**Output Description (Section 4.8.1):**
```python
- defaultGroup: int                 # Default group assignment
- name: str                         # Output name
- function: int                     # Output function (0-6)
- outputUsage: int                  # Usage field
- variableRamp: bool               # Supports variable ramping
- maxPower: float                  # Maximum power in Watts
- activeCoolingMode: bool          # Active cooling mode
```

**Channel Descriptions (Section 4.9.1):**
```python
- name: str                         # Channel name
- channelType: int                  # Channel type ID
- dsIndex: int                      # Index (0 is default)
- min: float                        # Minimum value
- max: float                        # Maximum value
- resolution: float                 # Resolution
```

---

## 4. Property Access Control Matrix

| Property Category | User Editable | Runtime Writable | Persisted | Auto-Generated |
|-------------------|---------------|------------------|-----------|----------------|
| **Configuration** | ✅ Yes | ❌ No | ✅ Yes | ❌ No |
| **State** | ❌ No | ✅ Yes | ❌ No | ❌ No |
| **Metadata** | ❌ No | ❌ No | ✅ Yes | ✅ Yes |

---

## 5. Proposed Class Structure

### 5.1 VirtualDevice (Enhanced)

```python
@dataclass
class VirtualDevice:
    """Virtual digitalSTROM device with property classification."""
    
    # === METADATA (Auto-generated, Read-only) ===
    device_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dsid: str = field(default_factory=lambda: generate_dsuid())
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_seen_at: str | None = None
    api_version: str = "1.0"
    
    # === CONFIGURATION (User-editable, Persisted) ===
    name: str = ""
    group_id: int = 0
    ha_entity_id: str = ""
    zone_id: int = 0
    
    # Configuration objects
    output_settings: OutputSettings | None = None
    button_settings: list[ButtonInputSettings] = field(default_factory=list)
    sensor_settings: list[SensorSettings] = field(default_factory=list)
    scene_configs: dict[int, Scene] = field(default_factory=dict)
    
    # User-defined configuration
    attributes: dict[str, Any] = field(default_factory=dict)
    
    # === STATE (Runtime, NOT persisted) ===
    # Note: These are NOT included in to_dict() for YAML persistence
    _runtime_state: DeviceRuntimeState = field(default_factory=DeviceRuntimeState, repr=False)
```

### 5.2 DeviceRuntimeState (New Class)

```python
@dataclass
class DeviceRuntimeState:
    """Runtime state properties (not persisted)."""
    
    # Output state
    output_state: OutputState | None = None
    
    # Channel states
    channel_states: dict[int, ChannelState] = field(default_factory=dict)
    
    # Input states
    button_states: dict[int, ButtonInputState] = field(default_factory=dict)
    binary_input_states: dict[int, BinaryInputState] = field(default_factory=dict)
    sensor_states: dict[int, SensorState] = field(default_factory=dict)
    
    # Device states
    device_states: dict[str, str] = field(default_factory=dict)
    device_properties: dict[str, Any] = field(default_factory=dict)
    
    # System status
    connection_status: str = "unknown"
    system_status: str = "unknown"
```

### 5.3 Serialization Methods

```python
def to_config_dict(self) -> dict[str, Any]:
    """Serialize ONLY configuration and metadata for YAML persistence."""
    return {
        # Metadata
        "device_id": self.device_id,
        "dsid": self.dsid,
        "created_at": self.created_at,
        "updated_at": self.updated_at,
        "api_version": self.api_version,
        
        # Configuration
        "name": self.name,
        "group_id": int(self.group_id),
        "ha_entity_id": self.ha_entity_id,
        "zone_id": self.zone_id,
        "attributes": self.attributes,
        
        # Configuration objects
        "output_settings": self.output_settings.to_dict() if self.output_settings else None,
        "scene_configs": {k: v.to_dict() for k, v in self.scene_configs.items()},
        # ... other config objects
    }

def to_state_dict(self) -> dict[str, Any]:
    """Serialize ONLY current runtime state (for Home Assistant updates)."""
    return {
        "device_id": self.device_id,
        "output_state": self._runtime_state.output_state.to_dict() if self._runtime_state.output_state else None,
        "channel_states": {k: v.to_dict() for k, v in self._runtime_state.channel_states.items()},
        "connection_status": self._runtime_state.connection_status,
        # ... other state values
    }

def to_full_vdc_dict(self) -> dict[str, Any]:
    """Serialize complete vDC property tree (config + state + metadata)."""
    return {
        "dSUID": self.dsid,
        # ... complete vDC property tree including all sections
    }
```

---

## 6. Update Operations

### 6.1 Configuration Update

```python
def update_configuration(self, **kwargs) -> None:
    """Update configuration properties (user-editable)."""
    # Only allow updating configuration properties
    allowed_keys = {
        'name', 'ha_entity_id', 'zone_id', 'attributes',
        'output_settings', 'scene_configs', # etc.
    }
    
    for key, value in kwargs.items():
        if key in allowed_keys and hasattr(self, key):
            setattr(self, key, value)
    
    # Update metadata
    self.updated_at = datetime.utcnow().isoformat()
    
    # Persist to YAML
    self._save_to_storage()
```

### 6.2 State Update

```python
def update_state(self, **kwargs) -> None:
    """Update runtime state properties (NOT persisted)."""
    # Update runtime state
    for key, value in kwargs.items():
        if hasattr(self._runtime_state, key):
            setattr(self._runtime_state, key, value)
    
    # Update last seen
    self.last_seen_at = datetime.utcnow().isoformat()
    
    # Notify Home Assistant of state change
    self._notify_ha_state_change()
```

### 6.3 Metadata Update

```python
def update_metadata(self, **kwargs) -> None:
    """Update metadata properties (system-managed)."""
    # Only system can update these
    metadata_keys = {
        'last_seen_at', 'connection_status', 'system_status'
    }
    
    for key, value in kwargs.items():
        if key in metadata_keys and hasattr(self, key):
            setattr(self, key, value)
    
    # Persist to YAML (metadata is saved)
    self._save_to_storage()
```

---

## 7. Summary Table

### Property-by-Property Classification

| Property | Category | User Edit | Runtime Update | Persisted | Auto-Gen |
|----------|----------|-----------|----------------|-----------|----------|
| device_id | Metadata | ❌ | ❌ | ✅ | ✅ |
| dsid | Metadata | ❌ | ❌ | ✅ | ✅ |
| created_at | Metadata | ❌ | ❌ | ✅ | ✅ |
| updated_at | Metadata | ❌ | 🔧 System | ✅ | ✅ |
| last_seen_at | Metadata | ❌ | 🔧 System | ✅ | ❌ |
| name | Config | ✅ | ❌ | ✅ | ❌ |
| group_id | Config | ✅ | ❌ | ✅ | ❌ |
| ha_entity_id | Config | ✅ | ❌ | ✅ | ❌ |
| zone_id | Config | ✅ | ❌ | ✅ | ❌ |
| attributes | Config | ✅ | ❌ | ✅ | ❌ |
| output_settings | Config | ✅ | ❌ | ✅ | ❌ |
| scene_configs | Config | ✅ | ❌ | ✅ | ❌ |
| channel_states | State | ❌ | ✅ | ❌ | ❌ |
| output_state | State | ❌ | ✅ | ❌ | ❌ |
| sensor_states | State | ❌ | ✅ | ❌ | ❌ |
| connection_status | Metadata | ❌ | 🔧 System | ✅ | ❌ |

Legend: 🔧 = System-managed updates

---

## 8. Implementation Recommendations

### 8.1 Immediate Actions

1. **Separate configuration from state** in VirtualDevice class
2. **Create DeviceRuntimeState** class for ephemeral state
3. **Implement separate serialization methods**:
   - `to_config_dict()` for YAML persistence
   - `to_state_dict()` for HA state updates
   - `to_full_vdc_dict()` for complete vDC API compliance
4. **Add update methods** with proper access control

### 8.2 Future Enhancements

1. **Validation layer** for configuration changes
2. **State change events** for HA integration
3. **Metadata tracking** for diagnostics
4. **Configuration versioning** for migrations
5. **State history** (optional, for debugging)

---

## 9. Questions for Review

1. **Timestamps**: Should we add created_at, updated_at, last_seen_at to metadata?
2. **Connection tracking**: Should connection_status and system_status be part of metadata?
3. **State persistence**: Should any state properties be optionally persisted (e.g., last known channel values)?
4. **Description objects**: Should button/sensor/channel descriptions be in configuration or metadata?
5. **Validation**: What level of validation should be enforced on configuration updates?

---

## 10. Next Steps

After review and approval of this proposal:

1. ✅ **Refactor VirtualDevice** class with property separation
2. ✅ **Create DeviceRuntimeState** class
3. ✅ **Implement update methods** with access control
4. ✅ **Update DeviceStorage** to handle new structure
5. ✅ **Create UI flow** for configuration management
6. ✅ **Implement state update mechanisms** for runtime values
7. ✅ **Add validation layer** for configuration changes
8. ✅ **Update documentation** with new structure

---

**Please review this proposal and provide feedback before implementation begins.**
