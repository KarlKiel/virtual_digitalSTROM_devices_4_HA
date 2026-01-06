"""State restoration module for virtual digitalSTROM devices.

This module handles restoring persisted STATE property values after startup,
recreating device states from YAML storage and optionally pushing them to
Home Assistant entities.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Optional

from homeassistant.core import HomeAssistant

from .device_storage import DeviceStorage
from .property_updater import PropertyUpdater, StatePropertyUpdater
from .state_listener import StatePropertyType
from .virtual_device import VirtualDevice

_LOGGER = logging.getLogger(__name__)


class StateRestorer:
    """Restores persisted STATE property values for virtual devices.
    
    This class reads state_values from device attributes (persisted in YAML)
    and restores them to:
    1. Python object state (internal device state tracking)
    2. Home Assistant entities (optional, to sync HA with persisted values)
    """
    
    def __init__(
        self,
        hass: HomeAssistant,
        device_storage: DeviceStorage,
        property_updater: PropertyUpdater,
    ):
        """Initialize the state restorer.
        
        Args:
            hass: Home Assistant instance
            device_storage: DeviceStorage instance with loaded devices
            property_updater: PropertyUpdater for applying state updates
        """
        self.hass = hass
        self.device_storage = device_storage
        self.property_updater = property_updater
        self.state_updater = property_updater.state_updater
    
    async def async_restore_all_devices(
        self,
        push_to_entities: bool = False,
    ) -> dict[str, Any]:
        """Restore state for all devices in storage.
        
        Args:
            push_to_entities: If True, push restored values to HA entities.
                If False, only restore internal state tracking.
        
        Returns:
            Dictionary with restoration statistics:
            {
                "total_devices": int,
                "devices_with_state": int,
                "total_properties_restored": int,
                "devices_restored": {device_id: properties_count},
                "errors": [error_messages],
            }
        """
        devices = self.device_storage.get_all_devices()
        
        stats = {
            "total_devices": len(devices),
            "devices_with_state": 0,
            "total_properties_restored": 0,
            "devices_restored": {},
            "errors": [],
        }
        
        _LOGGER.info(
            "Starting state restoration for %d devices (push_to_entities=%s)",
            len(devices),
            push_to_entities,
        )
        
        for device in devices:
            try:
                count = await self.async_restore_device_state(
                    device,
                    push_to_entities=push_to_entities,
                )
                
                if count > 0:
                    stats["devices_with_state"] += 1
                    stats["total_properties_restored"] += count
                    stats["devices_restored"][device.device_id] = count
                    
            except Exception as err:
                error_msg = f"Error restoring state for device {device.name}: {err}"
                _LOGGER.error(error_msg, exc_info=True)
                stats["errors"].append(error_msg)
        
        _LOGGER.info(
            "State restoration complete: %d devices, %d properties restored",
            stats["devices_with_state"],
            stats["total_properties_restored"],
        )
        
        if stats["errors"]:
            _LOGGER.warning("Encountered %d errors during restoration", len(stats["errors"]))
        
        return stats
    
    async def async_restore_device_state(
        self,
        device: VirtualDevice,
        push_to_entities: bool = False,
    ) -> int:
        """Restore state for a single device.
        
        Args:
            device: VirtualDevice instance to restore
            push_to_entities: If True, push restored values to HA entities
        
        Returns:
            Number of properties restored
        """
        # Get persisted state values from device attributes
        state_values = device.attributes.get("state_values", {})
        
        if not state_values:
            _LOGGER.debug("No persisted state values for device %s", device.name)
            return 0
        
        _LOGGER.info(
            "Restoring %d state values for device %s",
            len(state_values),
            device.name,
        )
        
        restored_count = 0
        
        for state_key, state_data in state_values.items():
            try:
                # Extract value and optional metadata
                if isinstance(state_data, dict):
                    value = state_data.get("value")
                    timestamp = state_data.get("timestamp")
                else:
                    # Old format: just the value
                    value = state_data
                    timestamp = None
                
                if value is None:
                    _LOGGER.debug("Skipping null value for %s", state_key)
                    continue
                
                # Parse state key to get property type and optional index
                property_type, index = self._parse_state_key(state_key)
                
                if not property_type:
                    _LOGGER.warning("Could not parse state key: %s", state_key)
                    continue
                
                # Restore the state value
                await self._restore_property_value(
                    device=device,
                    property_type=property_type,
                    value=value,
                    index=index,
                    push_to_entity=push_to_entities,
                    timestamp=timestamp,
                )
                
                restored_count += 1
                
            except Exception as err:
                _LOGGER.error(
                    "Error restoring state %s for device %s: %s",
                    state_key,
                    device.name,
                    err,
                    exc_info=True,
                )
        
        if restored_count > 0:
            _LOGGER.info(
                "Successfully restored %d state values for device %s",
                restored_count,
                device.name,
            )
        
        return restored_count
    
    async def _restore_property_value(
        self,
        device: VirtualDevice,
        property_type: StatePropertyType,
        value: Any,
        index: Optional[int],
        push_to_entity: bool,
        timestamp: Optional[str] = None,
    ) -> None:
        """Restore a single property value.
        
        Args:
            device: VirtualDevice instance
            property_type: Type of STATE property
            value: Value to restore
            index: Optional index for array properties
            push_to_entity: Whether to push value to HA entity
            timestamp: Optional timestamp when value was saved
        """
        device_id = device.device_id
        
        _LOGGER.debug(
            "Restoring %s[%s] = %s for device %s (timestamp: %s)",
            property_type.value,
            index if index is not None else "",
            value,
            device.name,
            timestamp or "unknown",
        )
        
        if push_to_entity:
            # Use the state updater to push the value to HA entity
            # This will also re-persist it (which is fine, ensures consistency)
            try:
                await self.state_updater.update_state_property(
                    device_id=device_id,
                    property_type=property_type,
                    value=value,
                    index=index,
                    persist=False,  # Avoid duplicate persistence - value already exists in storage
                )
                _LOGGER.debug(
                    "Pushed restored value to HA entity for %s[%s]",
                    property_type.value,
                    index if index is not None else "",
                )
            except Exception as err:
                # Log but don't fail - entity might not exist yet
                _LOGGER.warning(
                    "Could not push restored value to HA entity for %s[%s]: %s",
                    property_type.value,
                    index if index is not None else "",
                    err,
                )
        else:
            # Just restore internal state tracking without pushing to entities
            # The state is already in device.attributes['state_values'],
            # but we log it for awareness
            _LOGGER.debug(
                "Internal state restored (not pushed): %s[%s] = %s",
                property_type.value,
                index if index is not None else "",
                value,
            )
    
    def _parse_state_key(self, key: str) -> tuple[Optional[StatePropertyType], Optional[int]]:
        """Parse a state key into property type and optional index.
        
        Args:
            key: State key (e.g., "channel.value[0]", "sensor.value", "control.heatingLevel")
        
        Returns:
            Tuple of (StatePropertyType, index) or (None, None) if invalid
        """
        # Pattern: "property.name[index]" or "property.name"
        pattern = r"^(.+?)(?:\[(\d+)\])?$"
        match = re.match(pattern, key)
        
        if not match:
            return None, None
        
        property_type_str, index_str = match.groups()
        
        # Try to parse as StatePropertyType
        try:
            property_type = StatePropertyType(property_type_str)
        except ValueError:
            _LOGGER.debug("Unknown state property type: %s", property_type_str)
            return None, None
        
        index = int(index_str) if index_str else None
        
        return property_type, index


async def restore_states_on_startup(
    hass: HomeAssistant,
    device_storage: DeviceStorage,
    property_updater: PropertyUpdater,
    push_to_entities: bool = False,
) -> dict[str, Any]:
    """Convenience function to restore states on integration startup.
    
    Args:
        hass: Home Assistant instance
        device_storage: DeviceStorage with loaded devices
        property_updater: PropertyUpdater for applying updates
        push_to_entities: Whether to push restored values to HA entities
    
    Returns:
        Restoration statistics dictionary
    """
    restorer = StateRestorer(hass, device_storage, property_updater)
    return await restorer.async_restore_all_devices(push_to_entities=push_to_entities)
