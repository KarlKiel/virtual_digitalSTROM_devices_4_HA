"""
vDC (Virtual Device Connector) Property Classes

This module provides Python classes representing all vDC device properties
as defined in the vDC-API-properties specification (July 2022).

These classes can be used to construct virtual digitalSTROM devices (vdSD)
with proper type safety and validation.

For dSUID generation, use the dsuid_generator module which implements
the dSUID generation rules from ds-basics.pdf Chapter 13.3.
"""

from typing import Optional, List, Dict, Union, Any
from enum import Enum
from dataclasses import dataclass, field

# Note: dsuid_generator module is available for dSUID generation
# from dsuid_generator import generate_dsuid


# =============================================================================
# Enumerations
# =============================================================================

class ButtonType(Enum):
    """Type of physical button"""
    UNDEFINED = 0
    SINGLE_PUSHBUTTON = 1
    TWO_WAY_PUSHBUTTON = 2
    FOUR_WAY_NAVIGATION = 3
    FOUR_WAY_NAVIGATION_WITH_CENTER = 4
    EIGHT_WAY_NAVIGATION_WITH_CENTER = 5
    ON_OFF_SWITCH = 6


class ButtonElementID(Enum):
    """Element of multi-contact button"""
    CENTER = 0
    DOWN = 1
    UP = 2
    LEFT = 3
    RIGHT = 4
    UPPER_LEFT = 5
    LOWER_LEFT = 6
    UPPER_RIGHT = 7
    LOWER_RIGHT = 8


class ButtonMode(Enum):
    """Button operation mode"""
    INACTIVE = 255
    STANDARD = 0
    PRESENCE = 2
    BUTTON1_DOWN = 5
    BUTTON2_DOWN = 6
    BUTTON3_DOWN = 7
    BUTTON4_DOWN = 8
    BUTTON1_UP = 9
    BUTTON2_UP = 10
    BUTTON3_UP = 11
    BUTTON4_UP = 12


class ClickType(Enum):
    """Button click types"""
    TIP_1X = 0
    TIP_2X = 1
    TIP_3X = 2
    TIP_4X = 3
    HOLD_START = 4
    HOLD_REPEAT = 5
    HOLD_END = 6
    CLICK_1X = 7
    CLICK_2X = 8
    CLICK_3X = 9
    SHORT_LONG = 10
    LOCAL_OFF = 11
    LOCAL_ON = 12
    SHORT_SHORT_LONG = 13
    LOCAL_STOP = 14
    IDLE = 255


class InputType(Enum):
    """Binary input type"""
    POLL_ONLY = 0
    DETECTS_CHANGES = 1


class InputUsage(Enum):
    """Usage field for binary input"""
    UNDEFINED = 0
    ROOM_CLIMATE = 1
    OUTDOOR_CLIMATE = 2
    CLIMATE_SETTING = 3


class BinarySensorFunction(Enum):
    """Binary sensor function types"""
    APP_MODE = 0
    PRESENCE = 1
    LIGHT = 2
    PRESENCE_IN_DARKNESS = 3
    TWILIGHT = 4
    MOTION_DETECTOR = 5
    MOTION_IN_DARKNESS = 6
    SMOKE_DETECTOR = 7
    WIND_MONITOR = 8
    RAIN_MONITOR = 9
    SUN_RADIATION = 10
    THERMOSTAT = 11
    BATTERY_LOW = 12
    WINDOW_CONTACT = 13
    DOOR_CONTACT = 14
    WINDOW_HANDLE = 15
    GARAGE_DOOR_CONTACT = 16
    SUN_PROTECTION = 17
    FROST_DETECTION = 18
    HEATING_SYSTEM_ENABLED = 19
    HEATING_CHANGEOVER = 20
    INITIALIZATION_STATUS = 21
    MALFUNCTION = 22
    SERVICE = 23


class SensorType(Enum):
    """Physical unit types for sensors"""
    NONE = 0
    TEMPERATURE = 1  # °C
    HUMIDITY = 2  # %
    ILLUMINATION = 3  # lux
    VOLTAGE = 4  # V
    CO_CONCENTRATION = 5  # ppm
    RADON_ACTIVITY = 6  # Bq/m³
    GAS_TYPE = 7
    PARTICLES_10 = 8  # μg/m³
    PARTICLES_2_5 = 9  # μg/m³
    PARTICLES_1 = 10  # μg/m³
    ROOM_SETPOINT = 11  # 0..100%
    FAN_SPEED = 12  # 0..1
    WIND_SPEED = 13  # m/s
    ACTIVE_POWER = 14  # W
    ELECTRIC_CURRENT = 15  # A
    ENERGY_METER = 16  # kWh
    APPARENT_POWER = 17  # VA
    AIR_PRESSURE = 18  # hPa
    WIND_DIRECTION = 19  # degrees
    SOUND_PRESSURE = 20  # dB
    PRECIPITATION = 21  # mm/m²
    CO2_CONCENTRATION = 22  # ppm
    WIND_GUST_SPEED = 23  # m/s
    WIND_GUST_DIRECTION = 24  # degrees
    GENERATED_POWER = 25  # W
    GENERATED_ENERGY = 26  # kWh
    WATER_QUANTITY = 27  # l
    WATER_FLOW_RATE = 28  # l/s


