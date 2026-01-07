"""State listener manager for coordinating state tracking across virtual devices.

This module provides a centralized manager for all state listeners, enabling
UI-based mapping configuration and coordinated state persistence.
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

import yaml

from homeassistant.core import HomeAssistant

from .state_listener import (
    AttributeStateListener,
    BooleanStateListener,
    EnumStateListener,
    IntegerStateListener,
    NumericStateListener,
    StateListener,
    StatePropertyType,
    StateUpdate,
    StringStateListener,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class ListenerMapping:
    """Configuration for a state listener mapping."""
    
    device_id: str
    property_type: str  # StatePropertyType enum value
    entity_id: str
    listener_class: str  # Class name (e.g., "BooleanStateListener")
    index: Optional[int] = None
    attribute_name: Optional[str] = None
    enabled: bool = True
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        data = {
            "device_id": self.device_id,
            "property_type": self.property_type,
            "entity_id": self.entity_id,
            "listener_class": self.listener_class,
            "enabled": self.enabled,
        }
        if self.index is not None:
            data["index"] = self.index
        if self.attribute_name:
            data["attribute_name"] = self.attribute_name
        return data
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ListenerMapping:
        """Create from dictionary."""
        return cls(
            device_id=data["device_id"],
            property_type=data["property_type"],
            entity_id=data["entity_id"],
            listener_class=data["listener_class"],
            index=data.get("index"),
            attribute_name=data.get("attribute_name"),
            enabled=data.get("enabled", True),
        )


class StateListenerManager:
    """Manages all state listeners for virtual devices.
    
    This manager handles:
    - Creating and registering state listeners
    - Loading/saving listener mappings from YAML
    - Coordinating state updates across listeners
    - Providing callbacks for state persistence
    """
    
    # Map of listener class names to classes
    LISTENER_CLASSES = {
        "BooleanStateListener": BooleanStateListener,
        "NumericStateListener": NumericStateListener,
        "IntegerStateListener": IntegerStateListener,
        "StringStateListener": StringStateListener,
        "EnumStateListener": EnumStateListener,
        "AttributeStateListener": AttributeStateListener,
    }
    
    def __init__(
        self,
        hass: HomeAssistant,
        mapping_file: Optional[Path] = None,
    ):
        """Initialize the state listener manager.
        
        Args:
            hass: Home Assistant instance
            mapping_file: Optional path to YAML file for listener mappings
        """
        self.hass = hass
        self.mapping_file = mapping_file
        self._listeners: dict[str, StateListener] = {}  # key: f"{device_id}:{property_type}:{index}"
        self._mappings: dict[str, ListenerMapping] = {}
        self._state_update_callbacks: list[Callable[[StateUpdate], None]] = []
        
    def add_state_update_callback(
        self, callback: Callable[[StateUpdate], None]
    ) -> None:
        """Add a global callback for all state updates.
        
        This is useful for persistence layers that need to save all state changes.
        
        Args:
            callback: Callback function that receives StateUpdate objects
        """
        self._state_update_callbacks.append(callback)
        
    def remove_state_update_callback(
        self, callback: Callable[[StateUpdate], None]
    ) -> None:
        """Remove a global state update callback."""
        if callback in self._state_update_callbacks:
            self._state_update_callbacks.remove(callback)
    
    def _get_listener_key(
        self,
        device_id: str,
        property_type: StatePropertyType,
        index: Optional[int] = None,
    ) -> str:
        """Generate unique key for a listener."""
        idx_str = f":{index}" if index is not None else ""
        return f"{device_id}:{property_type.value}{idx_str}"
    
    async def async_add_listener(
        self,
        device_id: str,
        entity_id: str,
        property_type: StatePropertyType,
        listener_class: type[StateListener],
        index: Optional[int] = None,
        attribute_name: Optional[str] = None,
        auto_start: bool = True,
    ) -> StateListener:
        """Add a state listener.
        
        Args:
            device_id: Virtual device ID
            entity_id: Home Assistant entity ID to track
            property_type: Type of STATE property to track
            listener_class: Class of listener to create
            index: Optional index for array properties
            attribute_name: Optional attribute name (for AttributeStateListener, EnumStateListener)
            auto_start: Whether to start the listener immediately
            
        Returns:
            The created listener instance
        """
        key = self._get_listener_key(device_id, property_type, index)
        
        # Remove existing listener if any
        if key in self._listeners:
            await self.async_remove_listener(device_id, property_type, index)
        
        # Create listener
        if listener_class == AttributeStateListener and attribute_name:
            listener = listener_class(
                self.hass, device_id, entity_id, property_type, attribute_name, index
            )
        elif listener_class == EnumStateListener:
            listener = listener_class(
                self.hass, device_id, entity_id, property_type, index, attribute_name
            )
        else:
            listener = listener_class(
                self.hass, device_id, entity_id, property_type, index
            )
        
        # Add global state update callback
        listener.add_callback(self._handle_state_update)
        
        # Store listener
        self._listeners[key] = listener
        
        # Store mapping
        mapping = ListenerMapping(
            device_id=device_id,
            property_type=property_type.value,
            entity_id=entity_id,
            listener_class=listener_class.__name__,
            index=index,
            attribute_name=attribute_name,
        )
        self._mappings[key] = mapping
        
        # Start listener if requested
        if auto_start:
            await listener.async_start()
        
        _LOGGER.info(
            "Added state listener: %s -> %s (%s)",
            entity_id,
            property_type.value,
            listener_class.__name__,
        )
        
        return listener
    
    async def async_remove_listener(
        self,
        device_id: str,
        property_type: StatePropertyType,
        index: Optional[int] = None,
    ) -> None:
        """Remove a state listener.
        
        Args:
            device_id: Virtual device ID
            property_type: Type of STATE property
            index: Optional index for array properties
        """
        key = self._get_listener_key(device_id, property_type, index)
        
        if listener := self._listeners.pop(key, None):
            await listener.async_stop()
            self._mappings.pop(key, None)
            _LOGGER.info(
                "Removed state listener: %s",
                property_type.value,
            )
    
    async def async_remove_device_listeners(self, device_id: str) -> None:
        """Remove all listeners for a device.
        
        Args:
            device_id: Virtual device ID
        """
        keys_to_remove = [k for k in self._listeners.keys() if k.startswith(f"{device_id}:")]
        for key in keys_to_remove:
            listener = self._listeners.pop(key)
            await listener.async_stop()
            self._mappings.pop(key, None)
        
        _LOGGER.info("Removed %d listeners for device %s", len(keys_to_remove), device_id)
    
    def get_listener(
        self,
        device_id: str,
        property_type: StatePropertyType,
        index: Optional[int] = None,
    ) -> Optional[StateListener]:
        """Get a state listener.
        
        Args:
            device_id: Virtual device ID
            property_type: Type of STATE property
            index: Optional index
            
        Returns:
            The listener instance or None if not found
        """
        key = self._get_listener_key(device_id, property_type, index)
        return self._listeners.get(key)
    
    def get_device_listeners(self, device_id: str) -> list[StateListener]:
        """Get all listeners for a device.
        
        Args:
            device_id: Virtual device ID
            
        Returns:
            List of listeners for the device
        """
        return [
            listener
            for key, listener in self._listeners.items()
            if key.startswith(f"{device_id}:")
        ]
    
    def _handle_state_update(self, update: StateUpdate) -> None:
        """Handle state update from a listener."""
        _LOGGER.debug("State update: %s", update)
        
        # Notify all global callbacks
        for callback in self._state_update_callbacks:
            try:
                callback(update)
            except Exception as err:
                _LOGGER.error(
                    "Error in state update callback: %s",
                    err,
                    exc_info=True,
                )
    
    async def async_load_mappings(self) -> None:
        """Load listener mappings from YAML file."""
        if not self.mapping_file or not self.mapping_file.exists():
            _LOGGER.debug("No mapping file found, starting with empty mappings")
            return
        
        try:
            # Load YAML file in executor to avoid blocking I/O
            def _load_yaml():
                with open(self.mapping_file, "r") as f:
                    return yaml.safe_load(f) or {}
            
            data = await self.hass.async_add_executor_job(_load_yaml)
            
            mappings = data.get("listener_mappings", [])
            _LOGGER.info("Loading %d listener mappings from %s", len(mappings), self.mapping_file)
            
            for mapping_data in mappings:
                mapping = ListenerMapping.from_dict(mapping_data)
                
                if not mapping.enabled:
                    _LOGGER.debug("Skipping disabled mapping for %s", mapping.entity_id)
                    continue
                
                # Get listener class
                listener_class = self.LISTENER_CLASSES.get(mapping.listener_class)
                if not listener_class:
                    _LOGGER.warning(
                        "Unknown listener class: %s, skipping",
                        mapping.listener_class,
                    )
                    continue
                
                # Get property type
                try:
                    property_type = StatePropertyType(mapping.property_type)
                except ValueError:
                    _LOGGER.warning(
                        "Unknown property type: %s, skipping",
                        mapping.property_type,
                    )
                    continue
                
                # Create and start listener
                await self.async_add_listener(
                    device_id=mapping.device_id,
                    entity_id=mapping.entity_id,
                    property_type=property_type,
                    listener_class=listener_class,
                    index=mapping.index,
                    attribute_name=mapping.attribute_name,
                    auto_start=True,
                )
            
            _LOGGER.info("Loaded %d active listener mappings", len(self._listeners))
            
        except Exception as err:
            _LOGGER.error("Error loading listener mappings: %s", err, exc_info=True)
    
    async def async_save_mappings(self) -> None:
        """Save listener mappings to YAML file."""
        if not self.mapping_file:
            _LOGGER.warning("No mapping file configured, cannot save")
            return
        
        try:
            # Convert mappings to list
            mappings_list = [
                mapping.to_dict()
                for mapping in self._mappings.values()
            ]
            
            data = {
                "listener_mappings": mappings_list,
            }
            
            # Save YAML file in executor to avoid blocking I/O
            def _save_yaml():
                # Ensure directory exists
                self.mapping_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(self.mapping_file, "w") as f:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            await self.hass.async_add_executor_job(_save_yaml)
            
            _LOGGER.info(
                "Saved %d listener mappings to %s",
                len(mappings_list),
                self.mapping_file,
            )
            
        except Exception as err:
            _LOGGER.error("Error saving listener mappings: %s", err, exc_info=True)
    
    async def async_start_all(self) -> None:
        """Start all listeners."""
        for listener in self._listeners.values():
            await listener.async_start()
        _LOGGER.info("Started %d state listeners", len(self._listeners))
    
    async def async_stop_all(self) -> None:
        """Stop all listeners."""
        for listener in self._listeners.values():
            await listener.async_stop()
        _LOGGER.info("Stopped %d state listeners", len(self._listeners))
    
    def get_statistics(self) -> dict[str, Any]:
        """Get statistics about active listeners.
        
        Returns:
            Dictionary with listener statistics
        """
        stats = {
            "total_listeners": len(self._listeners),
            "total_mappings": len(self._mappings),
            "listeners_by_type": {},
            "listeners_by_device": {},
        }
        
        for key, listener in self._listeners.items():
            # Count by type
            prop_type = listener.property_type.value
            stats["listeners_by_type"][prop_type] = (
                stats["listeners_by_type"].get(prop_type, 0) + 1
            )
            
            # Count by device
            device_id = listener.device_id
            stats["listeners_by_device"][device_id] = (
                stats["listeners_by_device"].get(device_id, 0) + 1
            )
        
        return stats
