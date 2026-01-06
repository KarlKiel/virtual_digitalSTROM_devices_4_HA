"""vDC (Virtual Device Connector) Manager Module.

This module manages the vDC entity that represents the virtual device connector
as defined in the vDC-API-properties specification (July 2022), chapters 2 and 3.

The vDC entity is created during integration installation and persisted to YAML storage.
"""

from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import Any

import yaml

# Handle both package imports (when used as Home Assistant integration)
# and standalone imports (for testing)
try:
    from .dsuid_generator import generate_dsuid
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
            import random
            mac_bytes = [random.randint(0x00, 0xFF) for _ in range(6)]
            # Set locally administered bit to avoid conflicts with real hardware
            mac_bytes[0] = (mac_bytes[0] & 0xFE) | 0x02
            mac_formatted = ":".join([f"{b:02X}" for b in mac_bytes])
            _LOGGER.debug("Generated fallback MAC address: %s", mac_formatted)
            return mac_formatted
    
    def create_or_update_vdc(self, dss_port: int) -> dict[str, Any]:
        """Create or update the vDC entity configuration.
        
        This creates a vDC entity with the properties specified in the problem statement:
        - displayId: "KarlKiels generic vDC"
        - type: "vDC"
        - model: "vDC to control 3rd party devices in DS"
        - modelVersion: "1.0"
        - modelUID: "SW-gvDC400"
        - vendorName: "KarlKiel"
        - name: "KarlKiels generic vDC"
        - dsUID: Generated from MAC address using the dsuid_generator
        
        Args:
            dss_port: TCP port for digitalSTROM server connection
            
        Returns:
            The vDC configuration dictionary
        """
        # Check if vDC already exists and has a dsUID
        if self._vdc_config.get("dsUID"):
            _LOGGER.info("vDC entity already exists, updating configuration")
            existing_dsuid = self._vdc_config["dsUID"]
        else:
            # Generate new dsUID from MAC address
            mac_address = self._get_mac_address()
            existing_dsuid = generate_dsuid(mac_address=mac_address)
            _LOGGER.info("Generated new dsUID for vDC: %s (from MAC: %s)", existing_dsuid, mac_address)
        
        # Create/update vDC configuration with specified properties
        self._vdc_config = {
            # Common properties for vDC entity (per vDC spec Section 2)
            "dsUID": existing_dsuid,
            "displayId": VDC_DISPLAY_ID,
            "type": VDC_TYPE,
            "model": VDC_MODEL,
            "modelVersion": VDC_MODEL_VERSION,
            "modelUID": VDC_MODEL_UID,
            "vendorName": VDC_VENDOR_NAME,
            "name": VDC_NAME,
            # Additional configuration
            "dss_port": dss_port,
            "created_at": self._vdc_config.get("created_at", None),
            "updated_at": None,  # Will be set to current timestamp when saved
        }
        
        # Set timestamps
        from datetime import datetime
        now = datetime.now().isoformat()
        if not self._vdc_config.get("created_at"):
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
