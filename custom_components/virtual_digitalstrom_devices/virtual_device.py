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
    
    This class includes both the common properties for all addressable entities
    (per vDC spec Section 2) and device-specific configuration properties.
    
    Common Properties (vDC Spec Section 2):
        device_id (str): Internal UUID for HA integration (auto-generated)
        dsid (str): dSUID - digitalSTROM device ID (auto-generated, 34 hex chars)
        display_id (str): Human-readable identification printed on physical device
        type (str): Entity type, always "vdSD" for virtual devices
        model (str): Human-readable model string
        model_version (str): Model version (firmware version)
        model_uid (str): digitalSTROM system unique ID for functional model
        hardware_version (str): Hardware version string (optional)
        hardware_guid (str): Hardware GUID in URN format (optional)
    
    Device-Specific Properties:
        name (str): User-friendly device name (HA-specific)
        group_id (int): digitalSTROM group ID (device class)
        ha_entity_id (str): Home Assistant entity ID this device is mapped to
        zone_id (int): Zone/room ID where the device is located
        attributes (dict): Additional device-specific attributes
    """
    
    # Common properties for all addressable entities (vDC Spec Section 2)
    device_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dsid: str = field(default_factory=lambda: str(uuid.uuid4()))  # dSUID in vDC spec
    display_id: str = ""
    type: str = "vdSD"  # Always vdSD for virtual devices
    model: str = ""
    model_version: str = ""
    model_uid: str = ""
    hardware_version: str = ""
    hardware_guid: str = ""
    
    # Device-specific properties (HA integration + vDC general device properties)
    name: str = ""
    group_id: int = 0
    ha_entity_id: str = ""
    zone_id: int = 0
    attributes: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert device to dictionary for YAML serialization.
        
        Returns:
            Dictionary representation of the device with all properties
        """
        # Convert enum to int if group_id is an Enum
        group_id_value = self.group_id.value if isinstance(self.group_id, Enum) else self.group_id
        
        return {
            # Common properties (vDC Spec Section 2)
            "device_id": self.device_id,
            "dsid": self.dsid,
            "display_id": self.display_id,
            "type": self.type,
            "model": self.model,
            "model_version": self.model_version,
            "model_uid": self.model_uid,
            "hardware_version": self.hardware_version,
            "hardware_guid": self.hardware_guid,
            # Device-specific properties
            "name": self.name,
            "group_id": int(group_id_value),
            "ha_entity_id": self.ha_entity_id,
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
            # Common properties (vDC Spec Section 2)
            device_id=data.get("device_id", str(uuid.uuid4())),
            dsid=data.get("dsid", str(uuid.uuid4())),
            display_id=data.get("display_id", ""),
            type=data.get("type", "vdSD"),
            model=data.get("model", ""),
            model_version=data.get("model_version", ""),
            model_uid=data.get("model_uid", ""),
            hardware_version=data.get("hardware_version", ""),
            hardware_guid=data.get("hardware_guid", ""),
            # Device-specific properties
            name=data.get("name", ""),
            group_id=data.get("group_id", 0),
            ha_entity_id=data.get("ha_entity_id", ""),
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
