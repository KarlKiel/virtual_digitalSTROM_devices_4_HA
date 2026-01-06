"""State listener system for tracking Home Assistant entity changes.

This module provides listener objects that can be mapped to existing Home Assistant
entities to track changes for all STATE-classified properties as defined in the
vDC specification.

Based on COMPLETE_PROPERTY_CLASSIFICATION.md - STATE properties (45 total):
- Button input states (value, error, actionId, actionMode)
- Binary input states (value, extendedValue, error)
- Sensor input states (value, contextId, contextMsg, error)
- Dynamic actions (name, title)
- Device states (name, value)
- Device properties (name, value)
- Output states (localPriority, error)
- Channel states (value)
- Control values (heatingLevel, coolingLevel, ventilationLevel, etc.)
- System states (connection_status, system_status, progMode)
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

from homeassistant.core import HomeAssistant, State, callback
from homeassistant.helpers.event import async_track_state_change_event

_LOGGER = logging.getLogger(__name__)


class StatePropertyType(Enum):
    """Types of STATE properties that can be tracked."""
    
    # Button Input States (Section 4.2.3)
    BUTTON_VALUE = "button.value"
    BUTTON_ERROR = "button.error"
    BUTTON_ACTION_ID = "button.actionId"
    BUTTON_ACTION_MODE = "button.actionMode"
    
    # Binary Input States (Section 4.3.3)
    BINARY_VALUE = "binary.value"
    BINARY_EXTENDED_VALUE = "binary.extendedValue"
    BINARY_ERROR = "binary.error"
    
    # Sensor Input States (Section 4.4.3)
    SENSOR_VALUE = "sensor.value"
    SENSOR_CONTEXT_ID = "sensor.contextId"
    SENSOR_CONTEXT_MSG = "sensor.contextMsg"
    SENSOR_ERROR = "sensor.error"
    
    # Dynamic Actions (Section 4.6.1)
    DYNAMIC_ACTION_NAME = "dynamicAction.name"
    DYNAMIC_ACTION_TITLE = "dynamicAction.title"
    
    # Device States (Section 4.7.1)
    DEVICE_STATE_NAME = "deviceState.name"
    DEVICE_STATE_VALUE = "deviceState.value"
    
    # Device Properties (Section 4.7.2)
    DEVICE_PROPERTY_NAME = "deviceProperty.name"
    DEVICE_PROPERTY_VALUE = "deviceProperty.value"
    
    # Output States (Section 4.8.3)
    OUTPUT_LOCAL_PRIORITY = "output.localPriority"
    OUTPUT_ERROR = "output.error"
    
    # Channel States (Section 4.9.3)
    CHANNEL_VALUE = "channel.value"
    
    # Control Values (Section 4.11)
    CONTROL_HEATING_LEVEL = "control.heatingLevel"
    CONTROL_COOLING_LEVEL = "control.coolingLevel"
    CONTROL_VENTILATION_LEVEL = "control.ventilationLevel"
    
    # System States (Additional/General)
    PROG_MODE = "device.progMode"
    CONNECTION_STATUS = "device.connection_status"
    SYSTEM_STATUS = "device.system_status"


@dataclass
class StateUpdate:
    """Represents a state update event."""
    
    property_type: StatePropertyType
    device_id: str
    entity_id: str
    old_value: Any
    new_value: Any
    timestamp: datetime = field(default_factory=datetime.now)
    index: Optional[int] = None  # For indexed properties (e.g., button[0], sensor[1])
    
    def __str__(self) -> str:
        """Return string representation."""
        idx_str = f"[{self.index}]" if self.index is not None else ""
        return (
            f"StateUpdate({self.property_type.value}{idx_str}: "
            f"{self.old_value} -> {self.new_value} @ {self.timestamp})"
        )


class StateListener(ABC):
    """Base class for state listeners.
    
    Each listener tracks changes to a specific STATE property by monitoring
    a Home Assistant entity. When the entity state changes, the listener
    extracts the relevant value and notifies callbacks.
    """
    
    def __init__(
        self,
        hass: HomeAssistant,
        device_id: str,
        entity_id: str,
        property_type: StatePropertyType,
        index: Optional[int] = None,
    ):
        """Initialize the state listener.
        
        Args:
            hass: Home Assistant instance
            device_id: Virtual device ID this listener belongs to
            entity_id: Home Assistant entity ID to track
            property_type: Type of STATE property being tracked
            index: Optional index for array properties (e.g., button[0])
        """
        self.hass = hass
        self.device_id = device_id
        self.entity_id = entity_id
        self.property_type = property_type
        self.index = index
        self._callbacks: list[Callable[[StateUpdate], None]] = []
        self._unsubscribe: Optional[Callable] = None
        self._last_value: Any = None
        
    def add_callback(self, callback: Callable[[StateUpdate], None]) -> None:
        """Add a callback to be notified of state changes."""
        self._callbacks.append(callback)
        
    def remove_callback(self, callback: Callable[[StateUpdate], None]) -> None:
        """Remove a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
            
    @abstractmethod
    def extract_value(self, state: State) -> Any:
        """Extract the relevant value from the HA state.
        
        Args:
            state: Home Assistant state object
            
        Returns:
            The extracted value for this property type
        """
        pass
    
    async def async_start(self) -> None:
        """Start listening to state changes."""
        _LOGGER.debug(
            "Starting state listener for %s -> %s (device: %s)",
            self.entity_id,
            self.property_type.value,
            self.device_id,
        )
        
        # Get initial state
        if state := self.hass.states.get(self.entity_id):
            self._last_value = self.extract_value(state)
            _LOGGER.debug("Initial value for %s: %s", self.entity_id, self._last_value)
        
        # Subscribe to state changes
        self._unsubscribe = async_track_state_change_event(
            self.hass,
            self.entity_id,
            self._async_state_changed,
        )
        
    async def async_stop(self) -> None:
        """Stop listening to state changes."""
        if self._unsubscribe:
            self._unsubscribe()
            self._unsubscribe = None
            _LOGGER.debug(
                "Stopped state listener for %s -> %s",
                self.entity_id,
                self.property_type.value,
            )
    
    @callback
    def _async_state_changed(self, event) -> None:
        """Handle state change event."""
        new_state = event.data.get("new_state")
        old_state = event.data.get("old_state")
        
        if new_state is None:
            return
            
        old_value = self.extract_value(old_state) if old_state else None
        new_value = self.extract_value(new_state)
        
        # Only notify if value actually changed
        if old_value != new_value:
            self._last_value = new_value
            update = StateUpdate(
                property_type=self.property_type,
                device_id=self.device_id,
                entity_id=self.entity_id,
                old_value=old_value,
                new_value=new_value,
                index=self.index,
            )
            
            _LOGGER.debug("State change detected: %s", update)
            
            # Notify all callbacks
            for callback in self._callbacks:
                try:
                    callback(update)
                except Exception as err:
                    _LOGGER.error(
                        "Error in state listener callback: %s",
                        err,
                        exc_info=True,
                    )
    
    def get_current_value(self) -> Any:
        """Get the last known value."""
        return self._last_value


