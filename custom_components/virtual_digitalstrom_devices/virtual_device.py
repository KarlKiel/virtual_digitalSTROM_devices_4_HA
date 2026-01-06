"""Virtual device representation for digitalSTROM integration.

This module defines the VirtualDevice class which represents a configured
device instance that can be persisted to YAML storage.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
import uuid

try:
    from .dsuid_generator import generate_dsuid, generate_random_dsuid
except ImportError:
    # Fallback if dsuid_generator is not available
    def generate_dsuid(**kwargs):
        """Fallback dSUID generator using UUID4."""
        # Generate UUID4 and convert to 17 bytes (136 bits) for dSUID
        import uuid
        uuid_bytes = uuid.uuid4().bytes  # 16 bytes
        dsuid_bytes = uuid_bytes + b'\x00'  # Add 1 byte padding = 17 bytes
        return dsuid_bytes.hex().upper()  # Convert to 34 hex characters
    
    def generate_random_dsuid():
        """Fallback random dSUID generator."""
        import uuid
        uuid_bytes = uuid.uuid4().bytes  # 16 bytes
        dsuid_bytes = uuid_bytes + b'\x00'  # Add 1 byte padding = 17 bytes
        return dsuid_bytes.hex().upper()  # Convert to 34 hex characters


@dataclass
class VirtualDevice:
    """Represents a virtual digitalSTROM device instance.
    
    This class includes both the common properties for all addressable entities
    (per vDC spec Section 2) and device-specific configuration properties.
    
    Common Properties (vDC Spec Section 2):
        device_id (str): Internal UUID for HA integration (auto-generated)
        dsid (str): dSUID - digitalSTROM device ID (34 hex chars, auto-generated)
        display_id (str): Human-readable identification printed on physical device
        type (str): Entity type, always "vdSD" for virtual devices
        model (str): Human-readable model string
        model_version (str): Model version (firmware version)
        model_uid (str): digitalSTROM system unique ID for functional model
        hardware_version (str): Hardware version string (optional)
        hardware_guid (str): Hardware GUID in URN format (optional)
        hardware_model_guid (str): Hardware model GUID (optional)
        vendor_name (str): Vendor/manufacturer name (optional)
        vendor_guid (str): Vendor GUID (optional)
        oem_guid (str): OEM product GUID (optional)
        oem_model_guid (str): OEM model GUID (optional)
        device_class (str): Device class profile name (optional)
        device_class_version (str): Device class version (optional)
        active (bool): Device is operational (optional)
    
    Device-Specific Properties:
        name (str): User-friendly device name (HA-specific)
        group_id (int): digitalSTROM group ID (device class)
        ha_entity_id (str): Home Assistant entity ID this device is mapped to
        zone_id (int): Zone/room ID where the device is located
        attributes (dict): Additional device-specific attributes
    """
    
    # Common properties for all addressable entities (vDC Spec Section 2)
    device_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dsid: str = ""  # dSUID in vDC spec - will be generated if empty
    display_id: str = ""
    type: str = "vdSD"  # Always vdSD for virtual devices
    model: str = ""
    model_version: str = ""
    model_uid: str = ""
    hardware_version: str = ""
    hardware_guid: str = ""
    hardware_model_guid: str = ""
    vendor_name: str = ""
    vendor_guid: str = ""
    oem_guid: str = ""
    oem_model_guid: str = ""
    device_class: str = ""
    device_class_version: str = ""
    active: Optional[bool] = None
    
    # Device-specific properties (HA integration + vDC general device properties)
    name: str = ""
    group_id: int = 0
    ha_entity_id: str = ""
    zone_id: int = 0
    attributes: dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize and validate device properties."""
        # Generate dSUID if not provided
        if not self.dsid:
            self.dsid = self.generate_dsuid()
    
    def generate_dsuid(self) -> str:
        """
        Generate dSUID following ds-basics.pdf Chapter 13.3 rules.
        
        Priority order:
        1. Use hardware_guid if available (supports multiple formats)
        2. Use ha_entity_id as unique name
        3. Use name as unique name
        4. Generate random dSUID (must be persisted!)
        
        Returns:
            34-character hex string (17 bytes)
        """
        # Priority 1: Use hardware GUID if available
        if self.hardware_guid:
            try:
                return generate_dsuid(hardware_guid=self.hardware_guid)
            except Exception as e:
                # Log the error but continue to next method
                import logging
                logging.warning(f"Failed to generate dSUID from hardware_guid: {e}")
        
        # Priority 2: Use HA entity ID as unique name
        if self.ha_entity_id:
            return generate_dsuid(unique_name=self.ha_entity_id)
        
        # Priority 3: Use device name if available
        if self.name:
            return generate_dsuid(unique_name=self.name)
        
        # Last resort: Generate random dSUID
        # WARNING: This must be persisted!
        return generate_random_dsuid()
    
    def regenerate_dsuid(
        self,
        gtin: Optional[str] = None,
        serial: Optional[str] = None,
        mac_address: Optional[str] = None,
        unique_name: Optional[str] = None,
    ) -> str:
        """
        Regenerate dSUID with specific parameters.
        
        This method allows explicit control over dSUID generation.
        The generated dSUID will replace the current one.
        
        Args:
            gtin: GTIN number (used with serial)
            serial: Serial number (used with GTIN)
            mac_address: MAC address
            unique_name: Unique identifier/name
            
        Returns:
            The newly generated dSUID
        """
        self.dsid = generate_dsuid(
            gtin=gtin,
            serial=serial,
            mac_address=mac_address,
            unique_name=unique_name or self.ha_entity_id,
        )
        return self.dsid
    
    def to_dict(self) -> dict[str, Any]:
        """Convert device to dictionary for YAML serialization.
        
        Note: Optional properties are only included if they have non-empty values.
        This keeps the serialized output clean and reduces storage size while
        maintaining full backward compatibility.
        
        Returns:
            Dictionary representation of the device with all properties
        """
        # Convert enum to int if group_id is an Enum
        group_id_value = self.group_id.value if isinstance(self.group_id, Enum) else self.group_id
        
        result = {
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
        
        # Add optional new properties if they have values
        # This keeps the YAML output clean and reduces file size
        if self.hardware_model_guid:
            result["hardware_model_guid"] = self.hardware_model_guid
        if self.vendor_name:
            result["vendor_name"] = self.vendor_name
        if self.vendor_guid:
            result["vendor_guid"] = self.vendor_guid
        if self.oem_guid:
            result["oem_guid"] = self.oem_guid
        if self.oem_model_guid:
            result["oem_model_guid"] = self.oem_model_guid
        if self.device_class:
            result["device_class"] = self.device_class
        if self.device_class_version:
            result["device_class_version"] = self.device_class_version
        if self.active is not None:
            result["active"] = self.active
        
        return result
    
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
            dsid=data.get("dsid", ""),  # Empty string will trigger auto-generation
            display_id=data.get("display_id", ""),
            type=data.get("type", "vdSD"),
            model=data.get("model", ""),
            model_version=data.get("model_version", ""),
            model_uid=data.get("model_uid", ""),
            hardware_version=data.get("hardware_version", ""),
            hardware_guid=data.get("hardware_guid", ""),
            hardware_model_guid=data.get("hardware_model_guid", ""),
            vendor_name=data.get("vendor_name", ""),
            vendor_guid=data.get("vendor_guid", ""),
            oem_guid=data.get("oem_guid", ""),
            oem_model_guid=data.get("oem_model_guid", ""),
            device_class=data.get("device_class", ""),
            device_class_version=data.get("device_class_version", ""),
            active=data.get("active", None),
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
