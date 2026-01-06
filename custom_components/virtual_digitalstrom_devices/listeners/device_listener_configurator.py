"""Device listener configurator - automatically creates listeners for all device STATE properties.

This module analyzes virtual device configurations and automatically creates
the appropriate state listeners for all STATE-classified properties that the
device implements.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from homeassistant.core import HomeAssistant

from .state_listener import (
    BooleanStateListener,
    EnumStateListener,
    IntegerStateListener,
    NumericStateListener,
    StateListener,
    StatePropertyType,
    StringStateListener,
    AttributeStateListener,
)
from .state_listener_manager import StateListenerManager
from ..models.virtual_device import VirtualDevice

_LOGGER = logging.getLogger(__name__)


class DeviceListenerConfigurator:
    """Configures state listeners for virtual devices based on their properties.
    
    This class analyzes a device's configuration and automatically creates
    the appropriate state listeners for all STATE properties that the device
    implements (buttons, sensors, channels, outputs, control values, etc.).
    """
    
    # Mapping of property patterns to listener classes
    PROPERTY_LISTENER_MAP = {
        "button.value": BooleanStateListener,
        "button.error": EnumStateListener,
        "button.actionId": IntegerStateListener,
        "button.actionMode": EnumStateListener,
        "binary.value": BooleanStateListener,
        "binary.extendedValue": IntegerStateListener,
        "binary.error": EnumStateListener,
        "sensor.value": NumericStateListener,
        "sensor.contextId": IntegerStateListener,
        "sensor.contextMsg": StringStateListener,
        "sensor.error": EnumStateListener,
        "channel.value": NumericStateListener,
        "output.localPriority": BooleanStateListener,
        "output.error": EnumStateListener,
        "control.heatingLevel": NumericStateListener,
        "control.coolingLevel": NumericStateListener,
        "control.ventilationLevel": NumericStateListener,
        "device.progMode": BooleanStateListener,
        "device.connection_status": StringStateListener,
        "device.system_status": StringStateListener,
        "dynamicAction.name": StringStateListener,
        "dynamicAction.title": StringStateListener,
        "deviceState.name": StringStateListener,
        "deviceState.value": StringStateListener,
        "deviceProperty.name": StringStateListener,
        "deviceProperty.value": StringStateListener,
    }
    
    def __init__(self, hass: HomeAssistant, manager: StateListenerManager):
        """Initialize the configurator.
        
        Args:
            hass: Home Assistant instance
            manager: State listener manager to register listeners with
        """
        self.hass = hass
        self.manager = manager
    
    async def async_configure_device_listeners(
        self,
        device: VirtualDevice,
        entity_mappings: dict[str, Any],
    ) -> int:
        """Auto-configure state listeners for a virtual device.
        
        Args:
            device: Virtual device instance
            entity_mappings: Dictionary mapping property paths to HA entity IDs
                Example:
                {
                    "button[0].value": "binary_sensor.door_button",
                    "sensor[0].value": "sensor.temperature",
                    "channel[0].value": "light.living_room",
                    "control.heatingLevel": "climate.bedroom",
                }
        
        Returns:
            Number of listeners created
        """
        listener_count = 0
        device_id = device.device_id
        
        _LOGGER.info(
            "Configuring state listeners for device %s (%s)",
            device.name,
            device_id,
        )
        
        # Process each entity mapping
        for property_path, entity_id in entity_mappings.items():
            try:
                listener = await self._create_listener_for_property(
                    device_id=device_id,
                    property_path=property_path,
                    entity_id=entity_id,
                )
                if listener:
                    listener_count += 1
            except Exception as err:
                _LOGGER.error(
                    "Error creating listener for %s -> %s: %s",
                    property_path,
                    entity_id,
                    err,
                    exc_info=True,
                )
        
        _LOGGER.info(
            "Created %d state listeners for device %s",
            listener_count,
            device.name,
        )
        
        return listener_count
    
    async def _create_listener_for_property(
        self,
        device_id: str,
        property_path: str,
        entity_id: str,
    ) -> Optional[StateListener]:
        """Create a listener for a specific property path.
        
        Args:
            device_id: Virtual device ID
            property_path: Property path (e.g., "button[0].value", "sensor[1].value")
            entity_id: Home Assistant entity ID to track
            
        Returns:
            Created listener or None if property type not supported
        """
        # Parse property path to extract type, index, and property name
        parts = self._parse_property_path(property_path)
        if not parts:
            _LOGGER.warning("Invalid property path: %s", property_path)
            return None
        
        property_type_str = parts["property_type"]
        index = parts.get("index")
        attribute_name = parts.get("attribute")
        
        # Get property type enum
        try:
            property_type = StatePropertyType(property_type_str)
        except ValueError:
            _LOGGER.warning("Unknown property type: %s", property_type_str)
            return None
        
        # Get listener class
        listener_class = self.PROPERTY_LISTENER_MAP.get(property_type_str)
        if not listener_class:
            _LOGGER.warning("No listener class for property type: %s", property_type_str)
            return None
        
        # Create and register listener
        listener = await self.manager.async_add_listener(
            device_id=device_id,
            entity_id=entity_id,
            property_type=property_type,
            listener_class=listener_class,
            index=index,
            attribute_name=attribute_name,
            auto_start=True,
        )
        
        _LOGGER.debug(
            "Created listener: %s[%s] -> %s (%s)",
            property_type_str,
            index if index is not None else "",
            entity_id,
            listener_class.__name__,
        )
        
        return listener
    
    def _parse_property_path(self, path: str) -> Optional[dict[str, Any]]:
        """Parse a property path into components.
        
        Examples:
            "button[0].value" -> {property_type: "button.value", index: 0}
            "sensor[1].value" -> {property_type: "sensor.value", index: 1}
            "channel[0].value" -> {property_type: "channel.value", index: 0}
            "control.heatingLevel" -> {property_type: "control.heatingLevel"}
            "device.progMode" -> {property_type: "device.progMode"}
        
        Args:
            path: Property path string
            
        Returns:
            Dictionary with parsed components or None if invalid
        """
        import re
        
        # Pattern: category[index].property or category.property
        pattern = r"^(\w+)(?:\[(\d+)\])?\.(\w+)(?:@(\w+))?$"
        match = re.match(pattern, path)
        
        if not match:
            return None
        
        category, index_str, property_name, attribute = match.groups()
        
        # Build property type string
        property_type = f"{category}.{property_name}"
        
        result = {
            "property_type": property_type,
            "category": category,
            "property": property_name,
        }
        
        if index_str:
            result["index"] = int(index_str)
        
        if attribute:
            result["attribute"] = attribute
        
        return result
    
    async def async_configure_from_device_attributes(
        self,
        device: VirtualDevice,
    ) -> int:
        """Auto-configure listeners based on device attributes.
        
        This method inspects the device's attributes dictionary to find
        entity mappings and automatically creates listeners.
        
        Expected attribute structure:
        {
            "entity_mappings": {
                "button[0].value": "binary_sensor.door_button",
                "sensor[0].value": "sensor.temperature",
                ...
            }
        }
        
        Args:
            device: Virtual device instance
            
        Returns:
            Number of listeners created
        """
        entity_mappings = device.attributes.get("entity_mappings", {})
        
        if not entity_mappings:
            _LOGGER.debug(
                "No entity mappings found in device %s attributes",
                device.name,
            )
            return 0
        
        return await self.async_configure_device_listeners(device, entity_mappings)
    
    def get_recommended_mappings(
        self,
        device: VirtualDevice,
    ) -> dict[str, list[str]]:
        """Get recommended entity types for device properties.
        
        Based on the device's group_id and modelFeatures, suggests what
        types of HA entities should be mapped to each property.
        
        This handles multiple instances of the same property type.
        For example, a device might have:
        - 3 buttons (button[0], button[1], button[2])
        - 2 sensors (sensor[0], sensor[1])
        - 4 channels (channel[0], channel[1], channel[2], channel[3])
        
        Args:
            device: Virtual device instance
            
        Returns:
            Dictionary mapping property paths to lists of recommended entity domains
            
        Example:
            {
                "button[0].value": ["binary_sensor", "input_boolean"],
                "button[1].value": ["binary_sensor", "input_boolean"],
                "sensor[0].value": ["sensor"],
                "sensor[1].value": ["sensor"],
                "channel[0].value": ["light", "switch"],
                "channel[1].value": ["light", "switch"],
                "control.heatingLevel": ["climate"],
            }
        """
        recommendations = {}
        
        # Get device attributes to determine how many instances of each property type
        attributes = device.attributes or {}
        
        # Determine number of buttons, sensors, channels from attributes
        num_buttons = attributes.get("num_buttons", 0)
        num_binary_inputs = attributes.get("num_binary_inputs", 0)
        num_sensors = attributes.get("num_sensors", 0)
        num_channels = attributes.get("num_channels", 0)
        
        # Based on device group (from DEVICE_CLASSES.md)
        group_id = device.group_id
        
        # Group 1: Lights
        if group_id == 1:
            # Typically 1 brightness channel, possibly color channels
            for i in range(num_channels or 1):
                recommendations[f"channel[{i}].value"] = ["light"]
            # Power consumption sensor
            for i in range(num_sensors or 1):
                recommendations[f"sensor[{i}].value"] = ["sensor"]
            # Physical buttons (if any)
            for i in range(num_buttons):
                recommendations[f"button[{i}].value"] = ["binary_sensor", "switch"]
        
        # Group 2: Blinds/Shades
        elif group_id == 2:
            # Position channel
            recommendations["channel[0].value"] = ["cover"]
            # Tilt angle channel (if exists)
            if num_channels > 1:
                recommendations["channel[1].value"] = ["cover"]
            # Additional channels
            for i in range(2, num_channels):
                recommendations[f"channel[{i}].value"] = ["cover"]
            # Up/down buttons
            for i in range(num_buttons):
                recommendations[f"button[{i}].value"] = ["binary_sensor"]
        
        # Group 3: Heating (Climate)
        elif group_id == 3:
            recommendations["control.heatingLevel"] = ["climate"]
            # Temperature sensors
            for i in range(num_sensors or 1):
                recommendations[f"sensor[{i}].value"] = ["sensor"]
            # Valve position channel (if exists)
            for i in range(num_channels):
                recommendations[f"channel[{i}].value"] = ["climate", "sensor"]
        
        # Group 4: Audio
        elif group_id == 4:
            # Volume channel
            recommendations["channel[0].value"] = ["media_player"]
            # Additional channels (bass, treble, etc.)
            for i in range(1, num_channels):
                recommendations[f"channel[{i}].value"] = ["media_player", "number"]
            # Control buttons
            for i in range(num_buttons):
                recommendations[f"button[{i}].value"] = ["binary_sensor"]
        
        # Group 5: Video
        elif group_id == 5:
            for i in range(num_channels or 1):
                recommendations[f"channel[{i}].value"] = ["media_player"]
            for i in range(num_buttons):
                recommendations[f"button[{i}].value"] = ["binary_sensor"]
        
        # Group 8: Joker/Generic - most flexible
        elif group_id == 8:
            for i in range(num_sensors or 1):
                recommendations[f"sensor[{i}].value"] = ["sensor"]
            for i in range(num_binary_inputs):
                recommendations[f"binary[{i}].value"] = ["binary_sensor"]
            for i in range(num_buttons):
                recommendations[f"button[{i}].value"] = ["binary_sensor", "switch"]
            for i in range(num_channels):
                recommendations[f"channel[{i}].value"] = ["light", "switch", "number"]
        
        # Group 9: Cooling/Ventilation
        elif group_id == 9:
            recommendations["control.coolingLevel"] = ["climate"]
            recommendations["control.ventilationLevel"] = ["fan"]
            for i in range(num_sensors or 1):
                recommendations[f"sensor[{i}].value"] = ["sensor"]
            for i in range(num_channels):
                recommendations[f"channel[{i}].value"] = ["climate", "fan"]
        
        # Add common recommendations for all devices
        recommendations["device.connection_status"] = ["binary_sensor"]
        recommendations["device.progMode"] = ["input_boolean"]
        
        return recommendations


def create_default_entity_mappings(
    device: VirtualDevice,
    ha_entities: dict[str, str],
) -> dict[str, str]:
    """Create default entity mappings for a device.
    
    Helper function to create sensible default mappings when setting up
    a new virtual device.
    
    Args:
        device: Virtual device instance
        ha_entities: Available HA entities with their domains
            Example: {"light.living_room": "light", "sensor.temp": "sensor"}
    
    Returns:
        Dictionary of property paths to entity IDs
        
    Example:
        device = VirtualDevice(name="Living Room Light", group_id=1, ...)
        ha_entities = {
            "light.living_room": "light",
            "sensor.living_room_power": "sensor",
        }
        mappings = create_default_entity_mappings(device, ha_entities)
        # Returns: {
        #     "channel[0].value": "light.living_room",
        #     "sensor[0].value": "sensor.living_room_power",
        # }
    """
    configurator = DeviceListenerConfigurator(None, None)
    recommendations = configurator.get_recommended_mappings(device)
    
    mappings = {}
    
    # Try to find matching entities for each recommended property
    for property_path, recommended_domains in recommendations.items():
        for entity_id, domain in ha_entities.items():
            if domain in recommended_domains:
                # Simple heuristic: prefer entities with matching names
                if device.name.lower().replace(" ", "_") in entity_id.lower():
                    mappings[property_path] = entity_id
                    break
                # Or just use first matching domain
                elif property_path not in mappings:
                    mappings[property_path] = entity_id
    
    return mappings