class SensorUsage(Enum):
    """Usage field for sensors"""
    UNDEFINED = 0
    ROOM = 1
    OUTDOOR = 2
    USER_INTERACTION = 3
    DEVICE_LEVEL_MEASUREMENT = 4
    DEVICE_LEVEL_LAST_RUN = 5
    DEVICE_LEVEL_AVERAGE = 6


class OutputFunction(Enum):
    """Output function types"""
    ON_OFF_ONLY = 0
    DIMMER = 1
    POSITIONAL = 2
    DIMMER_WITH_COLOR_TEMP = 3
    FULL_COLOR_DIMMER = 4
    BIPOLAR = 5
    INTERNALLY_CONTROLLED = 6


class OutputUsage(Enum):
    """Usage field for output"""
    UNDEFINED = 0
    ROOM = 1
    OUTDOORS = 2
    USER_DISPLAY = 3


class OutputMode(Enum):
    """Output mode"""
    DISABLED = 0
    BINARY = 1
    GRADUAL = 2
    DEFAULT = 127


class HeatingSystemCapability(Enum):
    """Heating system capability"""
    HEATING_ONLY = 1
    COOLING_ONLY = 2
    HEATING_AND_COOLING = 3


class HeatingSystemType(Enum):
    """Heating system type"""
    UNDEFINED = 0
    FLOOR_HEATING = 1
    RADIATOR = 2
    WALL_HEATING = 3
    CONVECTOR_PASSIVE = 4
    CONVECTOR_ACTIVE = 5
    FLOOR_HEATING_LOW_ENERGY = 6


class SceneEffect(Enum):
    """Scene effect types"""
    NO_EFFECT = 0
    SMOOTH_NORMAL = 1
    SLOW = 2
    VERY_SLOW = 3
    BLINK = 4


class ErrorCode(Enum):
    """Error codes for inputs/outputs"""
    OK = 0
    OPEN_CIRCUIT = 1
    SHORT_CIRCUIT = 2
    OVERLOAD = 3
    BUS_CONNECTION_PROBLEM = 4
    LOW_BATTERY = 5
    OTHER_DEVICE_ERROR = 6


# =============================================================================
# Button Input Classes
# =============================================================================

@dataclass
class ButtonInputDescription:
    """Description (invariable properties) of a button input"""
    name: str
    ds_index: int
    supports_local_key_mode: bool
    button_type: ButtonType
    button_element_id: ButtonElementID
    button_id: Optional[int] = None


@dataclass
class ButtonInputSettings:
    """Settings (persistently stored) of a button input"""
    group: int
    function: int  # 0..15
    mode: ButtonMode
    channel: int  # 0=default, 1..191=standard, 192..239=device specific
    sets_local_priority: bool = False
    calls_present: bool = False


@dataclass
class ButtonInputState:
    """State (changing during operation) of a button input"""
    value: Optional[bool] = None  # None=unknown, False=inactive, True=active
    click_type: ClickType = ClickType.IDLE
    age: Optional[float] = None
    error: ErrorCode = ErrorCode.OK
    # Alternative for direct scene calls
    action_id: Optional[int] = None
    action_mode: Optional[int] = None  # 0=normal, 1=force, 2=undo


@dataclass
class ButtonInput:
    """Complete button input with description, settings, and state"""
    description: ButtonInputDescription
    settings: ButtonInputSettings
    state: ButtonInputState = field(default_factory=ButtonInputState)

    def __post_init__(self):
        """Validate that all components have the correct types"""
        if not isinstance(self.description, ButtonInputDescription):
            raise TypeError("description must be ButtonInputDescription")
        if not isinstance(self.settings, ButtonInputSettings):
            raise TypeError("settings must be ButtonInputSettings")
        if not isinstance(self.state, ButtonInputState):
            raise TypeError("state must be ButtonInputState")


# =============================================================================
# Binary Input Classes
# =============================================================================

@dataclass
class BinaryInputDescription:
    """Description (invariable properties) of a binary input"""
    name: str
    ds_index: int
    input_type: InputType
    input_usage: InputUsage
    sensor_function: BinarySensorFunction
    update_interval: float  # seconds