class BooleanStateListener(StateListener):
    """Listener for boolean state values (button.value, binary.value, output.localPriority)."""
    
    def extract_value(self, state: State) -> Optional[bool]:
        """Extract boolean value from state."""
        if state is None:
            return None
        # Handle both direct boolean state and attributes
        if state.state in ("on", "True", "true", "1"):
            return True
        elif state.state in ("off", "False", "false", "0"):
            return False
        return None


class NumericStateListener(StateListener):
    """Listener for numeric state values (sensor.value, channel.value, control values)."""
    
    def extract_value(self, state: State) -> Optional[float]:
        """Extract numeric value from state."""
        if state is None:
            return None
        try:
            return float(state.state)
        except (ValueError, TypeError):
            return None


class IntegerStateListener(StateListener):
    """Listener for integer state values (button.actionId, sensor.contextId, binary.extendedValue)."""
    
    def extract_value(self, state: State) -> Optional[int]:
        """Extract integer value from state."""
        if state is None:
            return None
        try:
            return int(float(state.state))
        except (ValueError, TypeError):
            return None


class StringStateListener(StateListener):
    """Listener for string state values (sensor.contextMsg, device states/properties, connection_status)."""
    
    def extract_value(self, state: State) -> Optional[str]:
        """Extract string value from state."""
        if state is None:
            return None
        return str(state.state) if state.state not in (None, "unknown", "unavailable") else None


