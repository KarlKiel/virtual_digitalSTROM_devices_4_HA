"""vDC (Virtual Device Connector) Manager Module.

This module manages the vDC entity that represents the virtual device connector
as defined in the vDC-API-properties specification (July 2022), chapters 2 and 3.

The vDC entity is created during integration installation and persisted to YAML storage.

Chapter 2 Properties (Common properties for all addressable entities):
- Required: dsUID, displayId, type, model, modelVersion, modelUID
- Optional: hardwareVersion, hardwareGuid, hardwareModelGuid, vendorName, vendorGuid,
           oemGuid, oemModelGuid, deviceClass, deviceClassVersion, name

Chapter 3 Properties (vDC-level specific properties):
- implementationId: Implementation identifier
- configURL: Configuration web UI URL
- apiVersion: vDC API version

All properties are persisted to YAML storage and available for use by the integration.
"""

from __future__ import annotations

import logging
import random
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

# Handle both package imports (when used as Home Assistant integration)
# and standalone imports (for testing)
try:
    from ..models.dsuid_generator import generate_dsuid
except ImportError:
    from dsuid_generator import generate_dsuid

_LOGGER = logging.getLogger(__name__)


# vDC Property constants as specified in the problem statement
VDC_DISPLAY_ID = "KarlKiels generic vDC"
VDC_TYPE = "vDC"
VDC_MODEL = "vDC to control 3rd party devices in DS"
VDC_MODEL_VERSION = "1.0"
VDC_MODEL_UID = "SW-gvDC400"
VDC_VENDOR_NAME = "KarlKiel"
VDC_NAME = "KarlKiels generic vDC"