@dataclass
class BinaryInputSettings:
    """Settings (persistently stored) of a binary input"""
    group: int
    sensor_function: BinarySensorFunction


@dataclass
class BinaryInputState:
    """State (changing during operation) of a binary input"""
    value: Optional[bool] = None  # None=unknown, False=inactive, True=active
    extended_value: Optional[int] = None  # Replaces 'value' if present
    age: Optional[float] = None
    error: ErrorCode = ErrorCode.OK


@dataclass
class BinaryInput:
    """Complete binary input with description, settings, and state"""
    description: BinaryInputDescription
    settings: BinaryInputSettings
    state: BinaryInputState = field(default_factory=BinaryInputState)


# =============================================================================
# Sensor Input Classes
# =============================================================================

@dataclass
class SensorInputDescription:
    """Description (invariable properties) of a sensor input"""
    name: str
    ds_index: int
    sensor_type: SensorType
    sensor_usage: SensorUsage
    min: float
    max: float
    resolution: float
    update_interval: float  # seconds
    alive_sign_interval: float  # seconds


@dataclass
class SensorInputSettings:
    """Settings (persistently stored) of a sensor input"""
    group: int
    min_push_interval: float = 2.0  # seconds
    changes_only_interval: float = 0.0  # seconds


@dataclass
class SensorInputState:
    """State (changing during operation) of a sensor input"""
    value: Optional[float] = None
    age: Optional[float] = None
    context_id: Optional[int] = None
    context_msg: Optional[str] = None
    error: ErrorCode = ErrorCode.OK


@dataclass
class SensorInput:
    """Complete sensor input with description, settings, and state"""
    description: SensorInputDescription
    settings: SensorInputSettings
    state: SensorInputState = field(default_factory=SensorInputState)


# =============================================================================
# Action Classes
# =============================================================================

@dataclass
class ParameterDescription:
    """Parameter description for device actions"""
    type: str  # 'numeric', 'enumeration', 'string'
    min: Optional[float] = None
    max: Optional[float] = None
    resolution: Optional[float] = None
    siunit: Optional[str] = None
    options: Optional[Dict[str, Any]] = None
    default: Optional[Union[float, str, int]] = None


@dataclass
class DeviceActionDescription:
    """Description of a device action method"""
    name: str
    params: Optional[List[ParameterDescription]] = None
    description: Optional[str] = None


@dataclass
class StandardAction:
    """Standard action (static, immutable)"""
    name: str  # Must have prefix "std."
    action: str  # Name of template action
    params: Optional[Dict[str, Any]] = None


@dataclass
class CustomAction:
    """Custom action (user-defined)"""
    name: str  # Must have prefix "custom."
    action: str  # Reference to template action
    title: str  # Human readable name
    params: Optional[Dict[str, Any]] = None


@dataclass
class DynamicAction:
    """Dynamic action (created on device side)"""
    name: str  # Must have prefix "dynamic."
    title: str  # Human readable name


# =============================================================================
# State and Property Classes
# =============================================================================

@dataclass
class DeviceStateDescription:
    """Description of a device state"""
    name: str
    options: Dict[int, str]  # Option ID : Value pairs
    description: Optional[str] = None


@dataclass
class DeviceState:
    """Current value of a device state"""
    name: str
    value: str  # Option value


@dataclass
class DevicePropertyDescription:
    """Description of a device property"""
    name: str
    type: str  # 'numeric', 'enumeration', 'string'
    min: Optional[float] = None
    max: Optional[float] = None
    resolution: Optional[float] = None
    siunit: Optional[str] = None
    options: Optional[Dict[str, Any]] = None
    default: Optional[Union[float, str, int]] = None


@dataclass
class DeviceProperty:
    """Current value of a device property"""
    name: str
    value: Union[str, float, int, bool]


@dataclass
class DeviceEventDescription:
    """Description of a device event"""
    name: str
    description: Optional[str] = None


# =============================================================================
# Output and Channel Classes
# =============================================================================

@dataclass
class OutputDescription:
    """Description (invariable properties) of device output"""
    default_group: int
    name: str
    function: OutputFunction
    output_usage: OutputUsage
    variable_ramp: bool
    max_power: Optional[float] = None  # Watts
    active_cooling_mode: Optional[bool] = None


