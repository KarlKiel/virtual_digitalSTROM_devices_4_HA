"""Property update system for virtual digitalSTROM devices.

This module provides methods to update CONFIG and STATE properties with:
- CONFIG updates: Persisted to YAML storage
- STATE updates: 
  - OUTPUT/CONTROL properties: Push values to mapped HA entities + selective persistence
  - INPUT properties (sensors, binary inputs): Persist only, NOT pushed (read-only)

Based on COMPLETE_PROPERTY_CLASSIFICATION.md:
- 81 CONFIG properties (always persisted)
- 45 STATE properties (selectively persisted, OUTPUT properties pushed to HA entities)
- 22 META properties (auto-calculated, not directly updatable)
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.service import async_call_from_config

from .device_storage import DeviceStorage
from ..listeners.state_listener import StatePropertyType
from ..models.virtual_device import VirtualDevice

_LOGGER = logging.getLogger(__name__)


class PropertyUpdateError(Exception):
    """Base exception for property update errors."""
    pass


class ConfigPropertyUpdater:
    """Handles updates to CONFIG properties with automatic persistence."""
    
    def __init__(
        self,
        hass: HomeAssistant,
        device_storage: DeviceStorage,
    ):
        """Initialize the CONFIG property updater.
        
        Args:
            hass: Home Assistant instance
            device_storage: DeviceStorage instance for persistence
        """
        self.hass = hass
        self.device_storage = device_storage
    
    async def update_config_property(
        self,
        device_id: str,
        property_path: str,
        value: Any,
        index: Optional[int] = None,
    ) -> bool:
        """Update a CONFIG property and persist to YAML.
        
        CONFIG properties describe the device and are always persisted.
        Examples: name, zone_id, group_id, output settings, scene values
        
        Args:
            device_id: Device identifier
            property_path: Property path (e.g., "name", "zone_id", "buttonInputSettings[0].group")
            value: New value to set
            index: Optional index for array properties
            
        Returns:
            True if update successful, False otherwise
            
        Raises:
            PropertyUpdateError: If update fails
        """
        try:
            device = self.device_storage.get_device(device_id)
            if not device:
                raise PropertyUpdateError(f"Device {device_id} not found")
            
            # Parse property path and update
            self._update_device_property(device, property_path, value, index)
            
            # Persist to YAML (CONFIG properties are ALWAYS persisted)
            self.device_storage.save_device(device)
            
            _LOGGER.info(
                f"Updated CONFIG property {property_path} for device {device_id} to {value}"
            )
            return True
            
        except Exception as e:
            _LOGGER.error(f"Error updating CONFIG property {property_path}: {e}")
            raise PropertyUpdateError(f"Failed to update CONFIG property: {e}") from e
    
    async def update_multiple_config_properties(
        self,
        device_id: str,
        updates: dict[str, Any],
    ) -> bool:
        """Update multiple CONFIG properties in a single transaction.
        
        Args:
            device_id: Device identifier
            updates: Dictionary of property_path: value pairs
            
        Returns:
            True if all updates successful, False otherwise
        """
        try:
            device = self.device_storage.get_device(device_id)
            if not device:
                raise PropertyUpdateError(f"Device {device_id} not found")
            
            # Update all properties
            for property_path, value in updates.items():
                self._update_device_property(device, property_path, value)
            
            # Single persistence operation
            self.device_storage.save_device(device)
            
            _LOGGER.info(
                f"Updated {len(updates)} CONFIG properties for device {device_id}"
            )
            return True
            
        except Exception as e:
            _LOGGER.error(f"Error updating multiple CONFIG properties: {e}")
            raise PropertyUpdateError(f"Failed to update CONFIG properties: {e}") from e
    
    def _update_device_property(
        self,
        device: VirtualDevice,
        property_path: str,
        value: Any,
        index: Optional[int] = None,
    ) -> None:
        """Update a property on the device object.
        
        Handles simple properties and nested/indexed properties.
        
        Args:
            device: VirtualDevice instance
            property_path: Property path (e.g., "name", "attributes.num_channels")
            value: New value
            index: Optional index for array properties
        """
        # Handle simple top-level properties
        if "." not in property_path and "[" not in property_path:
            if hasattr(device, property_path):
                setattr(device, property_path, value)
            else:
                # Store in attributes dict
                device.attributes[property_path] = value
            return
        
        # Handle nested properties in attributes
        if property_path.startswith("attributes."):
            attr_path = property_path[11:]  # Remove "attributes." prefix
            device.attributes[attr_path] = value
            return
        
        # Handle indexed properties (e.g., "buttonInputSettings[0].group")
        if "[" in property_path and "]" in property_path:
            # Extract array name, index, and sub-property
            parts = property_path.split("[")
            array_name = parts[0]
            rest = parts[1].split("]")
            arr_index = int(rest[0]) if index is None else index
            sub_property = rest[1][1:] if len(rest) > 1 and rest[1] else None
            
            # Get or create array in attributes
            if array_name not in device.attributes:
                device.attributes[array_name] = []
            
            array = device.attributes[array_name]
            
            # Ensure array is large enough
            while len(array) <= arr_index:
                array.append({})
            
            # Update the value
            if sub_property:
                if not isinstance(array[arr_index], dict):
                    array[arr_index] = {}
                array[arr_index][sub_property] = value
            else:
                array[arr_index] = value
            
            return
        
        # Default: store in attributes
        device.attributes[property_path] = value


class StatePropertyUpdater:
    """Handles updates to STATE properties with selective HA entity pushing.
    
    STATE properties fall into two categories:
    1. OUTPUT/CONTROL properties: Pushed to HA entities + selectively persisted
       - channel.value, control.heatingLevel, etc.
    2. INPUT properties: Persisted only, NOT pushed to HA (read-only inputs)
       - sensor.value, binary.value (these come FROM HA entities via listeners)
    """
    
    def __init__(
        self,
        hass: HomeAssistant,
        device_storage: DeviceStorage,
    ):
        """Initialize the STATE property updater.
        
        Args:
            hass: Home Assistant instance
            device_storage: DeviceStorage instance for selective persistence
        """
        self.hass = hass
        self.device_storage = device_storage
        
        # Properties that MUST be persisted (critical for functionality)
        self.critical_persistent_properties = {
            StatePropertyType.CONTROL_HEATING_LEVEL,
            StatePropertyType.CONTROL_COOLING_LEVEL,
            StatePropertyType.CONTROL_VENTILATION_LEVEL,
        }
        
        # Properties that SHOULD be persisted (avoid waiting after restart)
        self.recommended_persistent_properties = {
            StatePropertyType.SENSOR_VALUE,
            StatePropertyType.CHANNEL_VALUE,
            StatePropertyType.BINARY_VALUE,
            StatePropertyType.CONNECTION_STATUS,
            StatePropertyType.SYSTEM_STATUS,
        }
        
        # Read-only input properties that should NOT be pushed to HA entities
        # These are INPUT values that come FROM sensors/binary inputs, not outputs
        self.read_only_input_properties = {
            StatePropertyType.SENSOR_VALUE,
            StatePropertyType.BINARY_VALUE,
            StatePropertyType.BINARY_EXTENDED_VALUE,
            StatePropertyType.SENSOR_CONTEXT_ID,
            StatePropertyType.SENSOR_CONTEXT_MSG,
            StatePropertyType.SENSOR_ERROR,
            StatePropertyType.BINARY_ERROR,
        }
    
    async def update_state_property(
        self,
        device_id: str,
        property_type: StatePropertyType,
        value: Any,
        index: Optional[int] = None,
        persist: Optional[bool] = None,
    ) -> bool:
        """Update a STATE property with selective HA entity pushing.
        
        STATE properties are runtime values. This method:
        1. For OUTPUT/CONTROL properties: Pushes value to mapped HA entity + selective persistence
        2. For INPUT properties (sensors, binary inputs): Persists only, does NOT push to HA
        
        INPUT properties (read-only, NOT pushed):
        - sensor.value, binary.value - These come FROM HA entities via listeners
        - sensor.contextId, sensor.contextMsg, sensor.error
        - binary.extendedValue, binary.error
        
        OUTPUT/CONTROL properties (pushed to HA):
        - channel.value, control.heatingLevel, control.coolingLevel, etc.
        
        Args:
            device_id: Device identifier
            property_type: Type of STATE property
            value: New value to set
            index: Optional index for multi-instance properties
            persist: Override auto-persistence decision (True/False/None for auto)
            
        Returns:
            True if update successful, False otherwise
            
        Raises:
            PropertyUpdateError: If update fails
        """
        try:
            device = self.device_storage.get_device(device_id)
            if not device:
                raise PropertyUpdateError(f"Device {device_id} not found")
            
            # Get entity mapping from device attributes
            entity_mapping = self._get_entity_mapping(device, property_type, index)
            
            # Check if this is a read-only input property
            is_read_only_input = property_type in self.read_only_input_properties
            
            if not entity_mapping:
                _LOGGER.warning(
                    f"No entity mapping for {property_type.value}[{index}] on device {device_id}"
                )
                # Still persist locally even if no mapping exists
            elif is_read_only_input:
                # Read-only input properties (sensors, binary inputs) should NOT be pushed to HA
                # These are INPUT values that come FROM HA entities via listeners
                _LOGGER.debug(
                    f"Skipping push for read-only input property {property_type.value} (value persisted only)"
                )
            else:
                # Push value to Home Assistant entity (for output/control properties)
                await self._push_to_ha_entity(entity_mapping, value, property_type)
            
            # Decide whether to persist
            should_persist = self._should_persist(property_type, persist)
            
            if should_persist:
                # Store in device attributes for persistence
                self._store_state_value(device, property_type, value, index)
                self.device_storage.save_device(device)
                _LOGGER.debug(f"Persisted STATE property {property_type.value} for device {device_id}")
            
            _LOGGER.info(
                f"Updated STATE property {property_type.value}[{index}] for device {device_id} to {value}"
            )
            return True
            
        except Exception as e:
            _LOGGER.error(f"Error updating STATE property {property_type.value}: {e}")
            raise PropertyUpdateError(f"Failed to update STATE property: {e}") from e
    
    async def update_multiple_state_properties(
        self,
        device_id: str,
        updates: dict[tuple[StatePropertyType, Optional[int]], Any],
        persist: Optional[bool] = None,
    ) -> bool:
        """Update multiple STATE properties in a batch.
        
        Args:
            device_id: Device identifier
            updates: Dictionary of (property_type, index): value pairs
            persist: Override auto-persistence decision for all updates
            
        Returns:
            True if all updates successful, False otherwise
        """
        try:
            device = self.device_storage.get_device(device_id)
            if not device:
                raise PropertyUpdateError(f"Device {device_id} not found")
            
            any_persisted = False
            
            # Process all updates
            for (property_type, index), value in updates.items():
                # Get entity mapping
                entity_mapping = self._get_entity_mapping(device, property_type, index)
                
                # Check if this is a read-only input property
                is_read_only_input = property_type in self.read_only_input_properties
                
                if entity_mapping and not is_read_only_input:
                    # Push to HA entity (skip for read-only inputs)
                    await self._push_to_ha_entity(entity_mapping, value, property_type)
                
                # Check persistence
                should_persist = self._should_persist(property_type, persist)
                
                if should_persist:
                    self._store_state_value(device, property_type, value, index)
                    any_persisted = True
            
            # Single persistence operation if any updates need it
            if any_persisted:
                self.device_storage.save_device(device)
            
            _LOGGER.info(
                f"Updated {len(updates)} STATE properties for device {device_id}"
            )
            return True
            
        except Exception as e:
            _LOGGER.error(f"Error updating multiple STATE properties: {e}")
            raise PropertyUpdateError(f"Failed to update STATE properties: {e}") from e
    
    def _get_entity_mapping(
        self,
        device: VirtualDevice,
        property_type: StatePropertyType,
        index: Optional[int],
    ) -> Optional[str]:
        """Get the HA entity ID mapped to this property.
        
        Args:
            device: VirtualDevice instance
            property_type: Type of STATE property
            index: Optional index for multi-instance properties
            
        Returns:
            Entity ID string or None if no mapping exists
        """
        entity_mappings = device.attributes.get("entity_mappings", {})
        
        # Build the property key (e.g., "sensor[0].value", "channel[2].value")
        if index is not None:
            # Extract base property name (e.g., "sensor.value" -> "sensor", "value")
            parts = property_type.value.split(".")
            if len(parts) == 2:
                base, prop = parts
                property_key = f"{base}[{index}].{prop}"
            else:
                property_key = f"{property_type.value}[{index}]"
        else:
            property_key = property_type.value
        
        # Check for direct mapping or attribute-based mapping
        entity_id = entity_mappings.get(property_key)
        
        # If attribute mapping, it might be "entity@attribute"
        if entity_id and "@" in entity_id:
            return entity_id.split("@")[0]  # Return base entity
        
        return entity_id
    
    async def _push_to_ha_entity(
        self,
        entity_id: str,
        value: Any,
        property_type: StatePropertyType,
    ) -> None:
        """Push a value to a Home Assistant entity.
        
        Args:
            entity_id: Target entity ID
            value: Value to set
            property_type: Type of property (determines how to set value)
        """
        # Extract attribute if entity_id contains "@"
        attribute_name = None
        if "@" in entity_id:
            entity_id, attribute_name = entity_id.split("@", 1)
        
        # Determine the appropriate service call based on entity domain and property type
        domain = entity_id.split(".")[0]
        
        try:
            if domain == "light":
                await self._update_light_entity(entity_id, value, property_type, attribute_name)
            elif domain == "cover":
                await self._update_cover_entity(entity_id, value, property_type, attribute_name)
            elif domain == "climate":
                await self._update_climate_entity(entity_id, value, property_type, attribute_name)
            elif domain == "switch":
                await self._update_switch_entity(entity_id, value, property_type)
            elif domain in ["sensor", "binary_sensor"]:
                # Sensors are typically read-only, but we can update their state if they're template sensors
                await self._update_sensor_entity(entity_id, value)
            elif domain == "input_number":
                await self.hass.services.async_call(
                    "input_number",
                    "set_value",
                    {"entity_id": entity_id, "value": value},
                    blocking=True,
                )
            elif domain == "input_boolean":
                service = "turn_on" if value else "turn_off"
                await self.hass.services.async_call(
                    "input_boolean",
                    service,
                    {"entity_id": entity_id},
                    blocking=True,
                )
            elif domain == "input_text":
                await self.hass.services.async_call(
                    "input_text",
                    "set_value",
                    {"entity_id": entity_id, "value": str(value)},
                    blocking=True,
                )
            else:
                _LOGGER.warning(f"Unsupported entity domain for pushing: {domain}")
                
        except Exception as e:
            _LOGGER.error(f"Error pushing value to entity {entity_id}: {e}")
            raise
    
    async def _update_light_entity(
        self,
        entity_id: str,
        value: Any,
        property_type: StatePropertyType,
        attribute_name: Optional[str] = None,
    ) -> None:
        """Update a light entity."""
        if property_type == StatePropertyType.CHANNEL_VALUE:
            # Determine what channel value represents
            if attribute_name == "brightness" or attribute_name is None:
                # Brightness channel
                await self.hass.services.async_call(
                    "light",
                    "turn_on",
                    {"entity_id": entity_id, "brightness": int(value * 255 / 100)},
                    blocking=True,
                )
            elif attribute_name in ["red", "green", "blue", "white"]:
                # RGB/RGBW channel - would need to read current state and update one component
                _LOGGER.debug(f"RGB component update for {entity_id}: {attribute_name}={value}")
                # This is complex and would need the full RGB value to update properly
                # For now, just log it
        elif property_type == StatePropertyType.BINARY_VALUE:
            # On/off control
            service = "turn_on" if value else "turn_off"
            await self.hass.services.async_call(
                "light",
                service,
                {"entity_id": entity_id},
                blocking=True,
            )
    
    async def _update_cover_entity(
        self,
        entity_id: str,
        value: Any,
        property_type: StatePropertyType,
        attribute_name: Optional[str] = None,
    ) -> None:
        """Update a cover entity."""
        if property_type == StatePropertyType.CHANNEL_VALUE:
            if attribute_name == "position" or attribute_name is None:
                # Position channel
                await self.hass.services.async_call(
                    "cover",
                    "set_cover_position",
                    {"entity_id": entity_id, "position": int(value)},
                    blocking=True,
                )
            elif attribute_name == "tilt":
                # Tilt channel
                await self.hass.services.async_call(
                    "cover",
                    "set_cover_tilt_position",
                    {"entity_id": entity_id, "tilt_position": int(value)},
                    blocking=True,
                )
    
    async def _update_climate_entity(
        self,
        entity_id: str,
        value: Any,
        property_type: StatePropertyType,
        attribute_name: Optional[str] = None,
    ) -> None:
        """Update a climate entity."""
        if property_type in [
            StatePropertyType.CONTROL_HEATING_LEVEL,
            StatePropertyType.CONTROL_COOLING_LEVEL,
        ]:
            # Set temperature
            await self.hass.services.async_call(
                "climate",
                "set_temperature",
                {"entity_id": entity_id, "temperature": float(value)},
                blocking=True,
            )
        elif property_type == StatePropertyType.CONTROL_VENTILATION_LEVEL:
            # Set fan mode (would need mapping from level to fan mode)
            _LOGGER.debug(f"Ventilation level update for {entity_id}: {value}")
    
    async def _update_switch_entity(
        self,
        entity_id: str,
        value: Any,
        property_type: StatePropertyType,
    ) -> None:
        """Update a switch entity."""
        service = "turn_on" if value else "turn_off"
        await self.hass.services.async_call(
            "switch",
            service,
            {"entity_id": entity_id},
            blocking=True,
        )
    
    async def _update_sensor_entity(
        self,
        entity_id: str,
        value: Any,
    ) -> None:
        """Update a sensor entity state.
        
        Note: This only works for certain sensor types that support state updates.
        Most sensors are read-only from HA's perspective.
        """
        # For template sensors or MQTT sensors, we'd need to publish to their update mechanism
        _LOGGER.debug(f"Sensor state update requested for {entity_id}: {value}")
        # This is typically not supported - sensors pull data, not push
    
    def _should_persist(
        self,
        property_type: StatePropertyType,
        override: Optional[bool],
    ) -> bool:
        """Determine if a STATE property should be persisted.
        
        Args:
            property_type: Type of STATE property
            override: Override decision (True/False/None for auto)
            
        Returns:
            True if should persist, False otherwise
        """
        if override is not None:
            return override
        
        # Critical properties MUST be persisted
        if property_type in self.critical_persistent_properties:
            return True
        
        # Recommended properties SHOULD be persisted
        if property_type in self.recommended_persistent_properties:
            return True
        
        # Transient properties (button clicks, etc.) are NOT persisted by default
        if property_type in [
            StatePropertyType.BUTTON_VALUE,
            StatePropertyType.BUTTON_ACTION_ID,
            StatePropertyType.BUTTON_ACTION_MODE,
        ]:
            return False
        
        # Default: persist for safety
        return True
    
    def _store_state_value(
        self,
        device: VirtualDevice,
        property_type: StatePropertyType,
        value: Any,
        index: Optional[int],
    ) -> None:
        """Store a STATE value in device attributes for persistence.
        
        Args:
            device: VirtualDevice instance
            property_type: Type of STATE property
            value: Value to store
            index: Optional index for multi-instance properties
        """
        # Create state_values dict if it doesn't exist
        if "state_values" not in device.attributes:
            device.attributes["state_values"] = {}
        
        state_values = device.attributes["state_values"]
        
        # Build the storage key
        if index is not None:
            key = f"{property_type.value}[{index}]"
        else:
            key = property_type.value
        
        # Store the value with timestamp
        state_values[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
        }


class PropertyUpdater:
    """Unified property updater for CONFIG and STATE properties.
    
    This class provides a single interface for updating any property type,
    automatically routing to the appropriate updater.
    """
    
    def __init__(
        self,
        hass: HomeAssistant,
        device_storage: DeviceStorage,
    ):
        """Initialize the property updater.
        
        Args:
            hass: Home Assistant instance
            device_storage: DeviceStorage instance
        """
        self.hass = hass
        self.config_updater = ConfigPropertyUpdater(hass, device_storage)
        self.state_updater = StatePropertyUpdater(hass, device_storage)
    
    async def update_property(
        self,
        device_id: str,
        property_type: str,
        value: Any,
        index: Optional[int] = None,
        persist_state: Optional[bool] = None,
    ) -> bool:
        """Update any property (CONFIG or STATE).
        
        Args:
            device_id: Device identifier
            property_type: Property type (can be StatePropertyType enum or string path)
            value: New value
            index: Optional index for multi-instance properties
            persist_state: For STATE properties, override auto-persistence
            
        Returns:
            True if update successful, False otherwise
        """
        # Try to parse as StatePropertyType
        try:
            state_prop_type = StatePropertyType(property_type)
            # It's a STATE property
            return await self.state_updater.update_state_property(
                device_id, state_prop_type, value, index, persist_state
            )
        except ValueError:
            # It's a CONFIG property
            return await self.config_updater.update_config_property(
                device_id, property_type, value, index
            )
