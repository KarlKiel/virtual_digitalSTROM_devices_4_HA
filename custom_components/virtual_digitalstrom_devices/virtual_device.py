"""Virtual device representation for digitalSTROM integration.

This module defines the VirtualDevice class which represents a configured
device instance that can be persisted to YAML storage.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import uuid


@dataclass
class VirtualDevice:
    """Represents a virtual digitalSTROM device instance.
    
    Attributes:
        device_id: Unique identifier for the device
        name: Human-readable device name
        group_id: digitalSTROM group ID (device class)
        ha_entity_id: Home Assistant entity ID this device is mapped to
        dsid: digitalSTROM device ID (dSID)
        zone_id: Zone/room ID where the device is located
        attributes: Additional device-specific attributes
    """
    
    device_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    group_id: int = 0
    ha_entity_id: str = ""
    dsid: str = field(default_factory=lambda: str(uuid.uuid4()))
    zone_id: int = 0
    attributes: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert device to dictionary for YAML serialization.
        
        Returns:
            Dictionary representation of the device
        """
        # Convert enum to int if group_id is an Enum
        group_id_value = self.group_id.value if isinstance(self.group_id, Enum) else self.group_id
        
        return {
            "device_id": self.device_id,
            "name": self.name,
            "group_id": int(group_id_value),
            "ha_entity_id": self.ha_entity_id,
            "dsid": self.dsid,
            "zone_id": self.zone_id,
            "attributes": self.attributes,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VirtualDevice:
        """Create device from dictionary loaded from YAML.
        
        Args:
            data: Dictionary containing device data
            
        Returns:
            VirtualDevice instance
        """
        return cls(
            device_id=data.get("device_id", str(uuid.uuid4())),
            name=data.get("name", ""),
            group_id=data.get("group_id", 0),
            ha_entity_id=data.get("ha_entity_id", ""),
            dsid=data.get("dsid", str(uuid.uuid4())),
            zone_id=data.get("zone_id", 0),
            attributes=data.get("attributes", {}),
        )
    
    def update(self, **kwargs: Any) -> None:
        """Update device attributes.
        
        Args:
            **kwargs: Attributes to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