@dataclass
class OutputSettings:
    """Settings (persistently stored) of device output"""
    active_group: int
    groups: Dict[int, bool]  # Group number (1..63) : membership
    mode: OutputMode
    push_changes: bool
    on_threshold: Optional[float] = 50.0  # 0..100%
    min_brightness: Optional[float] = None  # 0..100%
    dim_time_up: Optional[int] = None
    dim_time_down: Optional[int] = None
    dim_time_up_alt1: Optional[int] = None
    dim_time_down_alt1: Optional[int] = None
    dim_time_up_alt2: Optional[int] = None
    dim_time_down_alt2: Optional[int] = None
    heating_system_capability: Optional[HeatingSystemCapability] = None
    heating_system_type: Optional[HeatingSystemType] = None


@dataclass
class OutputState:
    """State (changing during operation) of device output"""
    local_priority: bool = False
    error: ErrorCode = ErrorCode.OK


@dataclass
class Output:
    """Complete output with description, settings, and state"""
    description: OutputDescription
    settings: OutputSettings
    state: OutputState = field(default_factory=OutputState)


@dataclass
class ChannelDescription:
    """Description (invariable properties) of an output channel"""
    name: str
    channel_type: int  # Numerical Type ID
    ds_index: int  # 0 is default output channel
    min: float
    max: float
    resolution: float


@dataclass
class ChannelState:
    """Current state of an output channel"""
    value: float
    age: Optional[float] = None  # None when value set but not yet applied


@dataclass
class Channel:
    """Complete channel with description and state"""
    description: ChannelDescription
    state: ChannelState
    # No settings currently defined per spec


# =============================================================================
# Scene Classes
# =============================================================================

@dataclass
class SceneValue:
    """Value for a specific channel in a scene"""
    value: float
    dont_care: bool = False
    automatic: bool = False


@dataclass
class Scene:
    """Scene configuration for a device"""
    scene_number: int
    channels: Dict[int, SceneValue]  # Channel type ID : SceneValue
    effect: SceneEffect = SceneEffect.NO_EFFECT
    dont_care: bool = False  # Scene-global don't care flag
    ignore_local_priority: bool = False


# =============================================================================
# Control Values (vDC Spec Section 4.11)
# =============================================================================

@dataclass
class ControlValues:
    """
    Control Values for a device (vDC Spec Section 4.11).
    
    Control values are write-only values that can be set using setControlValue.
    They cannot be read like regular properties.
    """
    heating_level: Optional[float] = None  # -100..100: 0=no heating/cooling, 100=max heating, -100=max cooling


# =============================================================================
# Common Properties for All Addressable Entities (vDC Spec Section 2)
# =============================================================================

@dataclass
class CommonEntityProperties:
    """
    Common properties for all addressable entities (vDC Spec Section 2).
    
    These properties must be supported by all addressable entities:
    vdSD (virtual device), vDC, vDChost, vdSM
    
    All properties are defined in vDC-API-properties Chapter 2.
    """
    # Required properties
    ds_uid: str  # dSUID - 34 hex characters (2*17)
    display_id: str  # Human-readable identification printed on physical device
    type: str  # Entity type: "vdSD", "vDC", "vDChost", "vdSM"
    model: str  # Human-readable model string
    model_version: str  # Model version (firmware version)
    model_uid: str  # digitalSTROM system unique ID for functional model
    
    # Optional properties
    hardware_version: Optional[str] = None  # Hardware version string
    hardware_guid: Optional[str] = None  # Hardware GUID in URN format (gs1:, macaddress:, uuid:, etc.)
    hardware_model_guid: Optional[str] = None  # Hardware model GUID in URN format
    vendor_name: Optional[str] = None  # Human-readable vendor/manufacturer name
    vendor_guid: Optional[str] = None  # Vendor GUID in URN format
    oem_guid: Optional[str] = None  # OEM product GUID
    oem_model_guid: Optional[str] = None  # OEM product model GUID (often GTIN)
    config_url: Optional[str] = None  # URL to device web configuration
    device_icon_16: Optional[bytes] = None  # 16x16 pixel PNG image
    device_icon_name: Optional[str] = None  # Filename-safe icon name for caching
    name: Optional[str] = None  # User-specified name (also stored upstream)
    device_class: Optional[str] = None  # digitalSTROM device class profile name
    device_class_version: Optional[str] = None  # Device class profile revision
    active: Optional[bool] = None  # Operation state (true = can operate normally)


# =============================================================================
# vDC (Virtual Device Connector) Properties (vDC Spec Section 3)
# =============================================================================

@dataclass
class VDCCapabilities:
    """
    Capabilities of a vDC (vDC Spec Section 3.2).
    
    Each capability indicates what features the vDC supports.
    """
    metering: Optional[bool] = None  # vDC provides metering data
    identification: Optional[bool] = None  # vDC provides identification (e.g., LED blink)
    dynamic_definitions: Optional[bool] = None  # vDC supports dynamic device definitions


