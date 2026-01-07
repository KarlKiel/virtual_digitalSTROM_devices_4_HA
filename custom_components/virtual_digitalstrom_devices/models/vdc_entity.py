"""vDC Entity representation following vDC-API-properties specification.

This module implements the complete vDC hierarchy:
- vDC (Integration level) - Chapter 2 (Common) + Chapter 3 (vDC-specific)
- vdSD (Device level) - Chapter 2 (Common) + Chapter 4 (vdSD-specific)
- Property elements at all levels following the specification

The key insight is that EVERYTHING in vDC is property elements:
- vDC.capabilities = list[vdSD property elements]
- vdSD.configurations = list[feature property elements]
- Each feature (inputs/outputs/scenes) = list[property elements]
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


# =============================================================================
# Chapter 2: Common Properties for All Addressable Entities
# =============================================================================

@dataclass
class CommonEntityProperties:
    """Common properties for all addressable entities (Chapter 2).
    
    These properties must be supported by all addressable entities:
    vdSD (virtual device), vDC, vDChost, vdSM
    """
    # Required properties
    ds_uid: str  # dSUID - 34 hex characters (2*17)
    display_id: str  # Human-readable identification
    type: str  # Entity type: "vdSD", "vDC", "vDChost", "vdSM"
    model: str  # Human-readable model string
    model_version: str  # Model version (firmware version)
    model_uid: str  # digitalSTROM system unique ID for functional model
    
    # Optional properties
    hardware_version: Optional[str] = None
    hardware_guid: Optional[str] = None
    hardware_model_guid: Optional[str] = None
    vendor_name: Optional[str] = None
    vendor_guid: Optional[str] = None
    oem_guid: Optional[str] = None
    oem_model_guid: Optional[str] = None
    config_url: Optional[str] = None
    device_icon_16: Optional[bytes] = None
    device_icon_name: Optional[str] = None
    name: Optional[str] = None
    device_class: Optional[str] = None
    device_class_version: Optional[str] = None
    active: Optional[bool] = None
    
    def to_property_elements(self) -> Dict[str, Any]:
        """Convert to vDC property elements format."""
        elements = {
            "dSUID": self.ds_uid,
            "displayId": self.display_id,
            "type": self.type,
            "model": self.model,
            "modelVersion": self.model_version,
            "modelUID": self.model_uid,
        }
        
        # Add optional properties if present
        if self.hardware_version:
            elements["hardwareVersion"] = self.hardware_version
        if self.hardware_guid:
            elements["hardwareGuid"] = self.hardware_guid
        if self.hardware_model_guid:
            elements["hardwareModelGuid"] = self.hardware_model_guid
        if self.vendor_name:
            elements["vendorName"] = self.vendor_name
        if self.vendor_guid:
            elements["vendorGuid"] = self.vendor_guid
        if self.oem_guid:
            elements["oemGuid"] = self.oem_guid
        if self.oem_model_guid:
            elements["oemModelGuid"] = self.oem_model_guid
        if self.config_url:
            elements["configURL"] = self.config_url
        if self.device_icon_name:
            elements["deviceIconName"] = self.device_icon_name
        if self.name:
            elements["name"] = self.name
        if self.device_class:
            elements["deviceClass"] = self.device_class
        if self.device_class_version:
            elements["deviceClassVersion"] = self.device_class_version
        if self.active is not None:
            elements["active"] = self.active
        
        return elements


# =============================================================================
# Chapter 3: vDC Properties
# =============================================================================

@dataclass
class VDCCapabilities:
    """vDC Capabilities (Chapter 3.2)."""
    metering: Optional[bool] = None
    identification: Optional[bool] = None
    dynamic_definitions: Optional[bool] = None
    
    def to_property_elements(self) -> Dict[str, Any]:
        """Convert to vDC property elements format."""
        elements = {}
        if self.metering is not None:
            elements["metering"] = self.metering
        if self.identification is not None:
            elements["identification"] = self.identification
        if self.dynamic_definitions is not None:
            elements["dynamicDefinitions"] = self.dynamic_definitions
        return elements


@dataclass
class VDCEntity:
    """Virtual Device Connector (vDC) entity.
    
    This represents the integration level in Home Assistant.
    It contains:
    - Common properties (Chapter 2)
    - vDC-specific properties (Chapter 3)
    - capabilities: list[vdSD property elements] - all managed devices
    """
    # Common properties for all entities (Chapter 2)
    common: CommonEntityProperties
    
    # vDC-specific properties (Chapter 3)
    capabilities: VDCCapabilities = field(default_factory=VDCCapabilities)
    zone_id: Optional[int] = None
    implementation_id: Optional[str] = None
    
    # The key property: list of vdSD property elements
    # Each element is a complete vdSD (virtual device) property tree
    vdsds: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_vdsd(self, vdsd_property_element: Dict[str, Any]) -> None:
        """Add a vdSD as a property element.
        
        Args:
            vdsd_property_element: Complete vdSD property tree
        """
        self.vdsds.append(vdsd_property_element)
    
    def to_property_tree(self) -> Dict[str, Any]:
        """Convert entire vDC to property tree for vDC API.
        
        Returns:
            Complete property tree with all levels
        """
        tree = {}
        
        # Add common properties (Chapter 2)
        tree.update(self.common.to_property_elements())
        
        # Add vDC-specific properties (Chapter 3)
        tree["capabilities"] = self.capabilities.to_property_elements()
        if self.zone_id is not None:
            tree["zoneID"] = self.zone_id
        if self.implementation_id:
            tree["implementationId"] = self.implementation_id
        
        # Add all vdSDs as property elements
        # This is the list[property elements] that Chapter 3 describes
        tree["x-p44-vdcs"] = {}  # Container for vdSD property elements
        for idx, vdsd in enumerate(self.vdsds):
            tree["x-p44-vdcs"][str(idx)] = vdsd
        
        return tree


# =============================================================================
# Helper Functions
# =============================================================================

def create_vdc_entity(
    ds_uid: str,
    name: str = "Virtual digitalSTROM Devices",
    model: str = "HA Virtual vDC",
    model_version: str = "1.0",
) -> VDCEntity:
    """Create a vDC entity for Home Assistant integration.
    
    Args:
        ds_uid: dSUID for the vDC
        name: Name of the vDC
        model: Model string
        model_version: Version string
        
    Returns:
        VDCEntity instance
    """
    common = CommonEntityProperties(
        ds_uid=ds_uid,
        display_id=name,
        type="vDC",
        model=model,
        model_version=model_version,
        model_uid=f"homeassistant.vdc.{model_version}",
        name=name,
        vendor_name="Home Assistant",
    )
    
    capabilities = VDCCapabilities(
        metering=False,
        identification=True,
        dynamic_definitions=True,
    )
    
    return VDCEntity(
        common=common,
        capabilities=capabilities,
        implementation_id="homeassistant-virtual-vdc",
    )