class EnumStateListener(StateListener):
    """Listener for enum state values (error codes, button.actionMode)."""
    
    def __init__(
        self,
        hass: HomeAssistant,
        device_id: str,
        entity_id: str,
        property_type: StatePropertyType,
        index: Optional[int] = None,
        attribute_name: Optional[str] = None,
    ):
        """Initialize enum listener.
        
        Args:
            hass: Home Assistant instance
            device_id: Virtual device ID
            entity_id: HA entity ID to track
            property_type: Property type
            index: Optional index
            attribute_name: Optional attribute name to extract from (e.g., "error_code")
        """
        super().__init__(hass, device_id, entity_id, property_type, index)
        self.attribute_name = attribute_name
        
    def extract_value(self, state: State) -> Optional[int]:
        """Extract enum value from state or attribute."""
        if state is None:
            return None
            
        # Try to get from attribute first if specified
        if self.attribute_name and hasattr(state, "attributes"):
            value = state.attributes.get(self.attribute_name)
            if value is not None:
                try:
                    return int(value)
                except (ValueError, TypeError):
                    pass
        
        # Otherwise try state value
        try:
            return int(float(state.state))
        except (ValueError, TypeError):
            return None


class AttributeStateListener(StateListener):
    """Listener for state values stored in entity attributes."""
    
    def __init__(
        self,
        hass: HomeAssistant,
        device_id: str,
        entity_id: str,
        property_type: StatePropertyType,
        attribute_name: str,
        index: Optional[int] = None,
    ):
        """Initialize attribute listener.
        
        Args:
            hass: Home Assistant instance
            device_id: Virtual device ID
            entity_id: HA entity ID to track
            property_type: Property type
            attribute_name: Attribute name to extract
            index: Optional index
        """
        super().__init__(hass, device_id, entity_id, property_type, index)
        self.attribute_name = attribute_name
        
    def extract_value(self, state: State) -> Any:
        """Extract value from entity attribute."""
        if state is None or not hasattr(state, "attributes"):
            return None
        return state.attributes.get(self.attribute_name)


# Convenience factory functions

def create_button_value_listener(
    hass: HomeAssistant,
    device_id: str,
    entity_id: str,
    button_index: int = 0,
) -> BooleanStateListener:
    """Create a listener for button value state."""
    return BooleanStateListener(
        hass, device_id, entity_id, StatePropertyType.BUTTON_VALUE, button_index
    )


def create_sensor_value_listener(
    hass: HomeAssistant,
    device_id: str,
    entity_id: str,
    sensor_index: int = 0,
) -> NumericStateListener:
    """Create a listener for sensor value state."""
    return NumericStateListener(
        hass, device_id, entity_id, StatePropertyType.SENSOR_VALUE, sensor_index
    )


def create_channel_value_listener(
    hass: HomeAssistant,
    device_id: str,
    entity_id: str,
    channel_index: int = 0,
) -> NumericStateListener:
    """Create a listener for channel value state (e.g., brightness)."""
    return NumericStateListener(
        hass, device_id, entity_id, StatePropertyType.CHANNEL_VALUE, channel_index
    )


def create_control_value_listener(
    hass: HomeAssistant,
    device_id: str,
    entity_id: str,
    control_type: str = "heating",  # "heating", "cooling", "ventilation"
) -> NumericStateListener:
    """Create a listener for control value state (heating/cooling/ventilation level)."""
    property_map = {
        "heating": StatePropertyType.CONTROL_HEATING_LEVEL,
        "cooling": StatePropertyType.CONTROL_COOLING_LEVEL,
        "ventilation": StatePropertyType.CONTROL_VENTILATION_LEVEL,
    }
    property_type = property_map.get(control_type, StatePropertyType.CONTROL_HEATING_LEVEL)
    return NumericStateListener(hass, device_id, entity_id, property_type)


def create_connection_status_listener(
    hass: HomeAssistant,
    device_id: str,
    entity_id: str,
) -> StringStateListener:
    """Create a listener for connection status."""
    return StringStateListener(
        hass, device_id, entity_id, StatePropertyType.CONNECTION_STATUS
    )