@dataclass
class VDCProperties:
    """
    Properties for Virtual Device Connector (vDC Spec Section 3).
    
    These are properties specific to vDC entities (type="vDC").
    vDCs must also support CommonEntityProperties.
    """
    # Common properties (all vDCs must have these)
    common: CommonEntityProperties
    
    # vDC-specific properties
    capabilities: VDCCapabilities = field(default_factory=VDCCapabilities)
    zone_id: Optional[int] = None  # Default zone for this vDC
    implementation_id: Optional[str] = None  # Unique vDC implementation ID


# =============================================================================
# Device Properties Container
# =============================================================================

@dataclass
class DeviceProperties:
    """General device properties (Section 4.1.1)
    
    Note: The 'configurations' property is a list of property elements (property tree)
    as defined in vDC spec sections 4.1.2, 4.1.3, and 4.1.4. Each configuration contains
    nested structures for inputs, outputs/channels, and scenes.
    
    For implementation details, see custom_components/../models/property_tree.py
    """
    primary_group: int  # dS class number
    zone_id: int  # Global dS Zone ID
    model_features: Dict[str, bool]  # Feature name : enabled
    configurations: Dict[str, Any]  # Property tree: config_id -> property elements (sections 4.1.2-4.1.4)
    prog_mode: Optional[bool] = None
    current_config_id: Optional[str] = None


# =============================================================================
# Complete Virtual Device Class
# =============================================================================