class VdcManager:
    """Manages the vDC (Virtual Device Connector) entity.
    
    The vDC entity represents the virtual device connector itself and contains
    properties as defined in the vDC-API-properties specification chapters 2 and 3.
    
    Managed Properties:
    -------------------
    Chapter 2 - Common Properties (Required):
        - dsUID: digitalSTROM Unique Identifier (34 hex chars)
        - displayId: Human-readable identification
        - type: Entity type ("vDC")
        - model: Model description
        - modelVersion: Firmware/software version
        - modelUID: Unique ID for functional model
        
    Chapter 2 - Common Properties (Optional):
        - hardwareVersion: Hardware version string
        - hardwareGuid: Hardware GUID in URN format
        - hardwareModelGuid: Hardware model GUID
        - vendorName: Vendor/manufacturer name
        - vendorGuid: Vendor GUID
        - oemGuid: OEM product GUID
        - oemModelGuid: OEM model GUID
        - deviceClass: Device class profile name
        - deviceClassVersion: Device class version
        - name: User-friendly device name
        
    Chapter 3 - vDC-Level Properties:
        - implementationId: Implementation identifier
        - configURL: Configuration web UI URL
        - apiVersion: vDC API version
        
    All properties are persisted to YAML storage and can be retrieved or updated
    using the provided methods.
    """
    
    def __init__(self, storage_path: Path) -> None:
        """Initialize the vDC manager.
        
        Args:
            storage_path: Path to the YAML storage file for vDC configuration
        """
        self.storage_path = storage_path
        self._vdc_config: dict[str, Any] = {}
        self._load()
    
    def _load(self) -> None:
        """Load vDC configuration from YAML file."""
        try:
            if self.storage_path.exists():
                _LOGGER.debug("Loading vDC configuration from %s", self.storage_path)
                with open(self.storage_path, "r", encoding="utf-8") as file:
                    self._vdc_config = yaml.safe_load(file) or {}
                _LOGGER.info("Loaded vDC configuration from storage")
            else:
                _LOGGER.debug("vDC configuration file does not exist, will create new")
                self._vdc_config = {}
        except (yaml.YAMLError, ValueError, KeyError) as e:
            _LOGGER.error("Error parsing vDC configuration from %s: %s", self.storage_path, e)
            self._vdc_config = {}
        except (FileNotFoundError, PermissionError, OSError) as e:
            _LOGGER.error("Error accessing vDC configuration file %s: %s", self.storage_path, e)
            self._vdc_config = {}
    
    def _save(self) -> None:
        """Save vDC configuration to YAML file."""
        try:
            # Ensure parent directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to YAML file
            with open(self.storage_path, "w", encoding="utf-8") as file:
                yaml.safe_dump(self._vdc_config, file, default_flow_style=False, sort_keys=False)
            
            _LOGGER.debug("Saved vDC configuration to %s", self.storage_path)
        except yaml.YAMLError as e:
            _LOGGER.error("Error serializing vDC configuration to YAML: %s", e)
        except (FileNotFoundError, PermissionError, OSError) as e:
            _LOGGER.error("Error writing to vDC configuration file %s: %s", self.storage_path, e)
    
    def _get_mac_address(self) -> str:
        """Get the MAC address of the Home Assistant server.
        
        Note: uuid.getnode() returns the hardware MAC address if available,
        but may return a random 48-bit number with the multicast bit set
        if no MAC address can be found. The fallback logic handles this case.
        
        Returns:
            MAC address as a formatted string (e.g., "12:34:56:78:90:AB")
        """
        try:
            # Get MAC address using uuid.getnode()
            # This returns the MAC address as an integer
            mac_int = uuid.getnode()
            
            # Convert to 12-character hex string (6 bytes)
            mac_hex = f"{mac_int:012X}"
            
            # Format as XX:XX:XX:XX:XX:XX
            mac_formatted = ":".join([mac_hex[i:i+2] for i in range(0, 12, 2)])
            
            _LOGGER.debug("Retrieved MAC address: %s", mac_formatted)
            return mac_formatted
        except Exception as e:
            _LOGGER.warning("Failed to get MAC address: %s, using fallback", e)
            # Fallback: generate a random MAC address
            mac_bytes = [random.randint(0x00, 0xFF) for _ in range(6)]
            # Set locally administered bit to avoid conflicts with real hardware
            mac_bytes[0] = (mac_bytes[0] & 0xFE) | 0x02
            mac_formatted = ":".join([f"{b:02X}" for b in mac_bytes])
            _LOGGER.debug("Generated fallback MAC address: %s", mac_formatted)
            return mac_formatted
    
    def create_or_update_vdc(self, dss_port: int) -> dict[str, Any]:
        """Create or update the vDC entity configuration.
        
        This creates a vDC entity with all properties from:
        - Chapter 2: Common properties for all addressable entities (required and optional)
        - Chapter 3: vDC-level specific properties
        
        Required Chapter 2 properties:
        - dsUID, displayId, type, model, modelVersion, modelUID
        
        Optional Chapter 2 properties (preserved if already set):
        - hardwareVersion, hardwareGuid, hardwareModelGuid
        - vendorName, vendorGuid
        - oemGuid, oemModelGuid
        - deviceClass, deviceClassVersion
        - name (also used for user-friendly identification)
        
        Args:
            dss_port: TCP port for digitalSTROM server connection
            
        Returns:
            The vDC configuration dictionary
        """
        # Preserve existing configuration to avoid losing optional properties
        existing_config = self._vdc_config.copy()
        
        # Check if vDC already exists and has a dsUID
        if existing_config.get("dsUID"):
            _LOGGER.info("vDC entity already exists, updating configuration")
            existing_dsuid = existing_config["dsUID"]
        else:
            # Generate new dsUID from MAC address
            mac_address = self._get_mac_address()
            existing_dsuid = generate_dsuid(mac_address=mac_address)
            _LOGGER.info("Generated new dsUID for vDC: %s (from MAC: %s)", existing_dsuid, mac_address)
        
        # Update vDC configuration with required and optional properties
        # Start with existing config to preserve optional properties
        self._vdc_config = existing_config
        
        # Set/update required Chapter 2 common properties (vDC spec Section 2)
        self._vdc_config["dsUID"] = existing_dsuid
        self._vdc_config["displayId"] = VDC_DISPLAY_ID
        self._vdc_config["type"] = VDC_TYPE
        self._vdc_config["model"] = VDC_MODEL
        self._vdc_config["modelVersion"] = VDC_MODEL_VERSION
        self._vdc_config["modelUID"] = VDC_MODEL_UID
        self._vdc_config["vendorName"] = VDC_VENDOR_NAME
        self._vdc_config["name"] = VDC_NAME
        
        # Optional Chapter 2 properties - only set if not already present
        # These can be set externally and should be preserved
        self._vdc_config.setdefault("hardwareVersion", "")
        self._vdc_config.setdefault("hardwareGuid", "")
        self._vdc_config.setdefault("hardwareModelGuid", "")
        self._vdc_config.setdefault("vendorGuid", "")
        self._vdc_config.setdefault("oemGuid", "")
        self._vdc_config.setdefault("oemModelGuid", "")
        self._vdc_config.setdefault("deviceClass", "")
        self._vdc_config.setdefault("deviceClassVersion", "")
        
        # Chapter 3: vDC-level specific properties (optional)
        self._vdc_config.setdefault("implementationId", "")  # Implementation identifier
        self._vdc_config.setdefault("configURL", "")  # Configuration web UI URL
        self._vdc_config.setdefault("apiVersion", "1.0")  # vDC API version
        
        # Integration-specific configuration
        self._vdc_config["dss_port"] = dss_port
        
        # Set timestamps (metadata)
        now = datetime.now().isoformat()
        if "created_at" not in self._vdc_config or not self._vdc_config.get("created_at"):
            self._vdc_config["created_at"] = now
        self._vdc_config["updated_at"] = now
        
        # Save to YAML
        self._save()
        
        _LOGGER.info(
            "vDC entity configured: name='%s', type='%s', model='%s', dsUID='%s', port=%d",
            VDC_NAME,
            VDC_TYPE,
            VDC_MODEL,
            existing_dsuid,
            dss_port
        )
        
        return self._vdc_config
    
    def get_vdc_config(self) -> dict[str, Any]:
        """Get the current vDC configuration.
        
        Returns:
            The vDC configuration dictionary
        """
        return self._vdc_config.copy()
    
    def has_vdc(self) -> bool:
        """Check if vDC entity has been created.
        
        Returns:
            True if vDC entity exists, False otherwise
        """
        return bool(self._vdc_config.get("dsUID"))
    
    def get_dss_port(self) -> int | None:
        """Get the configured DSS port.
        
        Returns:
            The DSS port number or None if not configured
        """
        return self._vdc_config.get("dss_port")
    
    def get_dsuid(self) -> str | None:
        """Get the vDC dsUID.
        
        Returns:
            The dsUID string or None if not configured
        """
        return self._vdc_config.get("dsUID")
    
    def update_vdc_property(self, property_name: str, value: Any) -> bool:
        """Update a specific vDC property and save to storage.
        
        This allows updating optional Chapter 2 and Chapter 3 properties
        without recreating the entire configuration.
        
        Args:
            property_name: Name of the property to update
            value: New value for the property
            
        Returns:
            True if property was updated and saved successfully, False otherwise
        """
        # List of updatable properties (optional Chapter 2 and Chapter 3 properties)
        updatable_properties = [
            "hardwareVersion", "hardwareGuid", "hardwareModelGuid",
            "vendorGuid", "oemGuid", "oemModelGuid",
            "deviceClass", "deviceClassVersion",
            "implementationId", "configURL", "apiVersion"
        ]
        
        if property_name not in updatable_properties:
            _LOGGER.warning(
                "Property '%s' is not updatable. Only optional properties can be updated.",
                property_name
            )
            return False
        
        try:
            self._vdc_config[property_name] = value
            self._vdc_config["updated_at"] = datetime.now().isoformat()
            self._save()
            _LOGGER.info("Updated vDC property '%s' to '%s'", property_name, value)
            return True
        except Exception as e:
            _LOGGER.error("Failed to update vDC property '%s': %s", property_name, e)
            return False
    
    def get_all_properties(self) -> dict[str, Any]:
        """Get all vDC properties including Chapter 2 and Chapter 3 properties.
        
        Returns:
            Dictionary containing all vDC properties
        """
        return self.get_vdc_config()
