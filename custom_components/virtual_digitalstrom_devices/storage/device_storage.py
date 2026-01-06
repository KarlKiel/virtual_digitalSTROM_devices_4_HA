"""Device storage module for persisting virtual devices to YAML.

This module provides the DeviceStorage class which handles reading and writing
virtual device configurations to a YAML file.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

# Handle both package imports (when used as Home Assistant integration)
# and standalone imports (for examples/testing)
try:
    from ..models.virtual_device import VirtualDevice
except ImportError:
    import virtual_device  # type: ignore
    VirtualDevice = virtual_device.VirtualDevice  # type: ignore

_LOGGER = logging.getLogger(__name__)


class DeviceStorage:
    """Handles YAML-based storage for virtual devices.
    
    This class manages the persistence of VirtualDevice instances to a YAML file,
    providing methods to add, update, delete, and retrieve devices.
    """
    
    def __init__(self, storage_path: Path) -> None:
        """Initialize the device storage.
        
        Args:
            storage_path: Path to the YAML storage file
        """
        self.storage_path = storage_path
        self._devices: dict[str, VirtualDevice] = {}
        # Don't load in __init__ to avoid blocking I/O in async context
        # Call load() separately when needed
    
    def load(self) -> None:
        """Load devices from YAML file (synchronous)."""
        self._load()
    
    def _load(self) -> None:
        """Load devices from YAML file."""
        try:
            if self.storage_path.exists():
                _LOGGER.debug("Loading devices from %s", self.storage_path)
                with open(self.storage_path, "r", encoding="utf-8") as file:
                    data = yaml.safe_load(file) or {}
                    devices_data = data.get("devices", [])
                    
                    self._devices = {}
                    for device_data in devices_data:
                        device = VirtualDevice.from_dict(device_data)
                        self._devices[device.device_id] = device
                    
                    _LOGGER.info("Loaded %d device(s) from storage", len(self._devices))
            else:
                _LOGGER.debug("Storage file does not exist, starting with empty device list")
                self._devices = {}
        except (yaml.YAMLError, ValueError, KeyError) as e:
            _LOGGER.error("Error parsing device data from %s: %s", self.storage_path, e)
            self._devices = {}
        except (FileNotFoundError, PermissionError, OSError) as e:
            _LOGGER.error("Error accessing storage file %s: %s", self.storage_path, e)
            self._devices = {}
    
    def _save(self) -> None:
        """Save devices to YAML file."""
        try:
            # Ensure parent directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare data structure
            data = {
                "devices": [device.to_dict() for device in self._devices.values()]
            }
            
            # Write to YAML file
            with open(self.storage_path, "w", encoding="utf-8") as file:
                yaml.safe_dump(data, file, default_flow_style=False, sort_keys=False)
            
            _LOGGER.debug("Saved %d device(s) to %s", len(self._devices), self.storage_path)
        except yaml.YAMLError as e:
            _LOGGER.error("Error serializing device data to YAML: %s", e)
        except (FileNotFoundError, PermissionError, OSError) as e:
            _LOGGER.error("Error writing to storage file %s: %s", self.storage_path, e)
    
    def add_device(self, device: VirtualDevice) -> bool:
        """Add a new device to storage.
        
        Args:
            device: VirtualDevice instance to add
            
        Returns:
            True if device was added successfully, False if device_id already exists
        """
        if device.device_id in self._devices:
            _LOGGER.warning("Device with id %s already exists", device.device_id)
            return False
        
        self._devices[device.device_id] = device
        self._save()
        _LOGGER.info("Added device: %s (id: %s)", device.name, device.device_id)
        return True
    
    def update_device(self, device_id: str, **kwargs: Any) -> bool:
        """Update an existing device.
        
        Args:
            device_id: ID of the device to update
            **kwargs: Attributes to update
            
        Returns:
            True if device was updated successfully, False if device not found
        """
        if device_id not in self._devices:
            _LOGGER.warning("Device with id %s not found", device_id)
            return False
        
        self._devices[device_id].update(**kwargs)
        self._save()
        _LOGGER.info("Updated device: %s", device_id)
        return True
    
    def save_device(self, device: VirtualDevice) -> bool:
        """Save an existing device's current state.
        
        This method saves a device object that has already been modified,
        useful when you've made multiple changes to a device instance
        and want to persist them all at once.
        
        Args:
            device: VirtualDevice instance to save
            
        Returns:
            True if device was saved successfully, False if device not found
        """
        if device.device_id not in self._devices:
            _LOGGER.warning("Device with id %s not found", device.device_id)
            return False
        
        # Update the reference in storage (in case it's a different object)
        self._devices[device.device_id] = device
        self._save()
        _LOGGER.debug("Saved device: %s", device.device_id)
        return True
    
    def delete_device(self, device_id: str) -> bool:
        """Delete a device from storage.
        
        Args:
            device_id: ID of the device to delete
            
        Returns:
            True if device was deleted successfully, False if device not found
        """
        if device_id not in self._devices:
            _LOGGER.warning("Device with id %s not found", device_id)
            return False
        
        device = self._devices.pop(device_id)
        self._save()
        _LOGGER.info("Deleted device: %s (id: %s)", device.name, device_id)
        return True
    
    def get_device(self, device_id: str) -> VirtualDevice | None:
        """Get a device by ID.
        
        Args:
            device_id: ID of the device to retrieve
            
        Returns:
            VirtualDevice instance if found, None otherwise
        """
        return self._devices.get(device_id)
    
    def get_device_by_dsid(self, dsid: str) -> VirtualDevice | None:
        """Get a device by dsid.
        
        Args:
            dsid: digitalSTROM UID of the device to retrieve
            
        Returns:
            VirtualDevice instance if found, None otherwise
        """
        for device in self._devices.values():
            if device.dsid == dsid:
                return device
        return None
    
    def delete_device_by_dsid(self, dsid: str) -> bool:
        """Delete a device from storage by dsid.
        
        Args:
            dsid: digitalSTROM UID of the device to delete
            
        Returns:
            True if device was deleted successfully, False if device not found
        """
        # Find the device_id for this dsid
        for device_id, device in self._devices.items():
            if device.dsid == dsid:
                return self.delete_device(device_id)
        
        _LOGGER.warning("Device with dsid %s not found", dsid)
        return False
    
    def get_all_devices(self) -> list[VirtualDevice]:
        """Get all devices.
        
        Returns:
            List of all VirtualDevice instances
        """
        return list(self._devices.values())
    
    def _get_group_id_value(self, group_id: Any) -> int:
        """Extract integer value from group_id, handling both enum and int types.
        
        Args:
            group_id: Group ID as either int or enum
            
        Returns:
            Integer value of the group ID
        """
        return group_id.value if hasattr(group_id, 'value') else group_id
    
    def get_devices_by_group(self, group_id: int) -> list[VirtualDevice]:
        """Get all devices in a specific device class group.
        
        Args:
            group_id: digitalSTROM group ID (can be int or enum)
            
        Returns:
            List of VirtualDevice instances in the group
        """
        group_id_value = self._get_group_id_value(group_id)
        return [
            device for device in self._devices.values() 
            if self._get_group_id_value(device.group_id) == group_id_value
        ]
    
    def device_exists(self, device_id: str) -> bool:
        """Check if a device exists.
        
        Args:
            device_id: ID of the device to check
            
        Returns:
            True if device exists, False otherwise
        """
        return device_id in self._devices