@dataclass
class VirtualDevice:
    """
    Complete Virtual digitalSTROM Device (vdSD)
    
    This class represents a complete virtual device with all its properties,
    inputs, outputs, and configuration.
    """
    # Common entity properties (vDC Spec Section 2)
    common: CommonEntityProperties
    
    # General device properties (vDC Spec Section 4.1.1)
    properties: DeviceProperties
    
    # Input properties
    button_inputs: List[ButtonInput] = field(default_factory=list)
    binary_inputs: List[BinaryInput] = field(default_factory=list)
    sensor_inputs: List[SensorInput] = field(default_factory=list)
    
    # Action properties
    device_action_descriptions: List[DeviceActionDescription] = field(default_factory=list)
    standard_actions: List[StandardAction] = field(default_factory=list)
    custom_actions: List[CustomAction] = field(default_factory=list)
    dynamic_actions: List[DynamicAction] = field(default_factory=list)
    
    # State and property objects
    device_state_descriptions: List[DeviceStateDescription] = field(default_factory=list)
    device_states: List[DeviceState] = field(default_factory=list)
    device_property_descriptions: List[DevicePropertyDescription] = field(default_factory=list)
    device_properties: List[DeviceProperty] = field(default_factory=list)
    
    # Event descriptions
    device_event_descriptions: List[DeviceEventDescription] = field(default_factory=list)
    
    # Output properties
    output: Optional[Output] = None
    channels: List[Channel] = field(default_factory=list)
    
    # Scenes
    scenes: List[Scene] = field(default_factory=list)
    
    def add_button_input(self, button: ButtonInput) -> None:
        """Add a button input to the device"""
        self.button_inputs.append(button)
    
    def add_binary_input(self, binary_input: BinaryInput) -> None:
        """Add a binary input to the device"""
        self.binary_inputs.append(binary_input)
    
    def add_sensor_input(self, sensor: SensorInput) -> None:
        """Add a sensor input to the device"""
        self.sensor_inputs.append(sensor)
    
    def add_channel(self, channel: Channel) -> None:
        """Add an output channel to the device"""
        self.channels.append(channel)
    
    def add_scene(self, scene: Scene) -> None:
        """Add a scene to the device"""
        self.scenes.append(scene)
    
    def get_button_input(self, index: int) -> Optional[ButtonInput]:
        """Get button input by index"""
        if 0 <= index < len(self.button_inputs):
            return self.button_inputs[index]
        return None
    
    def get_sensor_input(self, index: int) -> Optional[SensorInput]:
        """Get sensor input by index"""
        if 0 <= index < len(self.sensor_inputs):
            return self.sensor_inputs[index]
        return None
    
    def get_channel(self, index: int) -> Optional[Channel]:
        """Get channel by index"""
        if 0 <= index < len(self.channels):
            return self.channels[index]
        return None
    
    def get_scene(self, scene_number: int) -> Optional[Scene]:
        """Get scene by scene number"""
        for scene in self.scenes:
            if scene.scene_number == scene_number:
                return scene
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert device to dictionary representation (for JSON serialization)"""
        result = {
            # Common entity properties
            "dSUID": self.common.ds_uid,
            "displayId": self.common.display_id,
            "type": self.common.type,
            "model": self.common.model,
            "modelVersion": self.common.model_version,
            "modelUID": self.common.model_uid,
            # Device properties
            "primaryGroup": self.properties.primary_group,
            "zoneID": self.properties.zone_id,
            "modelFeatures": self.properties.model_features,
            "configurations": self.properties.configurations,
        }
        
        # Add optional common properties
        if self.common.hardware_version is not None:
            result["hardwareVersion"] = self.common.hardware_version
        if self.common.hardware_guid is not None:
            result["hardwareGuid"] = self.common.hardware_guid
        if self.common.hardware_model_guid is not None:
            result["hardwareModelGuid"] = self.common.hardware_model_guid
        if self.common.vendor_name is not None:
            result["vendorName"] = self.common.vendor_name
        if self.common.vendor_guid is not None:
            result["vendorGuid"] = self.common.vendor_guid
        if self.common.oem_guid is not None:
            result["oemGuid"] = self.common.oem_guid
        if self.common.oem_model_guid is not None:
            result["oemModelGuid"] = self.common.oem_model_guid
        if self.common.config_url is not None:
            result["configURL"] = self.common.config_url
        if self.common.device_icon_name is not None:
            result["deviceIconName"] = self.common.device_icon_name
        if self.common.name is not None:
            result["name"] = self.common.name
        if self.common.device_class is not None:
            result["deviceClass"] = self.common.device_class
        if self.common.device_class_version is not None:
            result["deviceClassVersion"] = self.common.device_class_version
        if self.common.active is not None:
            result["active"] = self.common.active
        
        if self.properties.prog_mode is not None:
            result["progMode"] = self.properties.prog_mode
        
        if self.properties.current_config_id is not None:
            result["currentConfigId"] = self.properties.current_config_id
        
        # Add button inputs
        if self.button_inputs:
            result["buttonInputDescriptions"] = [
                {
                    "name": btn.description.name,
                    "dsIndex": btn.description.ds_index,
                    "supportsLocalKeyMode": btn.description.supports_local_key_mode,
                    "buttonType": btn.description.button_type.value,
                    "buttonElementID": btn.description.button_element_id.value,
                    "buttonID": btn.description.button_id,
                }
                for btn in self.button_inputs
            ]
            result["buttonInputSettings"] = [
                {
                    "group": btn.settings.group,
                    "function": btn.settings.function,
                    "mode": btn.settings.mode.value,
                    "channel": btn.settings.channel,
                    "setsLocalPriority": btn.settings.sets_local_priority,
                    "callsPresent": btn.settings.calls_present,
                }
                for btn in self.button_inputs
            ]
            result["buttonInputStates"] = [
                {
                    "value": btn.state.value,
                    "clickType": btn.state.click_type.value,
                    "age": btn.state.age,
                    "error": btn.state.error.value,
                }
                for btn in self.button_inputs
            ]
        
        # Add sensor inputs
        if self.sensor_inputs:
            result["sensorDescriptions"] = [
                {
                    "name": sensor.description.name,
                    "dsIndex": sensor.description.ds_index,
                    "sensorType": sensor.description.sensor_type.value,
                    "sensorUsage": sensor.description.sensor_usage.value,
                    "min": sensor.description.min,
                    "max": sensor.description.max,
                    "resolution": sensor.description.resolution,
                    "updateInterval": sensor.description.update_interval,
                    "aliveSignInterval": sensor.description.alive_sign_interval,
                }
                for sensor in self.sensor_inputs
            ]
            result["sensorStates"] = [
                {
                    "value": sensor.state.value,
                    "age": sensor.state.age,
                    "error": sensor.state.error.value,
                }
                for sensor in self.sensor_inputs
            ]
        
        # Add output if present
        if self.output:
            result["outputDescription"] = {
                "defaultGroup": self.output.description.default_group,
                "name": self.output.description.name,
                "function": self.output.description.function.value,
                "outputUsage": self.output.description.output_usage.value,
                "variableRamp": self.output.description.variable_ramp,
            }
            if self.output.description.max_power is not None:
                result["outputDescription"]["maxPower"] = self.output.description.max_power
        
        # Add channels
        if self.channels:
            result["channelDescriptions"] = [
                {
                    "name": ch.description.name,
                    "channelType": ch.description.channel_type,
                    "dsIndex": ch.description.ds_index,
                    "min": ch.description.min,
                    "max": ch.description.max,
                    "resolution": ch.description.resolution,
                }
                for ch in self.channels
            ]
            result["channelStates"] = [
                {
                    "value": ch.state.value,
                    "age": ch.state.age,
                }
                for ch in self.channels
            ]
        
        # Add scenes
        if self.scenes:
            result["scenes"] = {
                str(scene.scene_number): {
                    "channels": {
                        str(ch_id): {
                            "value": sv.value,
                            "dontCare": sv.dont_care,
                            "automatic": sv.automatic,
                        }
                        for ch_id, sv in scene.channels.items()
                    },
                    "effect": scene.effect.value,
                    "dontCare": scene.dont_care,
                    "ignoreLocalPriority": scene.ignore_local_priority,
                }
                for scene in self.scenes
            }
        
        return result


# =============================================================================
# Example Usage and Helper Functions
# =============================================================================

def create_temperature_sensor(
    name: str = "Temperature Sensor",
    ds_index: int = 0,
    group: int = 1,
    min_temp: float = -40.0,
    max_temp: float = 80.0,
    resolution: float = 0.1,
) -> SensorInput:
    """
    Helper function to create a temperature sensor input
    
    Args:
        name: Human readable name
        ds_index: Sensor index (0..N-1)
        group: dS group number
        min_temp: Minimum temperature in °C
        max_temp: Maximum temperature in °C
        resolution: Temperature resolution in °C
    
    Returns:
        Configured SensorInput object
    """
    description = SensorInputDescription(
        name=name,
        ds_index=ds_index,
        sensor_type=SensorType.TEMPERATURE,
        sensor_usage=SensorUsage.ROOM,
        min=min_temp,
        max=max_temp,
        resolution=resolution,
        update_interval=60.0,  # Update every minute
        alive_sign_interval=300.0,  # Alive sign every 5 minutes
    )
    
    settings = SensorInputSettings(
        group=group,
        min_push_interval=2.0,
        changes_only_interval=0.0,
    )
    
    state = SensorInputState()
    
    return SensorInput(description=description, settings=settings, state=state)


def create_pushbutton(
    name: str = "Pushbutton",
    ds_index: int = 0,
    group: int = 1,
    button_type: ButtonType = ButtonType.SINGLE_PUSHBUTTON,
) -> ButtonInput:
    """
    Helper function to create a simple pushbutton input
    
    Args:
        name: Human readable name
        ds_index: Button index (0..N-1)
        group: dS group number
        button_type: Type of physical button
    
    Returns:
        Configured ButtonInput object
    """
    description = ButtonInputDescription(
        name=name,
        ds_index=ds_index,
        supports_local_key_mode=True,
        button_type=button_type,
        button_element_id=ButtonElementID.CENTER,
    )
    
    settings = ButtonInputSettings(
        group=group,
        function=0,  # Device
        mode=ButtonMode.STANDARD,
        channel=0,  # Default channel
        sets_local_priority=False,
        calls_present=False,
    )
    
    state = ButtonInputState()
    
    return ButtonInput(description=description, settings=settings, state=state)


def create_dimmer_output(
    name: str = "Dimmer",
    default_group: int = 1,
    active_group: int = 1,
    max_power: Optional[float] = None,
) -> Output:
    """
    Helper function to create a dimmer output
    
    Args:
        name: Human readable name
        default_group: Default dS application ID
        active_group: Active dS application ID
        max_power: Maximum power in Watts
    
    Returns:
        Configured Output object
    """
    description = OutputDescription(
        default_group=default_group,
        name=name,
        function=OutputFunction.DIMMER,
        output_usage=OutputUsage.ROOM,
        variable_ramp=True,
        max_power=max_power,
    )
    
    settings = OutputSettings(
        active_group=active_group,
        groups={active_group: True},
        mode=OutputMode.GRADUAL,
        push_changes=True,
        on_threshold=50.0,
        min_brightness=1.0,
    )
    
    state = OutputState()
    
    return Output(description=description, settings=settings, state=state)


def create_brightness_channel(
    ds_index: int = 0,
    initial_value: float = 0.0,
) -> Channel:
    """
    Helper function to create a brightness channel
    
    Args:
        ds_index: Channel index (0 is default)
        initial_value: Initial brightness value (0..100)
    
    Returns:
        Configured Channel object
    """
    description = ChannelDescription(
        name="Brightness",
        channel_type=1,  # Brightness channel type
        ds_index=ds_index,
        min=0.0,
        max=100.0,
        resolution=0.1,
    )
    
    state = ChannelState(value=initial_value)
    
    return Channel(description=description, state=state)


# =============================================================================
# Example: Creating a complete virtual device
# =============================================================================

if __name__ == "__main__":
    # Example: Create a simple dimmable light with a pushbutton and temperature sensor
    
    # Import dSUID generator (available in same directory)
    try:
        from dsuid_generator import generate_dsuid
        # Generate dSUID from unique name (e.g., HA entity ID)
        dsuid = generate_dsuid(unique_name="light.living_room_main")
        print(f"Generated dSUID: {dsuid}")
    except ImportError:
        # Fallback if dsuid_generator not available
        dsuid = "0123456789ABCDEF0123456789ABCDEF01"
        print("Using fallback dSUID (dsuid_generator not imported)")
    
    # Create common entity properties with all new fields
    common_props = CommonEntityProperties(
        ds_uid=dsuid,
        display_id="LIGHT-001",
        type="vdSD",
        model="Virtual Dimmable Light",
        model_version="1.0.0",
        model_uid="vdSD-light-dimmer-temp-v1",
        hardware_version="1.0",
        hardware_guid="uuid:550e8400-e29b-41d4-a716-446655440000",
        hardware_model_guid="gs1:(01)4050300870342",
        vendor_name="Example Manufacturer",
        vendor_guid="vendorname:Example Corp",
        name="Living Room Main Light",
        device_class="light.dimmer",
        device_class_version="1.0",
        active=True,
    )
    
    # Create device properties
    device_props = DeviceProperties(
        primary_group=1,  # Light
        zone_id=0,
        model_features={"dimmable": True, "has_button": True, "has_sensor": True},
        configurations={
            "default": {
                "id": "default",
                "description": "Default configuration",
                "inputs": {},  # Would contain button/binary/sensor input references
                "outputs": {},  # Would contain output and channel references
                "scenes": {},  # Would contain scene configurations
            }
        },
    )
    
    # Create the virtual device
    device = VirtualDevice(
        common=common_props,
        properties=device_props,
    )
    
    # Add a pushbutton
    button = create_pushbutton(name="Light Switch", ds_index=0, group=1)
    device.add_button_input(button)
    
    # Add a temperature sensor
    temp_sensor = create_temperature_sensor(name="Room Temperature", ds_index=0, group=1)
    device.add_sensor_input(temp_sensor)
    
    # Add dimmer output
    dimmer = create_dimmer_output(name="Main Light", default_group=1, max_power=60.0)
    device.output = dimmer
    
    # Add brightness channel
    brightness_channel = create_brightness_channel(ds_index=0, initial_value=0.0)
    device.add_channel(brightness_channel)
    
    # Add a scene (e.g., scene 5 - "Deep Off")
    scene_deep_off = Scene(
        scene_number=5,
        channels={
            1: SceneValue(value=0.0, dont_care=False, automatic=False)
        },
        effect=SceneEffect.SMOOTH_NORMAL,
        dont_care=False,
        ignore_local_priority=False,
    )
    device.add_scene(scene_deep_off)
    
    # Add another scene (e.g., scene 1 - "Preset 1")
    scene_preset1 = Scene(
        scene_number=1,
        channels={
            1: SceneValue(value=75.0, dont_care=False, automatic=False)
        },
        effect=SceneEffect.SMOOTH_NORMAL,
        dont_care=False,
        ignore_local_priority=False,
    )
    device.add_scene(scene_preset1)
    
    # Print device info
    print("\n" + "="*60)
    print("Virtual Device Created:")
    print(f"  dSUID: {device.common.ds_uid}")
    print(f"  Display ID: {device.common.display_id}")
    print(f"  Type: {device.common.type}")
    print(f"  Model: {device.common.model}")
    print(f"  Name: {device.common.name}")
    print(f"  Active: {device.common.active}")
    print(f"  Primary Group: {device.properties.primary_group}")
    print(f"  Zone ID: {device.properties.zone_id}")
    print(f"  Button Inputs: {len(device.button_inputs)}")
    print(f"  Sensor Inputs: {len(device.sensor_inputs)}")
    print(f"  Channels: {len(device.channels)}")
    print(f"  Scenes: {len(device.scenes)}")
    
    # Access button state
    if device.button_inputs:
        btn = device.get_button_input(0)
        print(f"\nButton '{btn.description.name}':")
        print(f"  Type: {btn.description.button_type.name}")
        print(f"  Mode: {btn.settings.mode.name}")
        print(f"  Current click: {btn.state.click_type.name}")
    
    # Access sensor
    if device.sensor_inputs:
        sensor = device.get_sensor_input(0)
        print(f"\nSensor '{sensor.description.name}':")
        print(f"  Type: {sensor.description.sensor_type.name}")
        print(f"  Range: {sensor.description.min}°C to {sensor.description.max}°C")
        print(f"  Current value: {sensor.state.value}")
    
    # Convert to dictionary (could be serialized to JSON)
    device_dict = device.to_dict()
    print(f"\nDevice can be serialized to JSON with {len(device_dict)} top-level properties")
